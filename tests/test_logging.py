"""Port of testLogging.js - tests logging and execution time measurement."""
import copy
import pytest
from elkpy import ELK


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


class TestLogging:
    """Tests for logging and execution time measurement."""

    def test_should_provide_logs_if_requested(self, elk):
        graph = fresh_graph()
        result = elk.layout(graph, layout_options={'algorithm': 'stress'},
                            logging=True)
        assert result.get('logging') is not None
        assert result['logging'].get('children') is not None
        assert result['logging'].get('executionTime') is None

    def test_should_not_provide_logs_if_not_requested(self, elk):
        graph = fresh_graph()
        result = elk.layout(graph, logging=False)
        assert result.get('logging') is None

    def test_should_provide_execution_times_if_requested(self, elk):
        graph = fresh_graph()
        result = elk.layout(graph, layout_options={'algorithm': 'layered'},
                            measure_execution_time=True)
        assert result.get('logging') is not None
        assert result['logging'].get('executionTime') is not None

    def test_should_not_provide_execution_times_if_not_requested(self, elk):
        graph = fresh_graph()
        result = elk.layout(graph, measure_execution_time=False)
        assert result.get('logging') is None

    def test_should_not_provide_logging_by_default(self, elk):
        graph = fresh_graph()
        result = elk.layout(graph)
        assert result.get('logging') is None

    def test_should_clear_logging_from_previous_run(self, elk):
        graph = fresh_graph()
        # First run with logging
        elk.layout(graph, logging=True)
        assert graph.get('logging') is not None

        # Second run without logging - should clear previous logging
        elk.layout(graph)
        assert graph.get('logging') is None
