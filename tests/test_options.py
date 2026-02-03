"""Port of testOptions.js - tests layout options parsing and application."""
import copy
import pytest
from pyelk import ELK, UnsupportedConfigurationException


SIMPLE_GRAPH = {
    "id": "root",
    "layoutOptions": {"elk.direction": "RIGHT"},
    "children": [
        {"id": "n1", "width": 10, "height": 10},
        {"id": "n2", "width": 10, "height": 10},
    ],
    "edges": [
        {"id": "e1", "sources": ["n1"], "targets": ["n2"]}
    ],
}


@pytest.fixture
def elk():
    return ELK()


def fresh_graph():
    return copy.deepcopy(SIMPLE_GRAPH)


class TestLayoutOptions:
    """Tests for layout option handling."""

    def test_should_respect_options(self, elk):
        graph = fresh_graph()
        result = elk.layout(graph, layout_options={
            'org.eclipse.elk.layered.spacing.nodeNodeBetweenLayers': 11
        })
        # left-to-right layout: same y, different x
        assert result['children'][0]['y'] == result['children'][1]['y']
        assert abs(result['children'][0]['x'] - result['children'][1]['x']) == 10 + 11

    def test_should_not_override_concrete_layout_options(self, elk):
        graph = fresh_graph()
        result = elk.layout(graph, layout_options={
            'org.eclipse.elk.direction': 'DOWN'
        })
        # Graph has elk.direction: RIGHT which should not be overridden
        assert result['layoutOptions']['elk.direction'] == 'RIGHT'
        assert abs(result['children'][0]['x'] - result['children'][1]['x']) > 0
        assert result['children'][0]['y'] == result['children'][1]['y']

    def test_should_correctly_parse_elk_padding(self, elk):
        padding_graph = {
            "id": "root",
            "layoutOptions": {"elk.padding": "[left=2, top=3, right=3, bottom=2]"},
            "children": [{"id": "n1", "width": 10, "height": 10}],
        }
        result = elk.layout(padding_graph)
        assert result['children'][0]['x'] == 2
        assert result['children'][0]['y'] == 3
        assert result['width'] == 15
        assert result['height'] == 15

    def test_should_correctly_parse_kvector(self, elk):
        kvector_graph = {
            "id": "root",
            "children": [{
                "id": "n1", "width": 10, "height": 10,
                "layoutOptions": {"position": "(23, 43)"},
            }],
        }
        result = elk.layout(kvector_graph, layout_options={"algorithm": "fixed"})
        assert result['children'][0]['x'] == 23
        assert result['children'][0]['y'] == 43

    def test_should_correctly_parse_kvector_chain(self, elk):
        kvectorchain_graph = {
            "id": "root",
            "children": [
                {"id": "n1", "width": 10, "height": 10},
                {"id": "n2", "width": 10, "height": 10},
            ],
            "edges": [{
                "id": "e1",
                "sources": ["n1"],
                "targets": ["n2"],
                "layoutOptions": {"bendPoints": "( {1,2}, {3,4} )"},
            }],
        }
        result = elk.layout(kvectorchain_graph, layout_options={"algorithm": "fixed"})
        assert result['edges'][0]['sections'][0]['startPoint']['x'] == 1
        assert result['edges'][0]['sections'][0]['startPoint']['y'] == 2
        assert result['edges'][0]['sections'][0]['endPoint']['x'] == 3
        assert result['edges'][0]['sections'][0]['endPoint']['y'] == 4

    def test_should_raise_exception_for_invalid_layouter_id(self, elk):
        graph = {
            "id": "root",
            "children": [{"id": "n1", "width": 10, "height": 10}],
            "layoutOptions": {"algorithm": "foo.bar.baz"},
        }
        with pytest.raises(UnsupportedConfigurationException) as exc_info:
            elk.layout(graph)
        assert "org.eclipse.elk.core.UnsupportedConfigurationException" in str(exc_info.value)

    def test_should_default_to_elk_layered(self, elk):
        graph = {
            "id": "root",
            "children": [{"id": "n1", "width": 10, "height": 10}],
            "layoutOptions": {},
        }
        # Should not raise an exception
        result = elk.layout(graph)
        assert result is not None


class TestGlobalLayoutOptions:
    """Tests for global default layout options."""

    def test_should_respect_global_layout(self):
        elk = ELK(default_layout_options={
            'elk.layered.spacing.nodeNodeBetweenLayers': 33
        })
        graph = fresh_graph()
        result = elk.layout(graph)
        # left-to-right layout: same y, x difference = node_width + spacing
        assert result['children'][0]['y'] == result['children'][1]['y']
        assert abs(result['children'][0]['x'] - result['children'][1]['x']) == 10 + 33
