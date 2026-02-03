"""Comparing different layout algorithms on the same graph."""
import json
from pyelk import ELK

elk = ELK()

# A graph with 5 nodes and 6 edges
def make_graph(algorithm):
    return {
        "id": "root",
        "layoutOptions": {"elk.algorithm": algorithm},
        "children": [
            {"id": "n1", "width": 40, "height": 40},
            {"id": "n2", "width": 40, "height": 40},
            {"id": "n3", "width": 40, "height": 40},
            {"id": "n4", "width": 40, "height": 40},
            {"id": "n5", "width": 40, "height": 40},
        ],
        "edges": [
            {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
            {"id": "e2", "sources": ["n1"], "targets": ["n3"]},
            {"id": "e3", "sources": ["n2"], "targets": ["n4"]},
            {"id": "e4", "sources": ["n3"], "targets": ["n4"]},
            {"id": "e5", "sources": ["n4"], "targets": ["n5"]},
            {"id": "e6", "sources": ["n2"], "targets": ["n5"]},
        ],
    }

algorithms = [
    "layered",
    "stress",
    "force",
    "mrtree",
    "radial",
    "rectpacking",
]

for alg in algorithms:
    graph = make_graph(alg)
    result = elk.layout(graph)

    print(f"--- {alg} ---")
    for child in result["children"]:
        print(f"  {child['id']}: ({child['x']:.1f}, {child['y']:.1f})")
    print()
