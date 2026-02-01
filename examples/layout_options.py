"""Demonstrating layout options: constructor defaults, per-call options,
and element-specific options."""
import json
from elkpy import ELK

# Constructor-level defaults apply to every layout call
elk = ELK(default_layout_options={
    "elk.algorithm": "layered",
    "elk.direction": "RIGHT",
    "elk.spacing.nodeNode": "30",
})

graph = {
    "id": "root",
    "children": [
        {"id": "n1", "width": 30, "height": 30},
        {"id": "n2", "width": 30, "height": 30},
        {"id": "n3", "width": 30, "height": 30},
    ],
    "edges": [
        {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
        {"id": "e2", "sources": ["n2"], "targets": ["n3"]},
    ],
}

# Layout with constructor defaults (RIGHT direction, 30px spacing)
result = elk.layout(graph)
print("With constructor defaults (RIGHT, spacing=30):")
for c in result["children"]:
    print(f"  {c['id']}: ({c['x']:.1f}, {c['y']:.1f})")

# Per-call options override constructor defaults
graph2 = {
    "id": "root",
    "children": [
        {"id": "n1", "width": 30, "height": 30},
        {"id": "n2", "width": 30, "height": 30},
        {"id": "n3", "width": 30, "height": 30},
    ],
    "edges": [
        {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
        {"id": "e2", "sources": ["n2"], "targets": ["n3"]},
    ],
}

result2 = elk.layout(graph2, layout_options={"elk.direction": "DOWN"})
print("\nWith per-call override (DOWN):")
for c in result2["children"]:
    print(f"  {c['id']}: ({c['x']:.1f}, {c['y']:.1f})")

# Element-specific options override everything
graph3 = {
    "id": "root",
    "layoutOptions": {"elk.direction": "DOWN"},
    "children": [
        {"id": "n1", "width": 30, "height": 30},
        {"id": "n2", "width": 30, "height": 30},
        {"id": "n3", "width": 30, "height": 30},
    ],
    "edges": [
        {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
        {"id": "e2", "sources": ["n2"], "targets": ["n3"]},
    ],
}

result3 = elk.layout(graph3)
print("\nWith element-specific layoutOptions (DOWN):")
for c in result3["children"]:
    print(f"  {c['id']}: ({c['x']:.1f}, {c['y']:.1f})")
