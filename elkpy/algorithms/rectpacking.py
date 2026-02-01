"""Rectangle packing layout algorithm."""
from ..options import get_padding, get_spacing


class RectPackingProvider:
    """Packs rectangles (nodes) into a compact arrangement."""

    def layout(self, graph: dict, global_options: dict = None) -> None:
        children = graph.get('children', [])
        if not children:
            return

        padding = get_padding(graph, global_options)
        node_spacing = get_spacing(graph, 'elk.spacing.nodeNode', global_options, 15.0)

        for child in children:
            child.setdefault('width', 0.0)
            child.setdefault('height', 0.0)

        # Sort children by height (descending) for better packing
        sorted_children = sorted(children, key=lambda c: c.get('height', 0), reverse=True)

        # Target aspect ratio of 1.0 (square-ish)
        total_area = sum((c.get('width', 0) + node_spacing) *
                         (c.get('height', 0) + node_spacing) for c in children)
        target_width = max(total_area ** 0.5,
                           max(c.get('width', 0) for c in children) + 2 * node_spacing)

        # Simple shelf-based packing
        current_x = padding['left']
        current_y = padding['top']
        shelf_height = 0.0
        row_start_y = padding['top']

        placement = {}
        for child in sorted_children:
            w = child.get('width', 0)
            h = child.get('height', 0)

            if current_x + w > target_width and current_x > padding['left']:
                # Start new row
                current_x = padding['left']
                row_start_y += shelf_height + node_spacing
                shelf_height = 0.0

            placement[id(child)] = (current_x, row_start_y)
            shelf_height = max(shelf_height, h)
            current_x += w + node_spacing

        # Apply placement
        for child in children:
            if id(child) in placement:
                child['x'] = placement[id(child)][0]
                child['y'] = placement[id(child)][1]
            else:
                child['x'] = padding['left']
                child['y'] = padding['top']

        # Compute graph size
        max_x = 0.0
        max_y = 0.0
        for child in children:
            cx = child.get('x', 0.0) + child.get('width', 0.0)
            cy = child.get('y', 0.0) + child.get('height', 0.0)
            max_x = max(max_x, cx)
            max_y = max(max_y, cy)

        graph['width'] = max_x + padding['right']
        graph['height'] = max_y + padding['bottom']
