"""SPOrE layout algorithms - overlap removal and compaction."""
import math
from ..options import get_padding, get_spacing


def _compute_min_distance(placed_node, new_node, dx, dy, spacing):
    """Compute the minimum scalar t along direction (dx, dy) such that placing
    new_node at (origin_x + t*dx, origin_y + t*dy) doesn't overlap with placed_node
    (including spacing).

    Returns the minimum t > 0, or 0 if no constraint applies.
    """
    pw = placed_node.get('width', 0)
    ph = placed_node.get('height', 0)
    nw = new_node.get('width', 0)
    nh = new_node.get('height', 0)
    px = placed_node.get('x', 0)
    py = placed_node.get('y', 0)

    # We want the minimum t such that the rectangles don't overlap.
    # Rectangles overlap iff they overlap in BOTH x and y.
    # No overlap = separated in at least one axis.
    # We need to find min t where at least one axis is separated.

    # For each axis, compute the range of t where they DO overlap in that axis.
    # They overlap in x when:
    #   new_x < px + pw + spacing AND new_x + nw + spacing > px
    # where new_x is a function of t through the ray direction.

    candidates = []

    # The new_node's position relative to origin (first placed node's position)
    # is (t * dx, t * dy). But we place from the first node's position.
    # Actually, for multi-node, we need absolute coordinates.
    # Let's compute t such that (ox + t*dx, oy + t*dy) doesn't overlap with placed.
    # But origin is the center area. Let me simplify:

    # For separation in x (new_x >= px + pw + spacing):
    if dx > 1e-10:
        t_x = (px + pw + spacing) / dx
        candidates.append(t_x)
    elif dx < -1e-10:
        # new_x + nw + spacing <= px  →  t*dx <= px - nw - spacing
        t_x = (px - nw - spacing) / dx  # dx is negative, so this flips
        candidates.append(t_x)

    # For separation in y (new_y >= py + ph + spacing):
    if dy > 1e-10:
        t_y = (py + ph + spacing) / dy
        candidates.append(t_y)
    elif dy < -1e-10:
        t_y = (py - nh - spacing) / dy
        candidates.append(t_y)

    if not candidates:
        return 0.0

    # We need at least one axis to be separated. So the minimum t
    # that achieves ANY axis separation is sufficient.
    return min(t for t in candidates if t > 0) if any(t > 0 for t in candidates) else 0.0


def _spore_layout(graph, global_options, is_compaction):
    """Common SPOrE layout logic for both compaction and overlap removal."""
    children = graph.get('children', [])
    if not children:
        return

    padding = get_padding(graph, global_options)
    node_spacing = get_spacing(graph, 'elk.spacing.nodeNode', global_options, 20.0)

    for child in children:
        child.setdefault('x', 0.0)
        child.setdefault('y', 0.0)
        child.setdefault('width', 0.0)
        child.setdefault('height', 0.0)

    if len(children) == 1:
        children[0]['x'] = padding['left']
        children[0]['y'] = padding['top']
        _compute_size(graph, padding)
        return

    # Compute center of gravity
    n = len(children)
    cx = sum(c['x'] + c['width'] / 2 for c in children) / n
    cy = sum(c['y'] + c['height'] / 2 for c in children) / n

    # For each node, compute direction and distance from center
    node_info = []
    for child in children:
        ncx = child['x'] + child['width'] / 2
        ncy = child['y'] + child['height'] / 2
        dx = ncx - cx
        dy = ncy - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1e-10:
            dx, dy = 1.0, 0.0
            dist = 1.0
        else:
            dx /= dist
            dy /= dist
        node_info.append((child, dx, dy, dist))

    # Sort by distance from center (closest first)
    node_info.sort(key=lambda x: x[3])

    # Place first node at origin (0, 0), will normalize later
    placed = []
    for child, dx, dy, orig_dist in node_info:
        if not placed:
            child['x'] = 0.0
            child['y'] = 0.0
            placed.append(child)
        else:
            # Find minimum t along direction (dx, dy) from origin
            # such that the node doesn't overlap with any placed node
            max_t = 0.0
            for p in placed:
                t = _compute_min_distance(p, child, dx, dy, node_spacing)
                max_t = max(max_t, t)

            child['x'] = max_t * dx
            child['y'] = max_t * dy
            placed.append(child)

    # Normalize positions so minimum is at padding
    min_x = min(c['x'] for c in children)
    min_y = min(c['y'] for c in children)
    for child in children:
        child['x'] = round(child['x'] - min_x + padding['left'], 10)
        child['y'] = round(child['y'] - min_y + padding['top'], 10)

    _compute_size(graph, padding)


def _compute_size(graph, padding):
    max_x = 0.0
    max_y = 0.0
    for child in graph.get('children', []):
        cx = child.get('x', 0.0) + child.get('width', 0.0)
        cy = child.get('y', 0.0) + child.get('height', 0.0)
        max_x = max(max_x, cx)
        max_y = max(max_y, cy)
    graph['width'] = max_x + padding['right']
    graph['height'] = max_y + padding['bottom']


class SporeCompactionProvider:
    """Compacts a graph by moving nodes toward the center of gravity
    while maintaining relative positions, with minimum spacing."""

    def layout(self, graph: dict, global_options: dict = None) -> None:
        _spore_layout(graph, global_options, is_compaction=True)


class SporeOverlapProvider:
    """Removes overlaps between nodes while preserving relative positions."""

    def layout(self, graph: dict, global_options: dict = None) -> None:
        _spore_layout(graph, global_options, is_compaction=False)
