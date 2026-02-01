"""Port of testIds.js - tests element ID validation."""
import pytest
from elkpy import ELK, InvalidGraphException


@pytest.fixture
def elk():
    return ELK()


class TestIDs:
    """Tests for ID validation in layout()."""

    def test_should_return_no_error_if_id_is_string(self, elk):
        result = elk.layout({"id": "x"})
        assert result is not None

    def test_should_return_no_error_if_id_is_integer(self, elk):
        result = elk.layout({"id": 2})
        assert result is not None

    def test_should_return_error_if_id_is_not_present(self, elk):
        with pytest.raises(InvalidGraphException):
            elk.layout({})

    def test_should_return_error_if_id_is_non_integral_number(self, elk):
        with pytest.raises(InvalidGraphException):
            elk.layout({"id": 1.2})

    def test_should_return_error_if_id_is_array(self, elk):
        with pytest.raises(InvalidGraphException):
            elk.layout({"id": []})

    def test_should_return_error_if_id_is_object(self, elk):
        with pytest.raises(InvalidGraphException):
            elk.layout({"id": {}})

    def test_should_return_error_if_id_is_boolean(self, elk):
        with pytest.raises(InvalidGraphException):
            elk.layout({"id": True})
