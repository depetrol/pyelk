"""Port of test-bug-7.js - regression test for bug #7 (large graph with ports)."""
import pytest
from pyelk import ELK


@pytest.fixture
def elk():
    return ELK()


GRAPH = {
    "id": "root",
    "children": [
        {
            "id": "57da8b44fffd97e2179faa24", "width": 174, "height": 80,
            "ports": [{"id": "57da8b44fffd97e2179faa24_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {"id": "57da8b5efffd97e2179fb9d9", "width": 232, "height": 80},
        {
            "id": "57da7b5dfffd97e2179e06df", "width": 165, "height": 80,
            "ports": [
                {"id": "57da7b5dfffd97e2179e06df_0", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "0"}},
                {"id": "57da7b5dfffd97e2179e06df_1", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "1"}},
            ],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da78b9fffd97e2179de456", "width": 165, "height": 80,
            "ports": [
                {"id": "57da78b9fffd97e2179de456_0", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "0"}},
                {"id": "57da78b9fffd97e2179de456_1", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "1"}},
            ],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7725fffd97e2179dda52", "width": 232, "height": 80,
            "ports": [{"id": "57da7725fffd97e2179dda52_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da80bcfffd97e2179ecfcc", "width": 165, "height": 80,
            "ports": [
                {"id": "57da80bcfffd97e2179ecfcc_0", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "0"}},
                {"id": "57da80bcfffd97e2179ecfcc_1", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "1"}},
            ],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7be7fffd97e2179e1aab", "width": 174, "height": 80,
            "ports": [{"id": "57da7be7fffd97e2179e1aab_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7a5efffd97e2179dfcc3", "width": 174, "height": 80,
            "ports": [{"id": "57da7a5efffd97e2179dfcc3_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {"id": "57da75fdfffd97e2179dd20a", "width": 232, "height": 80},
        {
            "id": "57da8b77fffd97e2179fc13f", "width": 188, "height": 80,
            "ports": [
                {"id": "57da8b77fffd97e2179fc13f_0", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "0"}},
                {"id": "57da8b77fffd97e2179fc13f_1", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "1"}},
            ],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "581b09ebfffd970e5c907418", "width": 292, "height": 80,
            "ports": [{"id": "581b09ebfffd970e5c907418_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da8a27fffd97e2179f4546", "width": 194, "height": 80,
            "ports": [{"id": "57da8a27fffd97e2179f4546_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da79b5fffd97e2179dedc6", "width": 165, "height": 80,
            "ports": [
                {"id": "57da79b5fffd97e2179dedc6_0", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "0"}},
                {"id": "57da79b5fffd97e2179dedc6_1", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "1"}},
            ],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da87fbfffd97e2179ef368", "width": 174, "height": 80,
            "ports": [{"id": "57da87fbfffd97e2179ef368_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7827fffd97e2179ddf9a", "width": 294, "height": 80,
            "ports": [{"id": "57da7827fffd97e2179ddf9a_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da79f7fffd97e2179df786", "width": 167, "height": 80,
            "ports": [{"id": "57da79f7fffd97e2179df786_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7babfffd97e2179e1374", "width": 167, "height": 80,
            "ports": [{"id": "57da7babfffd97e2179e1374_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7920fffd97e2179de7aa", "width": 254, "height": 80,
            "ports": [{"id": "57da7920fffd97e2179de7aa_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7aa8fffd97e2179e001f", "width": 246, "height": 80,
            "ports": [{"id": "57da7aa8fffd97e2179e001f_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da8aacfffd97e2179f53be", "width": 165, "height": 80,
            "ports": [
                {"id": "57da8aacfffd97e2179f53be_0", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "0"}},
                {"id": "57da8aacfffd97e2179f53be_1", "width": 18, "height": 18,
                 "properties": {"port.side": "NORTH", "port.index": "1"}},
            ],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da8bcafffd97e2179ffd5e", "width": 174, "height": 80,
            "ports": [{"id": "57da8bcafffd97e2179ffd5e_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7f59fffd97e2179ebf83", "width": 233, "height": 80,
            "ports": [{"id": "57da7f59fffd97e2179ebf83_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7634fffd97e2179dd89a", "width": 187, "height": 80,
            "ports": [{"id": "57da7634fffd97e2179dd89a_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "581b0995fffd970e5c9061d9", "width": 313, "height": 80,
            "ports": [{"id": "581b0995fffd970e5c9061d9_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da8115fffd97e2179eea72", "width": 167, "height": 80,
            "ports": [{"id": "57da8115fffd97e2179eea72_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da8b03fffd97e2179f6a93", "width": 167, "height": 80,
            "ports": [{"id": "57da8b03fffd97e2179f6a93_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da9b1ffffd97e217a2b164", "width": 168, "height": 80,
            "ports": [{"id": "57da9b1ffffd97e217a2b164_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da7776fffd97e2179ddbce", "width": 273, "height": 80,
            "ports": [{"id": "57da7776fffd97e2179ddbce_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
        {
            "id": "57da9b3ffffd97e217a2c5b0", "width": 463, "height": 80,
            "ports": [{"id": "57da9b3ffffd97e217a2c5b0_0", "width": 18, "height": 18,
                        "properties": {"port.side": "NORTH", "port.index": "0"}}],
            "properties": {"portConstraints": "FIXED_ORDER"}
        },
    ],
    "edges": [
        {"id": "e1", "sources": ["57da8b44fffd97e2179faa24"], "targets": ["57da8b77fffd97e2179fc13f_0"]},
        {"id": "e2", "sources": ["57da8b5efffd97e2179fb9d9"], "targets": ["57da8b77fffd97e2179fc13f_1"]},
        {"id": "e3", "sources": ["57da7b5dfffd97e2179e06df"], "targets": ["57da7babfffd97e2179e1374_0"]},
        {"id": "e4", "sources": ["57da78b9fffd97e2179de456"], "targets": ["57da79b5fffd97e2179dedc6_0"]},
        {"id": "e5", "sources": ["57da7725fffd97e2179dda52"], "targets": ["57da7776fffd97e2179ddbce_0"]},
        {"id": "e6", "sources": ["57da80bcfffd97e2179ecfcc"], "targets": ["57da8115fffd97e2179eea72_0"]},
        {"id": "e7", "sources": ["57da7be7fffd97e2179e1aab"], "targets": ["57da80bcfffd97e2179ecfcc_0"]},
        {"id": "e8", "sources": ["57da7a5efffd97e2179dfcc3"], "targets": ["57da7b5dfffd97e2179e06df_0"]},
        {"id": "e9", "sources": ["57da75fdfffd97e2179dd20a"], "targets": ["57da7634fffd97e2179dd89a_0"]},
        {"id": "e10", "sources": ["57da75fdfffd97e2179dd20a"], "targets": ["57da7725fffd97e2179dda52_0"]},
        {"id": "e11", "sources": ["57da75fdfffd97e2179dd20a"], "targets": ["57da7920fffd97e2179de7aa_0"]},
        {"id": "e12", "sources": ["57da75fdfffd97e2179dd20a"], "targets": ["57da7aa8fffd97e2179e001f_0"]},
        {"id": "e13", "sources": ["57da75fdfffd97e2179dd20a"], "targets": ["57da7f59fffd97e2179ebf83_0"]},
        {"id": "e14", "sources": ["57da75fdfffd97e2179dd20a"], "targets": ["57da8a27fffd97e2179f4546_0"]},
        {"id": "e15", "sources": ["57da8b77fffd97e2179fc13f"], "targets": ["57da8bcafffd97e2179ffd5e_0"]},
        {"id": "e16", "sources": ["581b09ebfffd970e5c907418"], "targets": ["581b0995fffd970e5c9061d9_0"]},
        {"id": "e17", "sources": ["57da8a27fffd97e2179f4546"], "targets": ["57da8aacfffd97e2179f53be_1"]},
        {"id": "e18", "sources": ["57da79b5fffd97e2179dedc6"], "targets": ["57da79f7fffd97e2179df786_0"]},
        {"id": "e19", "sources": ["57da87fbfffd97e2179ef368"], "targets": ["57da8aacfffd97e2179f53be_0"]},
        {"id": "e20", "sources": ["57da7827fffd97e2179ddf9a"], "targets": ["57da78b9fffd97e2179de456_1"]},
        {"id": "e21", "sources": ["57da79f7fffd97e2179df786"], "targets": ["57da7a5efffd97e2179dfcc3_0"]},
        {"id": "e22", "sources": ["57da7babfffd97e2179e1374"], "targets": ["57da7be7fffd97e2179e1aab_0"]},
        {"id": "e23", "sources": ["57da7920fffd97e2179de7aa"], "targets": ["57da79b5fffd97e2179dedc6_1"]},
        {"id": "e24", "sources": ["57da7aa8fffd97e2179e001f"], "targets": ["57da7b5dfffd97e2179e06df_1"]},
        {"id": "e25", "sources": ["57da8aacfffd97e2179f53be"], "targets": ["57da8b03fffd97e2179f6a93_0"]},
        {"id": "e26", "sources": ["57da8bcafffd97e2179ffd5e"], "targets": ["57da9b1ffffd97e217a2b164_0"]},
        {"id": "e27", "sources": ["57da8bcafffd97e2179ffd5e"], "targets": ["57da9b3ffffd97e217a2c5b0_0"]},
        {"id": "e28", "sources": ["57da8bcafffd97e2179ffd5e"], "targets": ["581b09ebfffd970e5c907418_0"]},
        {"id": "e29", "sources": ["57da7f59fffd97e2179ebf83"], "targets": ["57da80bcfffd97e2179ecfcc_1"]},
        {"id": "e30", "sources": ["57da7634fffd97e2179dd89a"], "targets": ["57da78b9fffd97e2179de456_0"]},
        {"id": "e31", "sources": ["57da8115fffd97e2179eea72"], "targets": ["57da87fbfffd97e2179ef368_0"]},
        {"id": "e32", "sources": ["57da8b03fffd97e2179f6a93"], "targets": ["57da8b44fffd97e2179faa24_0"]},
        {"id": "e33", "sources": ["57da7776fffd97e2179ddbce"], "targets": ["57da7827fffd97e2179ddf9a_0"]},
    ],
    "properties": {"elk.algorithm": "layered"},
}


class TestBug7:
    """Regression test for bug #7 - large graph with ports should not raise error."""

    def test_should_not_raise_error(self, elk):
        result = elk.layout(GRAPH)
        assert result is not None
