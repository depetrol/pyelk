"""Main ELK class - the primary API for the elkpy library."""
import copy
import time
from typing import Any, Dict, List, Optional

from .exceptions import (
    ElkError, UnsupportedConfigurationException,
    UnsupportedGraphException, InvalidGraphException
)
from .graph import validate_graph, validate_id, normalize_edges, collect_nodes
from .options import (
    get_algorithm, get_option, resolve_algorithm, get_padding,
    get_effective_options, ALGORITHM_ALIASES
)
from .algorithms import get_layout_provider, ALGORITHM_REGISTRY


class ELK:
    """Main ELK layout engine.

    Provides graph layout functionality using various algorithms
    from the Eclipse Layout Kernel (ELK).

    Usage:
        elk = ELK()
        result = elk.layout(graph)

    Args:
        default_layout_options: Default layout options applied to all layouts.
        algorithms: List of algorithm IDs to register (for future use).
    """

    def __init__(self, default_layout_options: Optional[Dict[str, str]] = None,
                 algorithms: Optional[List[str]] = None):
        self.default_layout_options = default_layout_options or {}
        self.algorithms = algorithms or [
            'layered', 'stress', 'mrtree', 'radial', 'force',
            'disco', 'sporeOverlap', 'sporeCompaction', 'rectpacking'
        ]

    def layout(self, graph: dict = None, layout_options: Optional[Dict[str, str]] = None,
               logging: bool = False, measure_execution_time: bool = False) -> dict:
        """Perform layout on a graph.

        Args:
            graph: The graph to layout (modified in-place and returned).
            layout_options: Layout options for this specific layout call.
                These override the graph's own options but not concrete options
                set directly on elements.
            logging: If True, include logging information in the result.
            measure_execution_time: If True, include execution time measurement.

        Returns:
            The laid-out graph with computed coordinates.

        Raises:
            ValueError: If graph is missing.
            InvalidGraphException: If the graph structure is invalid.
            UnsupportedConfigurationException: If the configuration is unsupported.
        """
        if graph is None:
            raise ValueError("Missing mandatory parameter 'graph'.")

        # Clean up logging from previous runs
        graph.pop('logging', None)

        start_time = time.time() if measure_execution_time else None

        # Validate graph
        try:
            validate_graph(graph)
        except InvalidGraphException as e:
            raise e

        # Normalize edge formats
        normalize_edges(graph)

        # Merge options: default < global (layout_options) < element-specific
        # Global options from constructor default + per-call layout_options
        global_options = dict(self.default_layout_options)
        if layout_options:
            # Global options should NOT override element-specific options
            global_options.update(layout_options)

        # Layout the graph recursively
        log_data = {'name': 'Root', 'children': []} if logging else None

        try:
            self._layout_recursive(graph, global_options, log_data)
        except (UnsupportedConfigurationException, UnsupportedGraphException):
            raise
        except ElkError:
            raise
        except Exception as e:
            raise

        # Add logging info if requested
        if logging or measure_execution_time:
            logging_info = {}
            if logging and log_data:
                logging_info['name'] = log_data.get('name', 'Root')
                logging_info['children'] = log_data.get('children', [])
            if measure_execution_time and start_time is not None:
                elapsed = (time.time() - start_time) * 1000  # ms
                logging_info['executionTime'] = elapsed
            graph['logging'] = logging_info

        return graph

    def _layout_recursive(self, graph: dict, global_options: dict,
                          log_data: Optional[dict] = None) -> None:
        """Recursively layout a graph and its children."""
        eff_options = get_effective_options(graph, global_options)

        # Check for hierarchy handling
        hierarchy = eff_options.get('elk.hierarchyHandling') or eff_options.get(
            'hierarchyHandling') or 'SEPARATE_CHILDREN'

        # Check for cross-hierarchy edges
        if hierarchy == 'SEPARATE_CHILDREN':
            self._check_cross_hierarchy_edges(graph)

        # Layout children's sub-graphs first (bottom-up)
        for child in graph.get('children', []):
            if child.get('children'):
                if hierarchy == 'INCLUDE_CHILDREN':
                    # Include children in parent layout
                    pass
                else:
                    self._layout_recursive(child, global_options, log_data)

        # Get the algorithm for this graph level
        alg_id = get_algorithm(graph, global_options)

        # Check if algorithm exists
        provider = get_layout_provider(alg_id)
        if provider is None:
            raise UnsupportedConfigurationException(
                f"No layout algorithm with id '{alg_id}' is known.")

        # Add log entry
        if log_data is not None:
            child_log = {
                'name': f'{alg_id} on {graph.get("id", "?")}',
                'children': [],
            }
            log_data['children'].append(child_log)

        # Run the layout
        provider.layout(graph, global_options)

        # For INCLUDE_CHILDREN: also layout child containers and their internal edges
        if hierarchy == 'INCLUDE_CHILDREN':
            self._layout_hierarchical_children(graph, global_options, provider)

    def _layout_hierarchical_children(self, graph: dict, global_options: dict,
                                       provider) -> None:
        """Handle hierarchical layout for child containers in INCLUDE_CHILDREN mode."""
        for child in graph.get('children', []):
            if child.get('children'):
                # Layout the child's internal graph
                provider.layout(child, global_options)
                # Route edges that reference the container
                self._route_container_edges(child, global_options)
                # Recurse
                self._layout_hierarchical_children(child, global_options, provider)

    def _route_container_edges(self, container: dict, global_options: dict) -> None:
        """Route edges within a container that may reference the container itself."""
        container_id = str(container.get('id', ''))
        node_map = {}
        # Collect all nodes and ports
        for child in container.get('children', []):
            node_map[str(child.get('id', ''))] = child
            for port in child.get('ports', []):
                node_map[str(port.get('id', ''))] = child  # map port to its owner node
        # Also map the container itself
        node_map[container_id] = container

        for edge in container.get('edges', []):
            if edge.get('sections'):
                continue  # already routed

            sources = edge.get('sources', [])
            targets = edge.get('targets', [])
            if not sources and 'source' in edge:
                sources = [str(edge['source'])]
            if not targets and 'target' in edge:
                targets = [str(edge['target'])]

            src_id = str(sources[0]) if sources else None
            tgt_id = str(targets[0]) if targets else None

            src_node = node_map.get(src_id) if src_id else None
            tgt_node = node_map.get(tgt_id) if tgt_id else None

            if src_node and tgt_node:
                sx = src_node.get('x', 0) + src_node.get('width', 0) / 2
                sy = src_node.get('y', 0) + src_node.get('height', 0) / 2
                tx = tgt_node.get('x', 0) + tgt_node.get('width', 0) / 2
                ty = tgt_node.get('y', 0) + tgt_node.get('height', 0) / 2

                edge['sections'] = [{
                    'id': str(edge.get('id', '')) + '_s0',
                    'startPoint': {'x': sx, 'y': sy},
                    'endPoint': {'x': tx, 'y': ty},
                }]

    def _check_cross_hierarchy_edges(self, graph: dict) -> None:
        """Check for edges that cross hierarchy boundaries in SEPARATE_CHILDREN mode."""
        children = graph.get('children', [])
        if not children:
            return

        # For each child container, check that its edges only reference
        # its own descendants (not itself or anything outside).
        for child in children:
            child_id = str(child.get('id', ''))

            # Collect IDs of strict descendants (children of this child, not the child itself)
            inner_ids = set()
            for grandchild in child.get('children', []):
                self._collect_descendant_ids(grandchild, inner_ids)
            # Include ports of the child (these are valid edge endpoints)
            for port in child.get('ports', []):
                pid = port.get('id')
                if pid is not None:
                    inner_ids.add(str(pid))

            for edge in child.get('edges', []):
                sources = edge.get('sources', [])
                targets = edge.get('targets', [])
                if not sources and 'source' in edge:
                    sources = [edge['source']]
                if not targets and 'target' in edge:
                    targets = [edge['target']]

                for src in sources:
                    for tgt in targets:
                        src_str = str(src)
                        tgt_str = str(tgt)

                        # If either endpoint references the container itself
                        # or something outside the container, it's cross-hierarchy
                        if src_str == child_id or tgt_str == child_id:
                            raise UnsupportedGraphException(
                                f"Cross-hierarchy edge {edge.get('id', '')} "
                                f"references container node in SEPARATE_CHILDREN mode")
                        if src_str not in inner_ids or tgt_str not in inner_ids:
                            raise UnsupportedGraphException(
                                f"Cross-hierarchy edge {edge.get('id', '')} "
                                f"not supported in SEPARATE_CHILDREN mode")

            # Recurse into child's children
            self._check_cross_hierarchy_edges(child)

    def _collect_descendant_ids(self, node: dict, ids: set) -> None:
        """Collect all descendant IDs of a node."""
        nid = node.get('id')
        if nid is not None:
            ids.add(str(nid))
        for port in node.get('ports', []):
            pid = port.get('id')
            if pid is not None:
                ids.add(str(pid))
        for child in node.get('children', []):
            self._collect_descendant_ids(child, ids)

    def known_layout_algorithms(self) -> List[dict]:
        """Return descriptions of all known layout algorithms."""
        result = []
        for alg_id in ALGORITHM_REGISTRY:
            result.append({
                'id': alg_id,
                'name': alg_id.split('.')[-1],
                'description': f'Layout algorithm: {alg_id}',
            })
        return result

    def known_layout_options(self) -> List[dict]:
        """Return descriptions of all known layout options."""
        from .options import DEFAULTS
        result = []
        for key, val in DEFAULTS.items():
            result.append({
                'id': key,
                'name': key,
                'type': type(val).__name__,
            })
        return result

    def known_layout_categories(self) -> List[dict]:
        """Return descriptions of layout categories."""
        return [
            {'id': 'org.eclipse.elk.layered', 'name': 'Layered',
             'knownLayouters': ['org.eclipse.elk.layered']},
            {'id': 'org.eclipse.elk.force', 'name': 'Force',
             'knownLayouters': ['org.eclipse.elk.force', 'org.eclipse.elk.stress']},
            {'id': 'org.eclipse.elk.tree', 'name': 'Tree',
             'knownLayouters': ['org.eclipse.elk.mrtree']},
        ]
