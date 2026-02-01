"""Radial layout algorithm."""
import math
from ..options import get_padding, get_spacing


class RadialLayoutProvider:
    """Layout nodes in concentric circles based on graph distance from root."""

    def layout(self, graph: dict, global_options: dict = None) -> None:
        children = graph.get('children', [])
        if not children:
            return

        padding = get_padding(graph, global_options)
        node_spacing = get_spacing(graph, 'elk.spacing.nodeNode', global_options, 50.0)

        for child in children:
            child.setdefault('width', 0.0)
            child.setdefault('height', 0.0)

        n = len(children)
        node_ids = [str(c.get('id', i)) for i, c in enumerate(children)]
        node_index = {nid: i for i, nid in enumerate(node_ids)}

        # Build adjacency
        adj = [[] for _ in range(n)]
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
                        adj[si].append(ti)
                        adj[ti].append(si)

        # BFS from root (node 0 or node with most connections)
        root = max(range(n), key=lambda i: len(adj[i])) if n > 0 else 0

        dist = [-1] * n
        dist[root] = 0
        queue = [root]
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    queue.append(v)

        # Handle disconnected nodes
        for i in range(n):
            if dist[i] == -1:
                dist[i] = max(d for d in dist if d >= 0) + 1

        # Group by level
        max_level = max(dist)
        levels = [[] for _ in range(max_level + 1)]
        for i in range(n):
            levels[dist[i]].append(i)

        # Place nodes in concentric circles
        radius_step = node_spacing * 2

        for level, nodes_at_level in enumerate(levels):
            if level == 0:
                # Center node
                for idx in nodes_at_level:
                    children[idx]['x'] = 0
                    children[idx]['y'] = 0
            else:
                radius = level * radius_step
                count = len(nodes_at_level)
                for j, idx in enumerate(nodes_at_level):
                    angle = 2 * math.pi * j / count
                    children[idx]['x'] = radius * math.cos(angle)
                    children[idx]['y'] = radius * math.sin(angle)

        # Normalize positions
        min_x = min(c['x'] for c in children)
        min_y = min(c['y'] for c in children)
        for child in children:
            child['x'] = child['x'] - min_x + padding['left']
            child['y'] = child['y'] - min_y + padding['top']

        # Route edges
        node_map = {str(c.get('id', i)): c for i, c in enumerate(children)}
        for edge in graph.get('edges', []):
            self._route_edge(edge, node_map)

        # Compute size
        max_x = max(c['x'] + c.get('width', 0) for c in children)
        max_y = max(c['y'] + c.get('height', 0) for c in children)
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
