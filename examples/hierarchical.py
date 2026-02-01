"""Hierarchical (nested) graph layout."""
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
            "id": "group1",
            "layoutOptions": {
                "elk.algorithm": "layered",
                "elk.direction": "DOWN",
                "elk.padding": "[left=20, top=20, right=20, bottom=20]",
            },
            "children": [
                {"id": "g1_n1", "width": 30, "height": 30},
                {"id": "g1_n2", "width": 30, "height": 30},
            ],
            "edges": [
                {"id": "g1_e1", "sources": ["g1_n1"], "targets": ["g1_n2"]},
            ],
        },
        {
            "id": "group2",
            "layoutOptions": {
                "elk.algorithm": "layered",
                "elk.padding": "[left=20, top=20, right=20, bottom=20]",
            },
            "children": [
                {"id": "g2_n1", "width": 30, "height": 30},
                {"id": "g2_n2", "width": 30, "height": 30},
            ],
            "edges": [
                {"id": "g2_e1", "sources": ["g2_n1"], "targets": ["g2_n2"]},
            ],
        },
    ],
    "edges": [
        {"id": "cross_e1", "sources": ["group1"], "targets": ["group2"]},
    ],
}

result = elk.layout(graph)
print(json.dumps(result, indent=2))
