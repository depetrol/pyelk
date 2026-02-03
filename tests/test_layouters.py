"""Port of testLayouters.js - tests different layout algorithms."""
import copy
import pytest
from pyelk import ELK


GRAPH = {
    "id": "root",
    "children": [
        {"id": "n1", "x": 20, "y": 20, "width": 10, "height": 10},
        {"id": "n2", "x": 50, "y": 50, "width": 10, "height": 10},
    ],
    "edges": [{"id": "e1", "sources": ["n1"], "targets": ["n2"]}],
}

GRAPH_OVERLAPPING = {
    "id": "root",
    "children": [
        {"id": "n1", "x": 20, "y": 20, "width": 10, "height": 10},
        {"id": "n2", "x": 25, "y": 25, "width": 10, "height": 10},
    ],
    "edges": [{"id": "e1", "sources": ["n1"], "targets": ["n2"]}],
}


@pytest.fixture
def elk():
    return ELK()


class TestLayoutAlgorithms:
    """Tests for specific layout algorithms."""

    def test_spore_compaction(self, elk):
        graph = copy.deepcopy(GRAPH)
        result = elk.layout(graph, layout_options={
            'algorithm': 'elk.sporeCompaction',
            'elk.spacing.nodeNode': 14,
            'elk.padding': '[left=2, top=2, right=2, bottom=2]',
        })
        assert result['children'][0]['x'] == 2
        assert result['children'][0]['y'] == 2
        assert result['children'][1]['x'] == 26
        assert result['children'][1]['y'] == 26

    def test_spore_overlap_removal(self, elk):
        graph = copy.deepcopy(GRAPH_OVERLAPPING)
        result = elk.layout(graph, layout_options={
            'algorithm': 'elk.sporeOverlap',
            'elk.spacing.nodeNode': 13,
            'elk.padding': '[left=3, top=3, right=3, bottom=3]',
        })
        assert result['children'][0]['x'] == 3
        assert result['children'][0]['y'] == 3
        assert result['children'][1]['x'] == 26
        assert result['children'][1]['y'] == 26

    def test_rectangle_packing(self, elk):
        graph = copy.deepcopy(GRAPH_OVERLAPPING)
        result = elk.layout(graph, layout_options={
            'algorithm': 'elk.rectpacking',
        })
        assert result is not None
