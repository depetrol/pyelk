"""MrTree layout algorithm - tree layout."""
from ..options import get_padding, get_spacing, get_direction


class MrTreeLayoutProvider:
    """Layout trees using a hierarchical tree layout."""

    def layout(self, graph: dict, global_options: dict = None) -> None:
        children = graph.get('children', [])
        if not children:
            return

        padding = get_padding(graph, global_options)
        node_spacing = get_spacing(graph, 'elk.spacing.nodeNode', global_options, 20.0)
        layer_spacing = get_spacing(graph, 'elk.layered.spacing.nodeNodeBetweenLayers',
                                    global_options, 20.0)
        direction = get_direction(graph, global_options)

        for child in children:
            child.setdefault('width', 0.0)
            child.setdefault('height', 0.0)

        # Build adjacency
        node_ids = [str(c.get('id', i)) for i, c in enumerate(children)]
        node_index = {nid: i for i, nid in enumerate(node_ids)}
        n = len(children)

        children_of = [[] for _ in range(n)]
        has_parent = [False] * n

        for edge in graph.get('edges', []):
            sources = edge.get('sources', [])
            targets = edge.get('targets', [])
            if not sources and 'source' in edge:
                sources = [edge['source']]
            if not targets and 'target' in edge:
                targets = [edge['target']]
            for s in sources:
                for t in targets:
                    si = node_index.get(str(s))
                    ti = node_index.get(str(t))
                    if si is not None and ti is not None and si != ti:
                        children_of[si].append(ti)
                        has_parent[ti] = True

        # Find roots
        roots = [i for i in range(n) if not has_parent[i]]
        if not roots:
            roots = [0]

        # Compute tree layout
        horizontal = direction in ('RIGHT', 'LEFT')

        # Compute subtree sizes
        subtree_size = [0.0] * n
        levels = {}

        def compute_subtree(node_idx, level):
            levels[node_idx] = level
            child_indices = children_of[node_idx]
            if not child_indices:
                if horizontal:
                    subtree_size[node_idx] = children[node_idx].get('height', 0)
                else:
                    subtree_size[node_idx] = children[node_idx].get('width', 0)
                return

            total = 0
            for ci in child_indices:
                compute_subtree(ci, level + 1)
                total += subtree_size[ci]
            total += node_spacing * (len(child_indices) - 1)

            if horizontal:
                subtree_size[node_idx] = max(total, children[node_idx].get('height', 0))
            else:
                subtree_size[node_idx] = max(total, children[node_idx].get('width', 0))

        for root in roots:
            compute_subtree(root, 0)

        # Place nodes
        def place_node(node_idx, offset, depth):
            child = children[node_idx]
            w = child.get('width', 0)
            h = child.get('height', 0)

            if horizontal:
                child['x'] = padding['left'] + depth * (
                        max(c.get('width', 0) for c in children) + layer_spacing)
                child['y'] = offset + (subtree_size[node_idx] - h) / 2
            else:
                child['x'] = offset + (subtree_size[node_idx] - w) / 2
                child['y'] = padding['top'] + depth * (
                        max(c.get('height', 0) for c in children) + layer_spacing)

            child_indices = children_of[node_idx]
            current_offset = offset
            for ci in child_indices:
                place_node(ci, current_offset, depth + 1)
                current_offset += subtree_size[ci] + node_spacing

        current_offset = padding['top'] if horizontal else padding['left']
        for root in roots:
            place_node(root, current_offset, 0)
            current_offset += subtree_size[root] + node_spacing

        # Route edges
        node_map = {str(c.get('id', i)): c for i, c in enumerate(children)}
        for edge in graph.get('edges', []):
            self._route_edge(edge, node_map)

        # Compute size
        max_x = max((c['x'] + c.get('width', 0)) for c in children) if children else 0
        max_y = max((c['y'] + c.get('height', 0)) for c in children) if children else 0
        graph['width'] = max_x + padding['right']
        graph['height'] = max_y + padding['bottom']

    def _route_edge(self, edge: dict, node_map: dict) -> None:
        sources = edge.get('sources', [])
        targets = edge.get('targets', [])
        if not sources and 'source' in edge:
            sources = [edge['source']]
        if not targets and 'target' in edge:
            targets = [edge['target']]

        src_id = sources[0] if sources else None
        tgt_id = targets[0] if targets else None
        src = node_map.get(str(src_id)) if src_id else None
        tgt = node_map.get(str(tgt_id)) if tgt_id else None

        if src and tgt:
            sx = src.get('x', 0) + src.get('width', 0) / 2
            sy = src.get('y', 0) + src.get('height', 0) / 2
            tx = tgt.get('x', 0) + tgt.get('width', 0) / 2
            ty = tgt.get('y', 0) + tgt.get('height', 0) / 2
            edge['sections'] = [{
                'id': str(edge.get('id', '')) + '_s0',
                'startPoint': {'x': sx, 'y': sy},
                'endPoint': {'x': tx, 'y': ty},
            }]
