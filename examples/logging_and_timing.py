"""Using logging and execution time measurement."""
import json
from elkpy import ELK

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

result = elk.layout(graph, logging=True, measure_execution_time=True)

# The logging info is attached to the graph
logging_info = result.get("logging", {})
print(f"Execution time: {logging_info.get('executionTime', 0):.3f} ms")
print(f"Layout steps: {json.dumps(logging_info.get('children', []), indent=2)}")
