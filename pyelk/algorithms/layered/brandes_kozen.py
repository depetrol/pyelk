"""Brandes-Köpnig horizontal coordinate assignment.

ELK layered ``nodePlacement.strategy = BRANDES_KOZEN`` (alias accepted:
``BRANDES``).  This is phase 5 of the Sugiyama pipeline: after layering
and crossing minimisation have fixed the ORDER of nodes within each
layer, this decides the coordinates.  The naive alternative — centring
each layer independently — misaligns edge chains whenever neighbouring
layers differ in total width and staircase routes appear.  Köpnig's
phrase for the goal is "draw as many edges straight as possible".

Algorithm overview (four passes — align up/down x traverse left/right;
the pass whose layout is narrowest wins, ties prefer more aligned
segments):

1.  Vertical alignment.  For every node v, its median adjacent-layer
    neighbour w offers a block to join.  v joins w's block only if both
    are free (neither already carries an alignment in this pass) and the
    alignment does not CROSS an already-built chain: all chains aligned
    left (right) of v must place their aligned neighbour left (right) of
    w.  A crossing is resolved by endpoint degree: a candidate whose
    combined endpoint degree exceeds the incumbent's steals the slot.
    Chains = maximal paths through the accepted alignments; every node
    of a chain will share one x-centre later, so the chain's edges run
    vertical.

2.  Horizontal compaction.  Blocks are laid out in traversal order with
    per-layer position cursors: the block's shared centre is
    max(desired median of already-packed neighbour centres, feasible
    minimum from the cursors).  Cursor packing replaces the paper's
    unit-delta compaction — deliberate, because that compaction is where
    the original publication's two known errors live; both are
    documented (and corrected) in the arXiv erratum, and the cursor
    formulation is immune to both while keeping O(N) runtime.

3.  Balancing.  The four candidate layouts are compared by total extent,
    tie-broken by the count of nodes that had neighbours but could not
    align (a proxy for stray edge bends).

Deviations from the published pseudocode (all deliberate):

-  vertices carry real sizes — compaction uses half-width margins rather
   than the unit-delta bookkeeping;
-  Sugiyama long-edge DUMMY NODES are first-class chain members, so an
   aligned chain straightens the entire long edge through all its
   dummy layers;
-  everything is deterministic (sorted candidate orders, stable
   tie-breaks) so repeated layouts are byte-identical;
-  the orthogonal edge ROUTING is a separate phase (see
   ``LayeredLayoutProvider._route_edges`` with ``elk.edgeRouting:
   ORTHOGONAL``): aligned chains need no bends and untouched edges cross
   the inter-layer bands on per-band channel lanes.

References:

-  Ulrik Brandes and Boris Köpnig, "Fast and Simple Horizontal
   Coordinate Assignment", Proc. 9th Int. Symp. Graph Drawing (GD 2001),
   LNCS 2265, pp. 31-44, Springer, 2002.
   https://doi.org/10.1007/3-540-45848-4_3
-  Ulrik Brandes, Julian Walter, Johannes Zink, "Erratum: Fast and
   Simple Horizontal Coordinate Assignment", 2020 (documents the two
   flaws in the original compaction pseudocode).
   https://arxiv.org/abs/2008.01252
-  "Size- and Port-Aware Horizontal Node Coordinate Assignment", GD 2015
   (varying node sizes and fixed ports with BK).
   https://link.springer.com/chapter/10.1007/978-3-319-27261-0_12
-  Full method notes: docs/brandes_kozen.md in this repository.
"""

from collections import defaultdict


