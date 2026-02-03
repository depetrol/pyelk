"""Port of test-bug-8.js - tests hierarchical layouts with edge sections."""
import copy
import pytest
from pyelk import ELK, UnsupportedGraphException


GRAPH = {
    "id": "root",
    "children": [
        {
            "id": "A",
            "children": [
                {"id": "a1"},
                {"id": "a2"},
                {"id": "$generated_A_initial_0"},
            ],
            "edges": [{"id": "a1:0", "sources": ["a1"], "targets": ["A"]}],
        },
        {"id": "$generated_root_initial_0"},
    ],
}

GRAPH_PRIMITIVE_EDGE_FORMAT = {
    "id": "root",
    "children": [
        {
            "id": "A",
            "children": [
                {"id": "a1"},
                {"id": "a2"},
                {"id": "$generated_A_initial_0"},
            ],
            "edges": [{"id": "a1:0", "source": "a1", "target": "A"}],
        },
        {"id": "$generated_root_initial_0"},
    ],
}


@pytest.fixture
def elk():
    return ELK()


class TestBug8:
    """Regression tests for bug #8 - hierarchical layout edge sections."""

    def test_should_not_add_edge_sections_for_simple_bottom_up_layout(self, elk):
        graph = copy.deepcopy(GRAPH)
        with pytest.raises(UnsupportedGraphException) as exc_info:
            elk.layout(graph, layout_options={'hierarchyHandling': 'SEPARATE_CHILDREN'})
        assert "org.eclipse.elk.core.UnsupportedGraphException" in str(exc_info.value)

    def test_should_not_add_edge_sections_for_bottom_up_primitive_format(self, elk):
        graph = copy.deepcopy(GRAPH_PRIMITIVE_EDGE_FORMAT)
        with pytest.raises(UnsupportedGraphException) as exc_info:
            elk.layout(graph, layout_options={'hierarchyHandling': 'SEPARATE_CHILDREN'})
        assert "org.eclipse.elk.core.UnsupportedGraphException" in str(exc_info.value)

    def test_should_add_edge_sections_for_hierarchical_layout(self, elk):
        graph = copy.deepcopy(GRAPH)
        result = elk.layout(graph, layout_options={
            'hierarchyHandling': 'INCLUDE_CHILDREN'
        })
        edge_sections = result['children'][0]['edges'][0].get('sections')
        assert edge_sections is not None
        assert len(edge_sections) == 1
        assert 'startPoint' in edge_sections[0]
        assert 'endPoint' in edge_sections[0]

    def test_should_add_edge_sections_for_hierarchical_primitive_format(self, elk):
        graph = copy.deepcopy(GRAPH_PRIMITIVE_EDGE_FORMAT)
        result = elk.layout(graph, layout_options={
            'hierarchyHandling': 'INCLUDE_CHILDREN'
        })
        edge_sections = result['children'][0]['edges'][0].get('sections')
        assert edge_sections is not None
        assert len(edge_sections) == 1
        assert 'startPoint' in edge_sections[0]
        assert 'endPoint' in edge_sections[0]
