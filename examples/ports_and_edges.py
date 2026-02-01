"""Using ports to control edge attachment points."""
import json
from elkpy import ELK

elk = ELK()

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
                {"id": "n1_p1", "layoutOptions": {"elk.port.side": "EAST"}},
                {"id": "n1_p2", "layoutOptions": {"elk.port.side": "EAST"}},
            ],
            "layoutOptions": {"elk.portConstraints": "FIXED_SIDE"},
        },
        {
            "id": "n2",
            "width": 50,
            "height": 30,
            "ports": [
                {"id": "n2_p1", "layoutOptions": {"elk.port.side": "WEST"}},
            ],
            "layoutOptions": {"elk.portConstraints": "FIXED_SIDE"},
        },
        {
            "id": "n3",
            "width": 50,
            "height": 30,
            "ports": [
                {"id": "n3_p1", "layoutOptions": {"elk.port.side": "WEST"}},
            ],
            "layoutOptions": {"elk.portConstraints": "FIXED_SIDE"},
        },
    ],
    "edges": [
        {
            "id": "e1",
            "sources": ["n1_p1"],
            "targets": ["n2_p1"],
        },
        {
            "id": "e2",
            "sources": ["n1_p2"],
            "targets": ["n3_p1"],
        },
    ],
}

result = elk.layout(graph)
print(json.dumps(result, indent=2))