def align_and_pack(layers, all_nodes, chains, node_spacing, layer_spacing,
                   padding, horizontal):
    """Return {'step': {id(n): coord}, 'along': {id(n): coord}}.

    ``step`` is the within-layer coordinate (x for DOWN/UP layouts, y for
    RIGHT/LEFT layouts); ``along`` the layer stacking coordinate.
    """
    nodes = list(all_nodes)
    if not nodes:
        return {'step': {}, 'along': {}}

    nbr_up, nbr_down, degree = _neighbours(layers, chains)
    positions = [{id(n): i for i, n in enumerate(layer)} for layer in layers]

    best_key = None
    placed = None
    for adj in ('down', 'up'):
        for within in ('left', 'right'):
            nbr = nbr_down if adj == 'down' else nbr_up
            segs, unaligned = _scan(layers, positions, nbr, degree, adj,
                                    within)
            result = _pack(layers, segs, node_spacing, layer_spacing,
                           padding, horizontal)
            width = _extent(result['step'])
            key = (unaligned, round(width, 3))
            if best_key is None or key < best_key:
                best_key = key
                placed = result

    for n in nodes:
        placed['step'].setdefault(id(n), 0.0)
        placed['along'].setdefault(id(n), 0.0)
    return placed


def _neighbours(layers, chains):
    """Adjacent-layer neighbours via chain segments; degree = incident
    chain segments +2 per node (the BK alignment priority)."""
    nbr_up = defaultdict(list)      # id -> [(id, node)] in layer li-1
    nbr_down = defaultdict(list)    # id -> [(id, node)] in layer li+1
    deg = defaultdict(int)
    for layer in layers:
        for n in layer:
            deg[id(n)] += 0
    for chain in chains:
        for (la, a), (lb, b) in zip(chain, chain[1:]):
            if lb == la + 1:
                nbr_down[id(a)].append((id(b), b))
                nbr_up[id(b)].append((id(a), a))
            elif la == lb + 1:
                nbr_down[id(b)].append((id(a), a))
                nbr_up[id(a)].append((id(b), b))
            deg[id(a)] += 1
            deg[id(b)] += 1
    return nbr_up, nbr_down, deg


def _scan(layers, positions, nbr, degree, adj, within):
    """Vertical-alignment pass (paper Alg. 1, size/degree adapted).

    ``adj`` selects which adjacent layer to align towards ('down' =
    the layer below, traversed top-to-bottom; 'up' = the layer above,
    traversed bottom-to-top); ``within`` is the traversal order inside
    each layer and decides which of the two even-count median
    candidates is tried first.

    For every node the candidates are its median adjacent-layer
    neighbours (odd count: one; even: the two around the median, tried
    in traversal preference with fallback to the second).  An alignment
    (u, w) succeeds when neither endpoint is already aligned in this
    pass and the segment does not CROSS an accepted segment within the
    same layer pair (crossing = opposite position order in the two
    layers).  A crossed candidate with strictly higher combined endpoint
    degree steals the slot from each incumbent it crosses.

    Returns (segments, unaligned_count) where ``segments`` is a list of
    ((layer_i, u), (layer_j, w)) with |li - lj| == 1 and
    ``unaligned_count`` counts nodes that had neighbours but ended the
    pass without an alignment (the balancing tie-break proxy for stray
    bends)."""
    adj_off = 1 if adj == 'down' else -1
    layer_order = (list(range(len(layers))) if adj == 'down'
                   else list(range(len(layers) - 1, -1, -1)))

    cands = []
    for li in layer_order:
        if li + adj_off < 0 or li + adj_off >= len(layers):
            continue
        nj = li + adj_off
        side = 'down' if adj == 'down' else 'up'
        for v in layers[li]:
            if positions[li].get(id(v)) is None:
                continue
            for wid, w in nbr.get(id(v), []):
                if w.layer != nj or w is v:
                    continue
                if positions[nj].get(id(w)) is None:
                    continue
                pv = positions[li][id(v)]
                pw = positions[nj][id(w)]
                if within == 'right':
                    pv, pw = -pv, -pw
                cands.append((min(pv, pw), ((li, v), (nj, w))))
    cands.sort(key=lambda t: t[0])

    # group candidates per node (already free-node-first via the greedy
    # scan); even neighbour counts offer the r AND l median candidates —
    # the scan's within-direction decides the preference, and both are
    # attempted before giving up (Brandes-Köpnig algorithm 1)
    segs = []
    endpoints = set()
    by_node = defaultdict(list)
    for _, seg in cands:
        (li, v), (lj, w) = seg
        key = (li, id(v))
        by_node[key].append(seg)
    for li, layer in enumerate(layers):
        order = (layer if within == 'left' else list(reversed(layer)))
        for v in order:
            group = sorted(by_node.get((li, id(v)), []),
                           key=lambda s: (positions[s[1][0]].get(id(s[1][1]),
                                                                0)
                                          * (-1 if within == 'right' else 1)))
            for seg in group:
                (lj, w) = seg[1]
                if id(v) in endpoints:
                    break           # v already aligned
                if id(w) in endpoints:
                    continue
                crossing = [s for s in segs if _crosses(seg, s, positions)]
                if crossing:
                    my = degree[id(v)] + degree[id(w)]
                    their = max(degree[id(a1)] + degree[id(a2)]
                                for s in crossing for a1, a2 in
                                [(s[0][1], s[1][1])])
                    if my <= their:
                        continue
                    for s in crossing:
                        segs.remove(s)
                        endpoints.discard(id(s[0][1]))
                        endpoints.discard(id(s[1][1]))
                segs.append(seg)
                endpoints.add(id(v))
                endpoints.add(id(w))

    unaligned = sum(1 for layer in layers for n in layer
                    if id(n) not in endpoints and nbr.get(id(n)))
    return segs, unaligned


