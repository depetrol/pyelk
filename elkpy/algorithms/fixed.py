"""Fixed layout algorithm - positions nodes according to their specified positions."""
from ..options import get_option, get_padding, parse_kvector, parse_kvector_chain


class FixedLayoutProvider:
    """Places nodes at their specified positions (from 'position' option or x/y)."""

    def layout(self, graph: dict, global_options: dict = {}) -> None:
        padding = get_padding(graph, global_options)

        for child in graph.get('children', []):
            # Check for position option
            pos_str = get_option(child, 'position')
            if pos_str and isinstance(pos_str, str):
                pos = parse_kvector(pos_str)
                child['x'] = pos['x']
                child['y'] = pos['y']
            else:
                child.setdefault('x', padding['left'])
                child.setdefault('y', padding['top'])
            child.setdefault('width', 0.0)
            child.setdefault('height', 0.0)

        # Handle edges with bendPoints option
        for edge in graph.get('edges', []):
            bp_str = get_option(edge, 'bendPoints')
            if bp_str and isinstance(bp_str, str):
                points = parse_kvector_chain(bp_str)
                if len(points) >= 2:
                    section = {
                        'id': edge.get('id', '') + '_s0',
                        'startPoint': points[0],
                        'endPoint': points[-1],
                    }
                    if len(points) > 2:
                        section['bendPoints'] = points[1:-1]
                    edge['sections'] = [section]

        # Compute graph size
        max_x = 0.0
        max_y = 0.0
        for child in graph.get('children', []):
            cx = child.get('x', 0.0) + child.get('width', 0.0)
            cy = child.get('y', 0.0) + child.get('height', 0.0)
            max_x = max(max_x, cx)
            max_y = max(max_y, cy)

        graph['width'] = max_x + padding['right']
        graph['height'] = max_y + padding['bottom']
