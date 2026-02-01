"""Stress minimization layout algorithm."""
import math
import random
from ..options import get_padding, get_spacing, get_option


class StressLayoutProvider:
    """Layout using stress minimization (Kamada-Kawai style)."""

    def layout(self, graph: dict, global_options: dict = None) -> None:
        children = graph.get('children', [])
        if not children:
            return

        padding = get_padding(graph, global_options)
        desired_edge_length = get_spacing(graph, 'elk.spacing.nodeNode', global_options, 50.0)

        # Build adjacency from edges
        node_ids = [str(c.get('id', i)) for i, c in enumerate(children)]
        node_index = {nid: i for i, nid in enumerate(node_ids)}
        n = len(children)

        # Initialize positions
        for i, child in enumerate(children):
            if 'x' not in child or child['x'] == 0:
                child['x'] = random.uniform(0, 200)
            if 'y' not in child or child['y'] == 0:
                child['y'] = random.uniform(0, 200)
            child.setdefault('width', 0.0)
            child.setdefault('height', 0.0)

        # Build distance matrix using BFS
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

        # Compute shortest path distances (BFS)
        dist = [[float('inf')] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
            queue = [i]
            head = 0
            while head < len(queue):
                u = queue[head]
                head += 1
                for v in adj[u]:
                    if dist[i][v] == float('inf'):
                        dist[i][v] = dist[i][u] + 1
                        queue.append(v)

        # Replace inf with max_dist + 1
        max_dist = 0
        for i in range(n):
            for j in range(n):
                if dist[i][j] != float('inf'):
                    max_dist = max(max_dist, dist[i][j])
        for i in range(n):
            for j in range(n):
                if dist[i][j] == float('inf'):
                    dist[i][j] = max_dist + 1

        # Stress minimization iterations
        positions = [(c['x'] + c['width'] / 2, c['y'] + c['height'] / 2)
                     for c in children]

        for iteration in range(200):
            max_movement = 0.0
            new_positions = list(positions)

            for i in range(n):
                num_x, num_y, denom = 0.0, 0.0, 0.0

                for j in range(n):
                    if i == j:
                        continue
                    d_ij = dist[i][j] * desired_edge_length
                    w_ij = 1.0 / (d_ij * d_ij) if d_ij > 0 else 0

                    dx = positions[i][0] - positions[j][0]
                    dy = positions[i][1] - positions[j][1]
                    actual = math.sqrt(dx * dx + dy * dy)

                    if actual > 0.001:
                        num_x += w_ij * (positions[j][0] + d_ij * dx / actual)
                        num_y += w_ij * (positions[j][1] + d_ij * dy / actual)
                    else:
                        num_x += w_ij * (positions[j][0] + d_ij)
                        num_y += w_ij * positions[j][1]
                    denom += w_ij

                if denom > 0:
                    new_x = num_x / denom
                    new_y = num_y / denom
                    movement = math.sqrt((new_x - positions[i][0]) ** 2 +
                                         (new_y - positions[i][1]) ** 2)
                    max_movement = max(max_movement, movement)
                    new_positions[i] = (new_x, new_y)

            positions = new_positions
            if max_movement < 0.01:
                break

        # Apply positions
        min_x = min(p[0] for p in positions)
        min_y = min(p[1] for p in positions)

        for i, child in enumerate(children):
            child['x'] = positions[i][0] - min_x + padding['left']
            child['y'] = positions[i][1] - min_y + padding['top']

        # Route edges
        node_map = {str(c.get('id', i)): c for i, c in enumerate(children)}
        for edge in graph.get('edges', []):
            self._route_edge(edge, node_map)

        # Compute graph size
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