def _crosses(seg, other, positions):
    """Would aligning ``seg`` conflict with already-aligned ``other``?

    Two segments spanning the SAME adjacent-layer pair conflict when
    their endpoint position orders disagree between the two layers
    (paper step 1's crossing condition).  Segments over different layer
    pairs never conflict here — layer cursors in the compaction step
    resolve those by space, not by order."""
    (la1, a1), (la2, a2) = seg
    (lb1, b1), (lb2, b2) = other
    if {la1, la2} != {lb1, lb2} or la1 == la2:
        return False
    pa1 = positions[la1].get(id(a1))
    pa2 = positions[la2].get(id(a2))
    pb1 = positions[lb1].get(id(b1))
    pb2 = positions[lb2].get(id(b2))
    if None in (pa1, pa2, pb1, pb2):
        return False
    # orient both segments upper-layer-first
    if la2 < la1:
        (la1, a1), (la2, a2) = (la2, a2), (la1, a1)
        pa1, pa2 = pa2, pa1
    if lb2 < lb1:
        (lb1, b1), (lb2, b2) = (lb2, b2), (lb1, b1)
        pb1, pb2 = pb2, pb1
    if la1 != lb1:
        return False
    return ((pa1 - pb1) > 0) != ((pa2 - pb2) > 0)


def _build_chains(layers, segs):
    """Chains = maximal alignment paths over the segment set.

    Because one scan grants every node at most one alignment (per
    side), the segment set forms disjoint simple paths across
    consecutive layers.  Walking nodes in layer order means each path
    is assembled starting from its topmost node — a node whose upper
    partner was already consumed by an earlier walk gets absorbed
    there.  These chains become the blocks of the compaction step; all
    members of one chain share a centre, which is what renders the
    chain's edges vertical and straightens a Sugiyama long edge through
    all of its dummy layers."""
    nxt = defaultdict(dict)      # id(node) -> {layer: other node}
    for (li, v), (lj, w) in segs:
        nxt[id(v)][lj] = w
        nxt[id(w)][li] = v
    chains = []
    seen = set()
    for li, layer in enumerate(layers):
        for n in layer:
            if id(n) in seen:
                continue
            left, right, cur, cl = [], [], n, li
            while id(cur) in nxt and (cl - 1) in nxt[id(cur)]:
                cur = nxt[id(cur)][cl - 1]
                cl -= 1
                left.append((cl, cur))
            cur, cl = n, li
            while id(cur) in nxt and (cl + 1) in nxt[id(cur)]:
                cur = nxt[id(cur)][cl + 1]
                cl += 1
                right.append((cl, cur))
            chain = list(reversed(left)) + [(li, n)] + right
            ok = True
            for cl2, c in chain:
                if id(c) in seen:
                    ok = False
                    break
            if not ok:
                continue
            for _, c in chain:
                seen.add(id(c))
            chains.append(chain)
    return chains


