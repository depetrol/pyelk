# pyelk

A pure Python port of [elkjs](https://github.com/kieler/elkjs) - automatic graph layout based on the [Eclipse Layout Kernel (ELK)](https://www.eclipse.org/elk/).

pyelk computes positions for nodes, edges, ports, and labels in a graph. It is not a diagramming framework itself - it only calculates coordinates. You can use these coordinates with any rendering library (matplotlib, SVG, HTML canvas, etc.).

## Installation

```bash
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from pyelk import ELK

elk = ELK()

graph = {
    "id": "root",
    "layoutOptions": {"elk.algorithm": "layered"},
    "children": [
        {"id": "n1", "width": 30, "height": 30},
        {"id": "n2", "width": 30, "height": 30},
        {"id": "n3", "width": 30, "height": 30},
    ],
    "edges": [
        {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
        {"id": "e2", "sources": ["n1"], "targets": ["n3"]},
    ],
}

result = elk.layout(graph)

for child in result["children"]:
    print(f"{child['id']}: x={child['x']}, y={child['y']}")
```

Output:

```
n1: x=37.0, y=12.0
n2: x=12.0, y=62.0
n3: x=62.0, y=62.0
```

## Graph Format

pyelk uses the [ELK JSON format](https://www.eclipse.org/elk/documentation/tooldevelopers/graphdatastructure/jsonformat.html). A graph is a Python dictionary with the following structure:

```python
graph = {
    "id": "root",                          # required: unique identifier
    "layoutOptions": { ... },              # optional: layout configuration
    "children": [                          # optional: list of nodes
        {
            "id": "node1",
            "width": 50,                   # node width in pixels
            "height": 30,                  # node height in pixels
            "ports": [ ... ],              # optional: connection points
            "labels": [ ... ],             # optional: text labels
            "children": [ ... ],           # optional: nested sub-graph
            "edges": [ ... ],              # optional: edges within this node
            "layoutOptions": { ... },      # optional: node-specific options
        },
    ],
    "edges": [                             # optional: connections
        {
            "id": "edge1",
            "sources": ["node1"],          # source node/port IDs
            "targets": ["node2"],          # target node/port IDs
        },
    ],
}
```

### Edge Formats

pyelk supports two edge formats:

**Extended format** (recommended):
```python
{"id": "e1", "sources": ["n1"], "targets": ["n2"]}
```

**Primitive format** (also supported):
```python
{"id": "e1", "source": "n1", "target": "n2"}
```

## Layout Algorithms

pyelk includes the following layout algorithms:

| Algorithm | ID | Description |
|---|---|---|
| Layered | `layered` | Sugiyama-style layered layout. Best for directed graphs with inherent flow. |
| Stress | `stress` | Stress minimization (Kamada-Kawai). Good for general undirected graphs. |
| Force | `force` | Force-directed (Fruchterman-Reingold). General-purpose spring-based layout. |
| MrTree | `mrtree` | Hierarchical tree layout for tree-structured graphs. |
| Radial | `radial` | Concentric circle layout based on graph distance. |
| Rectangle Packing | `rectpacking` | Packs nodes into a compact rectangular area. |
| SPOrE Compaction | `sporeCompaction` | Compacts nodes toward center while maintaining spacing. |
| SPOrE Overlap | `sporeOverlap` | Removes node overlaps while preserving relative positions. |
| Fixed | `fixed` | Positions nodes at explicitly specified coordinates. |

Set the algorithm via `layoutOptions`:

```python
graph = {
    "id": "root",
    "layoutOptions": {"elk.algorithm": "stress"},
    "children": [ ... ],
    "edges": [ ... ],
}
```

You can use either short names (`"layered"`) or fully qualified names (`"org.eclipse.elk.layered"`).

## Layout Options

Layout options control how the algorithm positions elements. They can be set at three levels, from lowest to highest priority:

### 1. Constructor Defaults

Applied to every `layout()` call:

```python
elk = ELK(default_layout_options={
    "elk.algorithm": "layered",
    "elk.direction": "RIGHT",
})
```

### 2. Per-Call Options

Override constructor defaults for a single call:

```python
result = elk.layout(graph, layout_options={
    "elk.direction": "DOWN",
})
```

### 3. Element-Specific Options

Set directly on a graph element. These have the highest priority:

```python
graph = {
    "id": "root",
    "layoutOptions": {
        "elk.algorithm": "layered",
        "elk.direction": "DOWN",
    },
    "children": [ ... ],
}
```

### Common Options

| Option | Default | Description |
|---|---|---|
| `elk.algorithm` | `layered` | Layout algorithm to use |
| `elk.direction` | `DOWN` | Layout direction: `UP`, `DOWN`, `LEFT`, `RIGHT` |
| `elk.spacing.nodeNode` | `20` | Minimum spacing between nodes |
| `elk.padding` | `[left=12, top=12, right=12, bottom=12]` | Padding inside the graph container |
| `elk.portConstraints` | `UNDEFINED` | Port constraint level: `UNDEFINED`, `FREE`, `FIXED_SIDE`, `FIXED_ORDER`, `FIXED_POS` |
| `elk.hierarchyHandling` | `SEPARATE_CHILDREN` | How to handle nested graphs: `SEPARATE_CHILDREN` or `INCLUDE_CHILDREN` |
| `elk.layered.layering.strategy` | `LONGEST_PATH` | Layer assignment strategy: `LONGEST_PATH`, `NETWORK_SIMPLEX`, `COFFMAN_GRAHAM` |

For a full list of options, see the [ELK reference documentation](https://www.eclipse.org/elk/reference.html).

## Ports

Ports are explicit attachment points on a node's border where edges connect:

```python
graph = {
    "id": "root",
    "layoutOptions": {
        "elk.algorithm": "layered",
        "elk.direction": "RIGHT",
    },
    "children": [
        {
            "id": "n1",
            "width": 50,
            "height": 50,
            "ports": [
                {"id": "n1_out", "layoutOptions": {"elk.port.side": "EAST"}},
            ],
            "layoutOptions": {"elk.portConstraints": "FIXED_SIDE"},
        },
        {
            "id": "n2",
            "width": 50,
            "height": 30,
            "ports": [
                {"id": "n2_in", "layoutOptions": {"elk.port.side": "WEST"}},
            ],
            "layoutOptions": {"elk.portConstraints": "FIXED_SIDE"},
        },
    ],
    "edges": [
        {"id": "e1", "sources": ["n1_out"], "targets": ["n2_in"]},
    ],
}
```

After layout, each port will have computed `x` and `y` coordinates relative to its parent node.

## Labels

Labels are text elements attached to nodes. Placement is controlled via the `elk.nodeLabels.placement` option set on the label's own `layoutOptions`:

```python
{
    "id": "n1",
    "width": 100,
    "height": 100,
    "labels": [
        {
            "id": "n1_label",
            "text": "My Node",
            "layoutOptions": {
                "elk.nodeLabels.placement": "INSIDE V_CENTER H_CENTER",
            },
        }
    ],
}
```

Placement values combine position keywords:
- Location: `INSIDE` or `OUTSIDE`
- Vertical: `V_TOP`, `V_CENTER`, `V_BOTTOM`
- Horizontal: `H_LEFT`, `H_CENTER`, `H_RIGHT`

You can also set placement as a global layout option to apply to all labels that don't specify their own:

```python
result = elk.layout(graph, layout_options={
    "elk.nodeLabels.placement": "OUTSIDE V_TOP H_CENTER",
})
```

## Hierarchical Graphs

Graphs can be nested - a node can contain its own children and edges:

```python
graph = {
    "id": "root",
    "layoutOptions": {"elk.algorithm": "layered", "elk.direction": "RIGHT"},
    "children": [
        {
            "id": "group1",
            "layoutOptions": {
                "elk.algorithm": "layered",
                "elk.direction": "DOWN",
                "elk.padding": "[left=20, top=20, right=20, bottom=20]",
            },
            "children": [
                {"id": "a", "width": 30, "height": 30},
                {"id": "b", "width": 30, "height": 30},
            ],
            "edges": [
                {"id": "e_ab", "sources": ["a"], "targets": ["b"]},
            ],
        },
        {
            "id": "group2",
            "children": [
                {"id": "c", "width": 30, "height": 30},
            ],
        },
    ],
    "edges": [
        {"id": "e_groups", "sources": ["group1"], "targets": ["group2"]},
    ],
}
```

By default, each level of the hierarchy is laid out independently (`SEPARATE_CHILDREN`). The inner graphs are laid out first (bottom-up), then the outer graph treats the containers as single nodes.

## Logging and Execution Time

You can enable logging and execution time measurement:

```python
result = elk.layout(graph, logging=True, measure_execution_time=True)

info = result["logging"]
print(f"Execution time: {info['executionTime']:.3f} ms")
print(f"Steps: {info['children']}")
```

## API Reference

### `ELK(default_layout_options=None, algorithms=None)`

Creates a new layout engine instance.

- `default_layout_options` (dict): Default options for all `layout()` calls.
- `algorithms` (list): List of algorithm IDs to register (for informational purposes).

### `elk.layout(graph, layout_options=None, logging=False, measure_execution_time=False)`

Performs layout on a graph.

- `graph` (dict): The graph in ELK JSON format. Modified in-place and returned.
- `layout_options` (dict): Per-call layout options that override constructor defaults but not element-specific options.
- `logging` (bool): Attach logging information to the result.
- `measure_execution_time` (bool): Measure and attach execution time (in milliseconds).
- Returns: The laid-out graph with computed `x`, `y` coordinates on all elements.
- Raises: `ValueError`, `InvalidGraphException`, `UnsupportedConfigurationException`.

### `elk.known_layout_algorithms()`

Returns a list of dicts describing available algorithms, each with `id`, `name`, and `description`.

### `elk.known_layout_options()`

Returns a list of dicts describing known options, each with `id`, `name`, and `type`.

### `elk.known_layout_categories()`

Returns a list of algorithm categories.

## Differences from elkjs

- **Synchronous API**: pyelk's `layout()` returns the result directly instead of a Promise. No web workers are needed.
- **Pure Python**: No JavaScript runtime, GWT compilation, or external dependencies required.
- **Same graph format**: Uses the same ELK JSON format as elkjs, so graphs are interchangeable.
- **Same layout options**: All ELK layout option keys work the same way.

## Examples

See the [`examples/`](examples/) directory for runnable scripts:

- [`basic.py`](examples/basic.py) - Simple graph layout
- [`algorithms.py`](examples/algorithms.py) - Comparing different layout algorithms
- [`ports_and_edges.py`](examples/ports_and_edges.py) - Ports and directed edges
- [`labels.py`](examples/labels.py) - Node label placement
- [`hierarchical.py`](examples/hierarchical.py) - Nested/hierarchical graphs
- [`layout_options.py`](examples/layout_options.py) - Option priority and customization
- [`logging_and_timing.py`](examples/logging_and_timing.py) - Logging and execution time

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Acknowledgements
Thanks to the authors of [ELK](https://eclipse.dev/elk/) and [elkjs](https://github.com/kieler/elkjs) for their implementations as reference. Thanks to [claude-code](https://github.com/anthropics/claude-code) for helping with the Python implementation.

## License

EPL-2.0 (same as ELK)
