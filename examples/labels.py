"""Node labels and label placement."""
import json
from elkpy import ELK

elk = ELK()

graph = {
    "id": "root",
    "layoutOptions": {
        "elk.algorithm": "layered",
        "elk.direction": "DOWN",
    },
    "children": [
        {
            "id": "n1",
            "width": 100,
            "height": 100,
            "labels": [
                {
                    "id": "n1_label",
                    "text": "Source",
                    # Placement is set on the label's own layoutOptions
                    "layoutOptions": {
                        "elk.nodeLabels.placement": "INSIDE V_CENTER H_CENTER",
                    },
                }
            ],
        },
        {
            "id": "n2",
            "width": 100,
            "height": 100,
            "labels": [
                {
                    "id": "n2_label",
                    "text": "Target",
                    "layoutOptions": {
                        "elk.nodeLabels.placement": "OUTSIDE V_TOP H_CENTER",
                    },
                }
            ],
        },
    ],
    "edges": [
        {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
    ],
}

result = elk.layout(graph)

for child in result["children"]:
    label = child["labels"][0]
    placement = label["layoutOptions"]["elk.nodeLabels.placement"]
    print(f"{child['id']} ({placement}):")
    print(f"  node at ({child['x']}, {child['y']})")
    print(f"  label at ({label.get('x', 'N/A')}, {label.get('y', 'N/A')})")