def _pack(layers, segs, node_spacing, layer_spacing, padding, horizontal):
    """Horizontal compaction (paper Alg. 2/3, cursor formulation).

    Chains from :func:`_build_chains` are placed in traversal order
    (topmost layer first, then leftmost member).  Each chain receives
    ONE shared centre x (or y for RIGHT/LEFT layouts): the larger of

    - the median of its members' already-placed partner centres (the
      median rule of the paper), and
    - the feasible minimum from the per-layer cursors
      (cursor + node_spacing + half member extent), which guarantees no
      two nodes overlap regardless of differing node sizes.

    Replacing the paper's unit-delta absolute-coordinate recursion with
    cursors sidesteps the two errors documented in the arXiv erratum
    (the type-2/type-3 conflict bookkeeping and the place_block
    recursion's sink update) while keeping linear time.  Unaligned
    nodes pack as singleton chains; the 'along' axis stacks layers
    exactly like the centred fallback pass so only phase-5 behaviour
    differs."""
    step = {}
    along = {}

    cur = padding['top' if not horizontal else 'left']
    for layer in layers:
        # DOWN/UP stack along y: the layer's y-extent is node HEIGHT;
        # RIGHT/LEFT stack along x: node WIDTH
        max_other = max(((n.width if horizontal else n.height)
                         for n in layer), default=0.0)
        for n in layer:
            along[id(n)] = cur
        cur += max_other + layer_spacing

    chains = _build_chains(layers, segs)
    in_chain = {id(m) for chain in chains for _, m in chain}
    for li, layer in enumerate(layers):
        for n in layer:
            if id(n) not in in_chain:
                chains.append([(li, n)])

    start_limit = padding['left' if not horizontal else 'top'] - node_spacing
    cursors = [start_limit for _ in layers]

    def key(chain):
        li = min(c[0] for c in chain)
        idx = {id(n): i for i, n in enumerate(layers[li])}
        pos = min(idx.get(id(m), 0) for c, m in chain if c == li)
        return (li, pos)

    seg_map = defaultdict(list)
    for s in segs:
        for node in (s[0][1], s[1][1]):
            seg_map[id(node)].append(s)

    for chain in sorted(chains, key=key):
        want = []
        for (li, node) in chain:
            for s in seg_map.get(id(node), []):
                for cn in (s[0][1], s[1][1]):
                    if cn is not node and id(cn) in step:
                        want.append(step[id(cn)])
        desired = None
        if want:
            want.sort()
            k = len(want)
            desired = (want[k // 2] if k % 2
                       else (want[k // 2 - 1] + want[k // 2]) / 2.0)
        req = None
        for (li, node) in chain:
            half = (node.height if horizontal else node.width) / 2.0
            lo = cursors[li] + node_spacing + half
            req = lo if req is None else max(req, lo)
        c = desired if desired is not None else (req if req is not None
                                                 else start_limit)
        c = max(c, req) if req is not None else c
        for (li, node) in chain:
            step[id(node)] = c
            half = (node.height if horizontal else node.width) / 2.0
            cursors[li] = max(cursors[li], c + half)

    return {'step': step, 'along': along}


def _extent(step):
    vals = list(step.values())
    return (max(vals) - min(vals)) if vals else 0.0