# Brandes–Köpnig Horizontal Coordinate Assignment in pyelk

`pyelk.algorithms.layered.brandes_kozen` implements the **BRANDES_KOZEN**
node-placement strategy of the ELK layered algorithm — the horizontal
coordinate assignment phase (phase 5) of Sugiyama's framework.

> **Why it exists.** After layer assignment (phase 2) and crossing
> minimisation (phase 4) fix the *order* of nodes within each layer,
> something must decide the actual *coordinates*. The trivial approach —
> centring every layer independently of its width — misaligns edge chains
> whenever neighbouring layers have different totals, producing staircase
> routes. Brandes–Köpnig instead aligns the endpoints of edge chains to a
> shared centre so as many edges as possible run **straight**, then packs
> the aligned blocks without overlap.

## References

Original algorithm:

- Ulrik Brandes and Boris Köpnig, *Fast and Simple Horizontal Coordinate
  Assignment*, Proceedings of the 9th International Symposium on Graph
  Drawing (GD 2001), LNCS vol. 2265, pp. 31–44, Springer, 2002.
  DOI: <https://doi.org/10.1007/3-540-45848-4_3>

Archived corrections (arXiv) — the original paper contains two flaws in
its compaction pseudocode; both are documented and corrected here:

- Ulrik Brandes, Julian Walter, and Johannes Zink, *Erratum: Fast and
  Simple Horizontal Coordinate Assignment*, 2020.
  arXiv: <https://arxiv.org/abs/2008.01252>

Ports-and-varying-sizes extension (the background for treating node
sizes and fixed ports explicitly, as pyelk does):

- *Size- and Port-Aware Horizontal Node Coordinate Assignment*, GD 2015,
  <https://link.springer.com/chapter/10.1007/978-3-319-27261-0_12>
  (see also ELK's own `nodePlacement` documentation at
  <https://eclipse.dev/elk/reference/options/org-eclipse-elk-layered-nodeplacement-strategy.html>)

## The method

The algorithm runs **four times**, once for each combination of

- *vertical alignment direction*: align a node with its neighbours in the
  layer **above** (`up`) or **below** (`down`) it; and
- *horizontal traversal order*: visit nodes within each layer
  **left-to-right** (`left`) or **right-to-left** (`right`).

Each pass produces candidate x-coordinates; the pass whose layout is
narrowest wins (ties prefer more aligned segments). The four passes are
symmetric — describe the top-to-bottom, left-to-right case.

### Step 1 — vertical alignment (build alignment chains)

For every node `v` whose adjacent-layer neighbours `A(v)` are known:

- Compute the **median position**: the position (index within the
  adjacent layer) of the median neighbour. For an odd count `|A(v)|` the
  single middle neighbour is the candidate; for an even count there are
  two candidates `r` and `l` (the neighbours just left and right of the
  median). The traversal order decides which is tried first.
- `v` may join the **block** (alignment chain) of neighbour `w` only if
  neither is already part of a block (`align[root[w]] == root[w]`, and
  `v` unaligned), **and** the alignment does not cross an existing
  chain: writing `place(w)` for w's position, every already-aligned
  neighbour of a node left of `v` must satisfy `align[root[·]] < place`,
  and every such neighbour of a node right of `v` must satisfy
  `align[root[·]] > place`.
- On a crossing, **priority** decides: the candidate wins over the
  incumbent block when `|A(v)| > |A(root of the incumbent)|`; otherwise
  the conflict is left to the next pass.

Successful alignments are stored as edges of an alignment graph; the
connected components of that graph (each node holds at most one aligned
neighbour per side, so every component is a simple path) are the
**blocks**. Every maximal chain `v₁ … vₖ` spread over consecutive layers
will later share one x-centre — which is what straightens the edges of
the chain.

### Step 2 — horizontal compaction

Walk the blocks in the traversal order (anchored at their topmost node's
layer, then leftmost position). For each block:

1. **Desired centre** — the median of the already-placed neighbour
   centres of its members (neighbours that belong to blocks packed
   earlier and other edges). A block with no placed neighbours keeps
   contact with the previous block via the layer cursor.
2. **Feasible centre** — per-layer position cursors guarantee no
   overlap: `cursor[layer] + node_spacing + half_width` for every member
   of the block. The block centre is `max(desired, feasible)`.
3. Write the shared centre to every member and advance each touched
   layer's cursor past the member's right edge.

Because one block spans several layers, edges *inside* the block are
exactly vertical; the long edge of Sugiyama's dummy-node chain that is
aligned with its source and sink becomes a single straight segment.

### Step 3 — balancing

The four scans' results are compared by total layout width, tie-broken
by the number of unaligned nodes that had neighbours (a proxy for stray
bends). The winner is applied. ELK's `BALANCING` option also allows an
average of the four layouts; pyelk keeps the simpler pick-a-winner form.

## Where pyelk's implementation differs from the paper

The published pseudocode assumes unit-size vertices and no explicit
ports; real diagrams have neither. pyelk therefore:

- packs with **per-layer cursors and half-width margins** rather than the
  paper's unit-delta compaction — this is precisely the space where the
  original publication's two mistakes live (see the arXiv erratum:
  the miscomputed type-2/type-3 conflict handling and the
  `place_block` recursion's missing `sink` update). Our cursor formulation
  is immune to both;
- treats **dummy nodes as first-class chain members** (Sugiyama long-edge
  dummies participate in alignment, so a straightened chain straightens
  the whole long edge);
- routes edges **orthogonally** afterwards (`_route_edges` with
  `elk.edgeRouting: ORTHOGONAL`): aligned chains need no bends, all
  other edge segments cross the inter-layer band on per-band channel
  lanes, and port-anchored heads are preserved through `_write_back`;
- keeps everything deterministic (sorted candidate orders; ties broken
  by scan index) so repeated layouts are byte-identical.

Complexity: linear in the number of vertices, dummies and segments —
O(N) per scan, O(4N) overall, matching the paper.

## Using it

```python
from pyelk import ELK

result = ELK().layout(graph, layout_options={
    'algorithm': 'layered',
    'elk.layered.nodePlacement.strategy': 'BRANDES_KOZEN',  # alias: 'BRANDES'
})
```

The strategy lives in `to_elk_json`'s default option set for
(diagramboxes) `routing='elk'` and `routing='pyelk'`; any other value
falls back to the centred-stacking placement. Note `NETWORK_SIMPLEX`
upstream is only a **layering** strategy — node placement ignores it.