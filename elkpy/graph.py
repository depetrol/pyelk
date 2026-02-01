"""Graph validation and manipulation utilities for ELK."""
import copy
from typing import Dict, List, Optional, Tuple

from .exceptions import InvalidGraphException


def validate_id(element_id) -> str:
    """Validate and return a string ID. Accepts strings and integers."""
    if element_id is None:
        raise InvalidGraphException("Element ID is missing")
    if isinstance(element_id, bool):
        raise InvalidGraphException(f"Element ID must be a string or integer, got boolean")
    if isinstance(element_id, int):
        return str(element_id)
    if isinstance(element_id, float):
        if element_id != int(element_id):
            raise InvalidGraphException(f"Element ID must be integral, got {element_id}")
        return str(int(element_id))
    if isinstance(element_id, str):
        return element_id
    raise InvalidGraphException(f"Element ID must be a string or integer, got {type(element_id).__name__}")


def validate_graph(graph: dict) -> None:
    """Validate a graph structure, raising InvalidGraphException on errors."""
    if not isinstance(graph, dict):
        raise InvalidGraphException("Graph must be a dict")
    if 'id' not in graph:
        raise InvalidGraphException("Graph must have an 'id' field")
    validate_id(graph['id'])
    _validate_children(graph)


def _validate_children(node: dict) -> None:
    """Recursively validate children."""
    for child in node.get('children', []):
        if 'id' in child:
            validate_id(child['id'])
        _validate_children(child)


def deep_copy_graph(graph: dict) -> dict:
    """Deep copy a graph."""
    return copy.deepcopy(graph)


def normalize_edges(graph: dict) -> None:
    """Normalize edge formats: convert primitive edges to extended format."""
    for edge in graph.get('edges', []):
        _normalize_edge(edge)
    for child in graph.get('children', []):
        normalize_edges(child)


def _normalize_edge(edge: dict) -> None:
    """Convert a primitive edge (source/target) to extended format (sources/targets)."""
    if 'source' in edge and 'sources' not in edge:
        edge['sources'] = [edge['source']]
        source_port = edge.pop('sourcePort', None)
        if source_port:
            edge['sources'] = [source_port]
    if 'target' in edge and 'targets' not in edge:
        edge['targets'] = [edge['target']]
        target_port = edge.pop('targetPort', None)
        if target_port:
            edge['targets'] = [target_port]


def collect_nodes(graph: dict) -> Dict[str, dict]:
    """Collect all nodes by ID into a flat dict."""
    nodes = {}
    if 'id' in graph:
        nodes[str(graph['id'])] = graph
    for child in graph.get('children', []):
        nodes.update(collect_nodes(child))
    for port in graph.get('ports', []):
        if 'id' in port:
            nodes[str(port['id'])] = port
    return nodes


def collect_edges(graph: dict) -> List[dict]:
    """Collect all edges from a graph recursively."""
    edges = list(graph.get('edges', []))
    for child in graph.get('children', []):
        edges.extend(collect_edges(child))
    return edges


def set_defaults(node: dict) -> None:
    """Set default values for node dimensions."""
    node.setdefault('x', 0.0)
    node.setdefault('y', 0.0)
    node.setdefault('width', 0.0)
    node.setdefault('height', 0.0)


def compute_graph_size(graph: dict, padding: dict) -> None:
    """Compute the size of a graph based on its children and padding."""
    if not graph.get('children'):
        graph['width'] = padding['left'] + padding['right']
        graph['height'] = padding['top'] + padding['bottom']
        return

    max_x = 0.0
    max_y = 0.0
    for child in graph['children']:
        cx = child.get('x', 0.0) + child.get('width', 0.0)
        cy = child.get('y', 0.0) + child.get('height', 0.0)
        max_x = max(max_x, cx)
        max_y = max(max_y, cy)

    graph['width'] = max_x + padding['right']
    graph['height'] = max_y + padding['bottom']
