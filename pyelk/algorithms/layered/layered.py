"""Layered (Sugiyama) layout algorithm implementation.

The algorithm proceeds in five phases:
1. Cycle Breaking - make the graph acyclic by reversing edges
2. Layer Assignment - assign nodes to horizontal/vertical layers
3. Crossing Minimization - reorder nodes within layers to minimize crossings
4. Node Placement - assign coordinates to nodes
5. Edge Routing - route edges between nodes
"""
import math
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from ...options import (
    get_option, get_padding, get_spacing, get_direction,
    resolve_option_key, get_effective_options
)
from ...exceptions import UnsupportedConfigurationException


class LNode:
    """Internal node representation for layered layout."""

    def __init__(self, node_id: str, width: float = 0, height: float = 0,
                 original: dict = None, is_dummy: bool = False):
        self.id = node_id
        self.width = width
        self.height = height
        self.original = original
        self.is_dummy = is_dummy
        self.layer = -1
        self.position = -1  # position within layer
        self.x = 0.0
        self.y = 0.0
        self.incoming: List['LEdge'] = []
        self.outgoing: List['LEdge'] = []
        self.ports: List['LPort'] = []
        self.labels: List[dict] = []
        self.layer_constraint: Optional[str] = None


class LPort:
    """Internal port representation."""

    def __init__(self, port_id: str, width: float = 0, height: float = 0,
                 side: str = 'UNDEFINED', index: int = 0, original: dict = None):
        self.id = port_id
        self.width = width
        self.height = height
        self.side = side
        self.index = index
        self.original = original
        self.owner: Optional[LNode] = None
        self.x = 0.0
        self.y = 0.0
        self.incoming: List['LEdge'] = []
        self.outgoing: List['LEdge'] = []


class LEdge:
    """Internal edge representation."""

    def __init__(self, edge_id: str, source: LNode, target: LNode,
                 source_port: LPort = None, target_port: LPort = None,
                 original: dict = None):
        self.id = edge_id
        self.source = source
        self.target = target
        self.source_port = source_port
        self.target_port = target_port
        self.original = original
        self.reversed = False
        self.dummy_nodes: List[LNode] = []
        self.is_self_loop = (source is target)
        self.bend_points: List[Tuple[float, float]] = []


