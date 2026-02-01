"""Port of testRaiseException.js - tests exception handling."""
import pytest
from elkpy import ELK, UnsupportedConfigurationException


class TestExceptions:
    """Tests for exception handling."""

    def test_should_report_unsupported_configuration(self):
        elk = ELK()
        # A simple cycle where all nodes have FIRST layer constraint
        graph = {
            "id": "root",
            "properties": {"algorithm": "layered"},
            "children": [
                {"id": "n1", "width": 30, "height": 30,
                 "layoutOptions": {"layerConstraint": "FIRST"}},
                {"id": "n2", "width": 30, "height": 30,
                 "layoutOptions": {"layerConstraint": "FIRST"}},
                {"id": "n3", "width": 30, "height": 30,
                 "layoutOptions": {"layerConstraint": "FIRST"}},
            ],
            "edges": [
                {"id": "e1", "sources": ["n1"], "targets": ["n2"]},
                {"id": "e2", "sources": ["n2"], "targets": ["n3"]},
                {"id": "e3", "sources": ["n3"], "targets": ["n1"]},
            ],
        }
        with pytest.raises(UnsupportedConfigurationException) as exc_info:
            elk.layout(graph)
        assert "org.eclipse.elk.core.UnsupportedConfigurationException" in str(exc_info.value)
