"""Basic pyelk usage - lay out a simple graph."""
import json
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
print(json.dumps(result, indent=2))