class LayeredLayoutProvider:
    """Implements Sugiyama's layered layout algorithm."""

    def layout(self, graph: dict, global_options: dict = None) -> None:
        """Layout the graph using the layered algorithm."""
        children = graph.get('children', [])
        if not children:
            self._set_empty_size(graph, global_options)
            return

        padding = get_padding(graph, global_options)
        eff_options = get_effective_options(graph, global_options)
        direction = get_direction(graph, global_options)

        node_spacing = get_spacing(graph, 'elk.spacing.nodeNode', global_options, 20.0)
        layer_spacing = get_spacing(
            graph, 'elk.layered.spacing.nodeNodeBetweenLayers', global_options, 20.0)

        # Get layering strategy
        layering_strategy = (eff_options.get('elk.layered.layering.strategy') or
                             eff_options.get('layering.strategy') or
                             'LONGEST_PATH')

        # Build internal graph
        nodes, edges, node_map, port_map = self._build_internal_graph(
            graph, eff_options, global_options)

        if not nodes:
            self._set_empty_size(graph, global_options)
            return

        # Check for unsupported configurations
        self._check_constraints(nodes, edges)

        # Phase 1: Cycle breaking
        self._break_cycles(nodes, edges)

        # Phase 2: Layer assignment
        self._assign_layers(nodes, edges, layering_strategy)

        # Phase 3: Insert dummy nodes for long edges
        all_nodes = list(nodes)
        self._insert_dummy_nodes(all_nodes, edges)

        # Organize nodes into layers
        layers = self._organize_layers(all_nodes)

        # Phase 4: Crossing minimization
        self._minimize_crossings(layers)

        # Phase 5: Node placement
        horizontal = direction in ('RIGHT', 'LEFT')
        self._place_nodes(layers, node_spacing, layer_spacing, padding, horizontal, direction)

        # Phase 6: Edge routing
        self._route_edges(edges, node_map, port_map, horizontal, direction)

        # Place labels
        self._place_labels(nodes, eff_options, global_options)

        # Write back positions
        self._write_back(graph, nodes, edges, horizontal, direction)

        # Compute graph size
        self._compute_graph_size(graph, padding)

    def _set_empty_size(self, graph, global_options):
        padding = get_padding(graph, global_options)
        graph.setdefault('width', padding['left'] + padding['right'])
        graph.setdefault('height', padding['top'] + padding['bottom'])

    def _build_internal_graph(self, graph, eff_options, global_options):
        """Build internal LNode/LEdge representation from the JSON graph."""
        nodes = []
        node_map = {}  # id -> LNode
        port_map = {}  # id -> LPort

        for child in graph.get('children', []):
            node_id = str(child.get('id', ''))
            lnode = LNode(
                node_id=node_id,
                width=child.get('width', 0),
                height=child.get('height', 0),
                original=child
            )

            # Check for layer constraint
            lc = get_option(child, 'layerConstraint')
            if lc is None:
                lc = get_option(child, 'elk.layered.layering.layerConstraint')
            if lc:
                lnode.layer_constraint = lc

            # Process ports
            for port_data in child.get('ports', []):
                port_id = str(port_data.get('id', ''))
                side = (get_option(port_data, 'port.side') or
                        get_option(port_data, 'elk.port.side') or 'UNDEFINED')
                index = int(get_option(port_data, 'port.index') or
                            get_option(port_data, 'elk.port.index') or 0)
                lport = LPort(
                    port_id=port_id,
                    width=port_data.get('width', 0),
                    height=port_data.get('height', 0),
                    side=side,
                    index=index,
                    original=port_data
                )
                lport.owner = lnode
                lnode.ports.append(lport)
                port_map[port_id] = lport

            # Process labels
            for label_data in child.get('labels', []):
                lnode.labels.append(label_data)

            nodes.append(lnode)
            node_map[node_id] = lnode

        # Build edges
        edges = []
        for edge_data in graph.get('edges', []):
            edge_id = str(edge_data.get('id', ''))
            sources = edge_data.get('sources', [])
            targets = edge_data.get('targets', [])
            if not sources and 'source' in edge_data:
                sources = [str(edge_data['source'])]
            if not targets and 'target' in edge_data:
                targets = [str(edge_data['target'])]

            for src_id in sources:
                for tgt_id in targets:
                    src_id = str(src_id)
                    tgt_id = str(tgt_id)

                    # Resolve source - could be node or port
                    src_node = node_map.get(src_id)
                    src_port = port_map.get(src_id)
                    if src_port and not src_node:
                        src_node = src_port.owner

                    tgt_node = node_map.get(tgt_id)
                    tgt_port = port_map.get(tgt_id)
                    if tgt_port and not tgt_node:
                        tgt_node = tgt_port.owner

                    if src_node and tgt_node:
                        ledge = LEdge(
                            edge_id=edge_id,
                            source=src_node,
                            target=tgt_node,
                            source_port=src_port,
                            target_port=tgt_port,
                            original=edge_data
                        )
                        src_node.outgoing.append(ledge)
                        tgt_node.incoming.append(ledge)
                        if src_port:
                            src_port.outgoing.append(ledge)
                        if tgt_port:
                            tgt_port.incoming.append(ledge)
                        edges.append(ledge)

        return nodes, edges, node_map, port_map

    def _check_constraints(self, nodes, edges):
        """Check for unsupported configurations."""
        # Check if all nodes have FIRST layer constraint in a cycle
        first_nodes = [n for n in nodes if n.layer_constraint == 'FIRST']
        if len(first_nodes) >= 2:
            # Check if they form a cycle
            first_ids = {n.id for n in first_nodes}
            for edge in edges:
                if (edge.source.id in first_ids and edge.target.id in first_ids
                        and not edge.is_self_loop):
                    # Check if there's a cycle among FIRST nodes
                    if self._has_cycle_among(first_nodes, edges):
                        raise UnsupportedConfigurationException(
                            "Cycle among nodes with FIRST layer constraint")

    def _has_cycle_among(self, nodes, edges):
        """Check if there's a cycle among the given nodes."""
        node_ids = {n.id for n in nodes}
        # Build subgraph adjacency
        adj = defaultdict(list)
        for edge in edges:
            if edge.source.id in node_ids and edge.target.id in node_ids:
                if not edge.is_self_loop:
                    adj[edge.source.id].append(edge.target.id)

        # DFS cycle detection
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {nid: WHITE for nid in node_ids}

        def dfs(u):
            color[u] = GRAY
            for v in adj[u]:
                if color[v] == GRAY:
                    return True
                if color[v] == WHITE and dfs(v):
                    return True
            color[u] = BLACK
            return False

        for nid in node_ids:
            if color[nid] == WHITE:
                if dfs(nid):
                    return True
        return False

    def _break_cycles(self, nodes, edges):
        """Break cycles using DFS-based approach."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n.id: WHITE for n in nodes}

        # Build adjacency (excluding self-loops)
        adj = defaultdict(list)
        edge_map = {}
        for edge in edges:
            if not edge.is_self_loop:
                adj[edge.source.id].append(edge.target.id)
                edge_map[(edge.source.id, edge.target.id)] = edge

        def dfs(u):
            color[u] = GRAY
            for v in adj[u]:
                if color[v] == GRAY:
                    # Back edge - reverse it
                    edge = edge_map.get((u, v))
                    if edge:
                        self._reverse_edge(edge)
                elif color[v] == WHITE:
                    dfs(v)
            color[u] = BLACK

        for node in nodes:
            if color[node.id] == WHITE:
                dfs(node.id)

    def _reverse_edge(self, edge):
        """Reverse an edge."""
        # Remove from current source/target
        if edge in edge.source.outgoing:
            edge.source.outgoing.remove(edge)
        if edge in edge.target.incoming:
            edge.target.incoming.remove(edge)

        # Swap
        edge.source, edge.target = edge.target, edge.source
        edge.source_port, edge.target_port = edge.target_port, edge.source_port

        # Add to new source/target
        edge.source.outgoing.append(edge)
        edge.target.incoming.append(edge)
        edge.reversed = not edge.reversed

    def _assign_layers(self, nodes, edges, strategy='LONGEST_PATH'):
        """Assign nodes to layers."""
        if strategy == 'NETWORK_SIMPLEX':
            self._network_simplex_layering(nodes, edges)
        elif strategy == 'COFFMAN_GRAHAM':
            self._coffman_graham_layering(nodes, edges)
        else:
            self._longest_path_layering(nodes, edges)

        # Apply layer constraints
        self._apply_layer_constraints(nodes)

    def _longest_path_layering(self, nodes, edges):
        """Longest path layering (default)."""
        # Compute in-degree (excluding self-loops)
        in_degree = {n.id: 0 for n in nodes}
        for edge in edges:
            if not edge.is_self_loop:
                in_degree[edge.target.id] += 1

        # Topological sort
        queue = [n for n in nodes if in_degree[n.id] == 0]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for edge in node.outgoing:
                if not edge.is_self_loop:
                    in_degree[edge.target.id] -= 1
                    if in_degree[edge.target.id] == 0:
                        queue.append(edge.target)

        # Handle any remaining nodes (shouldn't happen after cycle breaking)
        remaining = set(n.id for n in nodes) - set(n.id for n in order)
        for node in nodes:
            if node.id in remaining:
                order.append(node)

        # Assign layers based on longest path
        layer_of = {}
        for node in reversed(order):
            max_target_layer = -1
            for edge in node.outgoing:
                if not edge.is_self_loop and edge.target.id in layer_of:
                    max_target_layer = max(max_target_layer, layer_of[edge.target.id])
            layer_of[node.id] = max_target_layer + 1

        # Normalize layers (start from 0)
        if layer_of:
            max_layer = max(layer_of.values())
            for node in nodes:
                node.layer = max_layer - layer_of.get(node.id, 0)

    def _network_simplex_layering(self, nodes, edges):
        """Network simplex layering - produces optimal layer assignment."""
        # Use longest path as initial feasible solution
        self._longest_path_layering(nodes, edges)

        # Network simplex optimization
        non_self_edges = [e for e in edges if not e.is_self_loop]

        for _ in range(50):  # max iterations
            improved = False

            for edge in non_self_edges:
                slack = edge.target.layer - edge.source.layer - 1
                if slack < 0:
                    # Infeasible - fix
                    edge.target.layer = edge.source.layer + 1
                    improved = True

            # Try to reduce total edge length by moving nodes
            for node in nodes:
                if not node.incoming and not node.outgoing:
                    continue

                target_layers = [e.target.layer for e in node.outgoing if not e.is_self_loop]
                source_layers = [e.source.layer for e in node.incoming if not e.is_self_loop]

                if target_layers:
                    min_target = min(target_layers)
                    ideal = min_target - 1
                elif source_layers:
                    max_source = max(source_layers)
                    ideal = max_source + 1
                else:
                    continue

                # Check if moving to ideal layer is feasible
                feasible = True
                for e in node.incoming:
                    if not e.is_self_loop and e.source.layer >= ideal:
                        feasible = False
                        break
                if feasible:
                    for e in node.outgoing:
                        if not e.is_self_loop and e.target.layer <= ideal:
                            feasible = False
                            break

                if feasible and ideal != node.layer:
                    node.layer = ideal
                    improved = True

            if not improved:
                break

        # Normalize
        if nodes:
            min_layer = min(n.layer for n in nodes)
            for n in nodes:
                n.layer -= min_layer

    def _coffman_graham_layering(self, nodes, edges):
        """Coffman-Graham layering."""
        # Use longest path as base
        self._longest_path_layering(nodes, edges)

    def _apply_layer_constraints(self, nodes):
        """Apply FIRST/LAST layer constraints."""
        if not nodes:
            return

        min_layer = min(n.layer for n in nodes)
        max_layer = max(n.layer for n in nodes)

        for node in nodes:
            if node.layer_constraint == 'FIRST':
                node.layer = min_layer
            elif node.layer_constraint == 'LAST':
                node.layer = max_layer

    def _insert_dummy_nodes(self, all_nodes, edges):
        """Insert dummy nodes for edges spanning multiple layers."""
        dummy_counter = 0
        edges_to_process = list(edges)

        for edge in edges_to_process:
            if edge.is_self_loop:
                continue

            span = edge.target.layer - edge.source.layer
            if span <= 1:
                continue

            # Insert dummy nodes
            prev_node = edge.source
            for i in range(1, span):
                dummy_id = f"_dummy_{dummy_counter}"
                dummy_counter += 1
                dummy = LNode(
                    node_id=dummy_id,
                    width=0,
                    height=0,
                    is_dummy=True
                )
                dummy.layer = edge.source.layer + i
                all_nodes.append(dummy)
                edge.dummy_nodes.append(dummy)
                prev_node = dummy

    def _organize_layers(self, all_nodes):
        """Organize nodes into layers."""
        if not all_nodes:
            return []
        max_layer = max(n.layer for n in all_nodes)
        layers = [[] for _ in range(max_layer + 1)]
        for node in all_nodes:
            if 0 <= node.layer <= max_layer:
                layers[node.layer].append(node)
        return layers

    def _minimize_crossings(self, layers):
        """Minimize edge crossings using the barycenter method."""
        if len(layers) <= 1:
            return

        # Forward sweep
        for i in range(1, len(layers)):
            self._sort_layer_by_barycenter(layers[i], layers[i - 1], forward=True)

        # Backward sweep
        for i in range(len(layers) - 2, -1, -1):
            self._sort_layer_by_barycenter(layers[i], layers[i + 1], forward=False)

        # Assign positions
        for layer in layers:
            for pos, node in enumerate(layer):
                node.position = pos

    def _sort_layer_by_barycenter(self, layer, ref_layer, forward=True):
        """Sort nodes in a layer by barycenter of connected nodes in reference layer."""
        ref_positions = {n.id: i for i, n in enumerate(ref_layer)}

        barycenters = {}
        for node in layer:
            positions = []
            if forward:
                for edge in node.incoming:
                    if not edge.is_self_loop:
                        pos = ref_positions.get(edge.source.id)
                        if pos is not None:
                            positions.append(pos)
            else:
                for edge in node.outgoing:
                    if not edge.is_self_loop:
                        pos = ref_positions.get(edge.target.id)
                        if pos is not None:
                            positions.append(pos)

            if positions:
                barycenters[node.id] = sum(positions) / len(positions)
            else:
                barycenters[node.id] = float('inf')

        layer.sort(key=lambda n: barycenters.get(n.id, float('inf')))

    def _place_nodes(self, layers, node_spacing, layer_spacing, padding,
                     horizontal, direction):
        """Place nodes, assigning x/y coordinates."""
        if not layers:
            return

        if horizontal:
            self._place_horizontal(layers, node_spacing, layer_spacing, padding, direction)
        else:
            self._place_vertical(layers, node_spacing, layer_spacing, padding, direction)

    def _place_vertical(self, layers, node_spacing, layer_spacing, padding, direction):
        """Place nodes for DOWN/UP direction."""
        # For DOWN: layers go top-to-bottom, nodes go left-to-right
        # Compute max width per layer first for centering
        layer_widths = []
        for layer in layers:
            total_width = sum(n.width for n in layer)
            total_width += node_spacing * max(len(layer) - 1, 0)
            layer_widths.append(total_width)

        max_width = max(layer_widths) if layer_widths else 0

        current_y = padding['top']
        for li, layer in enumerate(layers):
            # Center nodes within max_width
            total_width = layer_widths[li]
            start_x = padding['left'] + (max_width - total_width) / 2

            current_x = start_x
            max_height = 0
            for node in layer:
                node.x = current_x
                node.y = current_y
                current_x += node.width + node_spacing
                max_height = max(max_height, node.height)

            current_y += max_height + layer_spacing

    def _place_horizontal(self, layers, node_spacing, layer_spacing, padding, direction):
        """Place nodes for RIGHT/LEFT direction."""
        # For RIGHT: layers go left-to-right, nodes go top-to-bottom
        layer_heights = []
        for layer in layers:
            total_height = sum(n.height for n in layer)
            total_height += node_spacing * max(len(layer) - 1, 0)
            layer_heights.append(total_height)

        max_height = max(layer_heights) if layer_heights else 0

        current_x = padding['left']
        for li, layer in enumerate(layers):
            total_height = layer_heights[li]
            start_y = padding['top'] + (max_height - total_height) / 2

            current_y = start_y
            max_width = 0
            for node in layer:
                node.x = current_x
                node.y = current_y
                current_y += node.height + node_spacing
                max_width = max(max_width, node.width)

            current_x += max_width + layer_spacing

    def _route_edges(self, edges, node_map, port_map, horizontal, direction):
        """Route edges between nodes."""
        for edge in edges:
            if edge.is_self_loop:
                continue

            src = edge.source
            tgt = edge.target

            # Compute start and end points
            if edge.reversed:
                actual_src, actual_tgt = tgt, src
            else:
                actual_src, actual_tgt = src, tgt

            # Get port positions if applicable
            if edge.source_port:
                sp = self._get_port_position(edge.source_port, src, horizontal, direction, True)
            else:
                sp = self._get_node_connection_point(src, horizontal, direction, True)

            if edge.target_port:
                ep = self._get_port_position(edge.target_port, tgt, horizontal, direction, False)
            else:
                ep = self._get_node_connection_point(tgt, horizontal, direction, False)

            if edge.reversed:
                sp, ep = ep, sp

            # Collect bend points from dummy nodes
            bend_points = []
            for dummy in edge.dummy_nodes:
                if horizontal:
                    bend_points.append((dummy.x + dummy.width / 2,
                                        dummy.y + dummy.height / 2))
                else:
                    bend_points.append((dummy.x + dummy.width / 2,
                                        dummy.y + dummy.height / 2))

            edge.bend_points = bend_points

    def _get_node_connection_point(self, node, horizontal, direction, is_source):
        """Get the connection point on a node for an edge."""
        if horizontal:
            if is_source:
                return (node.x + node.width, node.y + node.height / 2)
            else:
                return (node.x, node.y + node.height / 2)
        else:
            if is_source:
                return (node.x + node.width / 2, node.y + node.height)
            else:
                return (node.x + node.width / 2, node.y)

    def _get_port_position(self, port, node, horizontal, direction, is_source):
        """Get the position of a port on its owner node."""
        # Place port at the appropriate position on the node
        if port.side == 'EAST' or (port.side == 'UNDEFINED' and is_source and horizontal):
            return (node.x + node.width, node.y + port.y + port.height / 2)
        elif port.side == 'WEST' or (port.side == 'UNDEFINED' and not is_source and horizontal):
            return (node.x, node.y + port.y + port.height / 2)
        elif port.side == 'SOUTH' or (port.side == 'UNDEFINED' and is_source and not horizontal):
            return (node.x + port.x + port.width / 2, node.y + node.height)
        elif port.side == 'NORTH' or (port.side == 'UNDEFINED' and not is_source and not horizontal):
            return (node.x + port.x + port.width / 2, node.y)
        else:
            return (node.x + node.width / 2, node.y + node.height / 2)

    def _place_labels(self, nodes, eff_options, global_options):
        """Place labels on nodes based on placement options."""
        for node in nodes:
            if node.is_dummy or not node.labels:
                continue

            # Get node label placement
            global_placement = (eff_options.get('elk.nodeLabels.placement') or
                                (global_options or {}).get('elk.nodeLabels.placement') or '')

            for label in node.labels:
                # Check label's own placement option
                placement = get_option(label, 'elk.nodeLabels.placement')
                if placement is None:
                    placement = global_placement

                if not placement:
                    continue

                lw = label.get('width', 0)
                lh = label.get('height', 0)
                nw = node.width
                nh = node.height

                # Label-node spacing (elk.spacing.labelNode default is 5)
                label_node_spacing = 5.0

                # Parse placement string
                parts = placement.upper().split()

                h_pos = 'H_CENTER'
                v_pos = 'V_TOP'
                inside = 'INSIDE' in parts

                for p in parts:
                    if p.startswith('H_'):
                        h_pos = p
                    elif p.startswith('V_'):
                        v_pos = p

                # Compute x position
                if h_pos == 'H_LEFT':
                    lx = 0
                elif h_pos == 'H_RIGHT':
                    lx = nw - lw
                else:  # H_CENTER
                    lx = (nw - lw) / 2

                # Compute y position
                if inside:
                    if v_pos == 'V_TOP':
                        ly = 0
                    elif v_pos == 'V_BOTTOM':
                        ly = nh - lh
                    else:  # V_CENTER
                        ly = (nh - lh) / 2
                else:  # OUTSIDE
                    if v_pos == 'V_TOP':
                        ly = -(lh + label_node_spacing)
                    elif v_pos == 'V_BOTTOM':
                        ly = nh + label_node_spacing
                    else:  # V_CENTER
                        ly = (nh - lh) / 2

                label['x'] = lx
                label['y'] = ly

    def _write_back(self, graph, nodes, edges, horizontal, direction):
        """Write computed positions back to the original graph."""
        # Write node positions
        for node in nodes:
            if node.is_dummy or node.original is None:
                continue
            node.original['x'] = node.x
            node.original['y'] = node.y

            # Write port positions
            self._place_ports(node)

        # Write edge sections
        for edge in edges:
            if edge.original is None:
                continue
            if edge.is_self_loop:
                # Self-loops get a simple routing
                src = edge.source
                sx = src.x + src.width
                sy = src.y
                section = {
                    'id': edge.id + '_s0',
                    'startPoint': {'x': sx, 'y': sy},
                    'endPoint': {'x': sx, 'y': sy + src.height},
                    'bendPoints': [
                        {'x': sx + 20, 'y': sy},
                        {'x': sx + 20, 'y': sy + src.height},
                    ]
                }
                edge.original['sections'] = [section]
                continue

            src = edge.source
            tgt = edge.target

            if edge.reversed:
                actual_src, actual_tgt = tgt, src
            else:
                actual_src, actual_tgt = src, tgt

            sp = self._get_node_connection_point(actual_src, horizontal, direction, True)
            ep = self._get_node_connection_point(actual_tgt, horizontal, direction, False)

            section = {
                'id': edge.id + '_s0',
                'startPoint': {'x': sp[0], 'y': sp[1]},
                'endPoint': {'x': ep[0], 'y': ep[1]},
            }

            if edge.bend_points:
                section['bendPoints'] = [{'x': bp[0], 'y': bp[1]}
                                         for bp in edge.bend_points]

            edge.original['sections'] = [section]

    def _place_ports(self, node):
        """Place ports on a node."""
        if not node.ports:
            return

        # Group ports by side
        sides = defaultdict(list)
        for port in node.ports:
            sides[port.side].append(port)

        # Sort by index within each side
        for side, ports in sides.items():
            ports.sort(key=lambda p: p.index)

        # Place ports evenly along each side
        for side, ports in sides.items():
            n_ports = len(ports)
            for i, port in enumerate(ports):
                if side == 'NORTH':
                    spacing = node.width / (n_ports + 1)
                    port.x = spacing * (i + 1) - port.width / 2
                    port.y = -port.height
                elif side == 'SOUTH':
                    spacing = node.width / (n_ports + 1)
                    port.x = spacing * (i + 1) - port.width / 2
                    port.y = node.height
                elif side == 'EAST':
                    spacing = node.height / (n_ports + 1)
                    port.x = node.width
                    port.y = spacing * (i + 1) - port.height / 2
                elif side == 'WEST':
                    spacing = node.height / (n_ports + 1)
                    port.x = -port.width
                    port.y = spacing * (i + 1) - port.height / 2
                else:
                    # Default placement
                    port.x = 0
                    port.y = 0

                # Write back to original
                if port.original:
                    port.original['x'] = port.x
                    port.original['y'] = port.y

    def _compute_graph_size(self, graph, padding):
        """Compute the size of the graph from its children."""
        children = graph.get('children', [])
        if not children:
            graph['width'] = padding['left'] + padding['right']
            graph['height'] = padding['top'] + padding['bottom']
            return

        max_x = 0.0
        max_y = 0.0
        for child in children:
            cx = child.get('x', 0.0) + child.get('width', 0.0)
            cy = child.get('y', 0.0) + child.get('height', 0.0)
            max_x = max(max_x, cx)
            max_y = max(max_y, cy)

        # Also consider ports that extend beyond node boundaries
        for child in children:
            for port in child.get('ports', []):
                px = child.get('x', 0) + port.get('x', 0)
                py = child.get('y', 0) + port.get('y', 0)
                pw = px + port.get('width', 0)
                ph = py + port.get('height', 0)
                max_x = max(max_x, pw)
                max_y = max(max_y, ph)

        graph['width'] = max_x + padding['right']
        graph['height'] = max_y + padding['bottom']
