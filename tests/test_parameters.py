"""Port of testParameters.js - tests parameter validation."""
import pytest
from elkpy import ELK


@pytest.fixture
def elk():
    return ELK()


class TestParameters:
    """Tests for layout() parameter validation."""

    def test_should_reject_if_graph_is_missing(self, elk):
        with pytest.raises(ValueError):
            elk.layout()

    def test_should_succeed_if_graph_is_specified(self, elk):
        result = elk.layout({"id": 2})
        assert result is not None
