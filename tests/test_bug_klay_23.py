"""Port of test-bug-klay-23.js - unspecified bendpoints."""
import pytest
from elkpy import ELK


SIMPLE_GRAPH = {
    "id": "root",
    "layoutOptions": {
        "elk.algorithm": "layered",
        "elk.layered.crossingMinimization.strategy": "INTERACTIVE",
    },
    "children": [
        {"id": "n1", "width": 10, "height": 10},
        {"id": "n2", "width": 10, "height": 10},
    ],
    "edges": [
        {
            "id": "e1",
            "sources": ["n1"],
            "targets": ["n2"],
        },
        {
            "id": "e2",
            "sources": ["n1"],
            "targets": ["n2"],
            "sections": [{
                "id": "es2",
                "startPoint": {"x": 0, "y": 0},
                "bendPoints": [{"x": 20, "y": 0}],
                "endPoint": {"x": 50, "y": 0},
            }],
        },
    ],
}


@pytest.fixture
def elk():
    return ELK()


class TestBugKlay23:
    """Regression test for klay#23 - unspecified bendpoints."""

    def test_should_be_fine_with_unspecified_bendpoints(self, elk):
        result = elk.layout(SIMPLE_GRAPH)
        assert result is not None
