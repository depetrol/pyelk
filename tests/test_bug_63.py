"""Port of test-bug-63.js - COFFMAN_GRAHAM layering with self-loops."""
import pytest
from pyelk import ELK


@pytest.fixture
def elk():
    return ELK()


GRAPH = {
    "id": "root",
    "properties": {
        "algorithm": "layered",
        "layering.strategy": "COFFMAN_GRAHAM",
    },
    "children": [
        {"id": "n1", "width": 30, "height": 30},
        {"id": "n2", "width": 30, "height": 30},
        {"id": "n3", "width": 30, "height": 30},
    ],
    "edges": [
        {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
        {"id": "e2", "sources": ["n1"], "targets": ["n3"]},
        # This self-loop used to cause a stack overflow in <= 0.4.1
        {"id": "e3", "sources": ["n1"], "targets": ["n1"]},
    ],
}


class TestBug63:
    """Regression test for bug #63 - COFFMAN_GRAHAM with self-loops."""

    def test_coffman_graham_should_cope_with_selfloops(self, elk):
        result = elk.layout(GRAPH)
        assert result is not None
