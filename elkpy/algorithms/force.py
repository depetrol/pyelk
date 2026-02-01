"""Force-directed layout algorithm."""
import math
import random
from ..options import get_padding, get_spacing


class ForceLayoutProvider:
    """Layout using force-directed (Fruchterman-Reingold style) approach."""

    def layout(self, graph: dict, global_options: dict = None) -> None:
        children = graph.get('children', [])
        if not children:
            return

        padding = get_padding(graph, global_options)
        node_spacing = get_spacing(graph, 'elk.spacing.nodeNode', global_options, 50.0)
        n = len(children)

        # Initialize positions
        for child in children:
            if 'x' not in child or child['x'] == 0:
                child['x'] = random.uniform(0, 100)
            if 'y' not in child or child['y'] == 0:
                child['y'] = random.uniform(0, 100)
            child.setdefault('width', 0.0)
            child.setdefault('height', 0.0)

        # Build edge list
        node_ids = [str(c.get('id', i)) for i, c in enumerate(children)]
        node_index = {nid: i for i, nid in enumerate(node_ids)}

        edge_list = []
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
                        edge_list.append((si, ti))

        area = n * node_spacing * node_spacing
        k = math.sqrt(area / max(n, 1))
        temperature = k * 10

        positions = [(c['x'] + c['width'] / 2, c['y'] + c['height'] / 2)
                     for c in children]

        for iteration in range(300):
            forces = [(0.0, 0.0)] * n

            # Repulsive forces
            for i in range(n):
                for j in range(i + 1, n):
                    dx = positions[i][0] - positions[j][0]
                    dy = positions[i][1] - positions[j][1]
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < 0.01:
                        dist = 0.01
                    force = k * k / dist
                    fx = force * dx / dist
                    fy = force * dy / dist
                    forces[i] = (forces[i][0] + fx, forces[i][1] + fy)
                    forces[j] = (forces[j][0] - fx, forces[j][1] - fy)

            # Attractive forces
            for si, ti in edge_list:
                dx = positions[si][0] - positions[ti][0]
                dy = positions[si][1] - positions[ti][1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 0.01:
                    dist = 0.01
                force = dist * dist / k
                fx = force * dx / dist
                fy = force * dy / dist
                forces[si] = (forces[si][0] - fx, forces[si][1] - fy)
                forces[ti] = (forces[ti][0] + fx, forces[ti][1] + fy)

            # Apply forces with temperature
            new_positions = []
            for i in range(n):
                fx, fy = forces[i]
                mag = math.sqrt(fx * fx + fy * fy)
                if mag > 0:
                    dx = fx / mag * min(mag, temperature)
                    dy = fy / mag * min(mag, temperature)
                else:
                    dx, dy = 0, 0
                new_positions.append((positions[i][0] + dx, positions[i][1] + dy))

            positions = new_positions
            temperature *= 0.95

            if temperature < 0.01:
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
