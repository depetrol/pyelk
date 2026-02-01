"""Port of test-bug-klay-22.js - node label placement."""
import copy
import pytest
from elkpy import ELK


SIMPLE_GRAPH = {
    "id": "root",
    "children": [
        {
            "id": "n1", "width": 100, "height": 100,
            "labels": [{"id": "l1", "text": "Label1"}],
        },
        {
            "id": "n2", "width": 100, "height": 100,
            "labels": [{
                "id": "l2",
                "text": "Label2",
                "layoutOptions": {
                    "elk.nodeLabels.placement": "INSIDE V_CENTER H_CENTER",
                },
            }],
        },
    ],
    "edges": [
        {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
    ],
}


@pytest.fixture
def elk():
    return ELK()


class TestBugKlay22:
    """Regression test for klay#22 - node label placement."""

    def test_should_place_labels_according_to_set_options(self, elk):
        graph = copy.deepcopy(SIMPLE_GRAPH)
        result = elk.layout(graph, layout_options={
            'elk.nodeLabels.placement': 'OUTSIDE V_TOP H_CENTER',
        })
        # OUTSIDE V_TOP H_CENTER
        assert result['children'][0]['labels'][0]['x'] == 50
        assert result['children'][0]['labels'][0]['y'] == -5
        # INSIDE V_CENTER H_CENTER
        assert result['children'][1]['labels'][0]['x'] == 50
        assert result['children'][1]['labels'][0]['y'] == 50
