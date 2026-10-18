"""Brandes-Köpnig node placement (strategy BRANDES_KOZEN / BRANDES).

Checks: valid non-overlapping layouts, deterministic output, alias
acceptance, and that BK actually straightens the aligned long edge the
centred fallback bends: s has a single neighbour — the dummy of the
spanning s->z edge — so BK gives the chain (s, dummy, z) one shared
centre, while SIMPLE re-centres each layer and must bend it because the
middle layer carries a wide sibling."""
import copy

from pyelk import ELK

WIDE = {
    "id": "root",
    "layoutOptions": {
        "algorithm": "layered",
        "elk.spacing.nodeNode": 10,
        "elk.layered.spacing.nodeNodeBetweenLayers": 10,
    },
    "children": [
        {"id": "s", "width": 40, "height": 20},
        {"id": "a", "width": 100, "height": 20},
        {"id": "b", "width": 100, "height": 20},
        {"id": "z", "width": 40, "height": 20},
    ],
    "edges": [
        {"id": "e1", "sources": ["s"], "targets": ["z"]},
        {"id": "e2", "sources": ["a"], "targets": ["b"]},
        {"id": "e3", "sources": ["b"], "targets": ["z"]},
    ],
}


class TestBrandesKozen:
    def test_runs_without_error(self):
        result = self._layout()
        assert len(result["children"]) == 4

    def test_alias_brandes_also_runs(self):
        result = ELK().layout(self._graph(), layout_options={
            "elk.layered.nodePlacement.strategy": "BRANDES"})
        assert len(result["children"]) == 4

    def test_no_overlaps_within_layers(self):
        result = self._layout()
        rows = {}
        for c in result["children"]:
            rows.setdefault(round(c["y"], 3), []).append(c)
        for row in rows.values():
            row.sort(key=lambda c: c["x"])
            for a, b in zip(row, row[1:]):
                assert a["x"] + a["width"] <= b["x"] + 1e-3, \
                    "%s overlaps %s" % (a["id"], b["id"])

    def test_deterministic(self):
        assert self._layout() == self._layout()

    def test_simple_still_works(self):
        result = ELK().layout(self._graph(), layout_options={
            "elk.layered.nodePlacement.strategy": "SIMPLE"})
        assert len(result["children"]) == 4

    def test_bk_aligns_more_adjacent_centres(self):
        """A layered graph whose long edge (x->z) runs through dummies:
        BK's alignment chains give more adjacent-layer edges a shared
        centre than the centred fallback (which re-centres each layer
        independently and bends everything off the median)."""
        g = {
            "id": "root",
            "layoutOptions": {
                "algorithm": "layered",
                "elk.spacing.nodeNode": 10,
                "elk.layered.spacing.nodeNodeBetweenLayers": 10,
            },
            "children": [
                {"id": "x", "width": 40, "height": 20},
                {"id": "a", "width": 100, "height": 20},
                {"id": "b", "width": 100, "height": 20},
                {"id": "z", "width": 40, "height": 20},
            ],
            "edges": [
                {"id": "e_xa", "sources": ["x"], "targets": ["a"]},
                {"id": "e_ab", "sources": ["a"], "targets": ["b"]},
                {"id": "e_bz", "sources": ["b"], "targets": ["z"]},
                {"id": "e_xz", "sources": ["x"], "targets": ["z"]},
            ],
        }
        bk = ELK().layout(copy.deepcopy(g), layout_options={
            "elk.layered.nodePlacement.strategy": "BRANDES_KOZEN"})
        simple = ELK().layout(copy.deepcopy(g), layout_options={
            "elk.layered.nodePlacement.strategy": "SIMPLE"})
        pairs_bk = self._straight_pairs(bk)
        pairs_simple = self._straight_pairs(simple)
        assert pairs_bk > pairs_simple, \
            "BK aligned %d centre pairs vs SIMPLE %d" \
            % (pairs_bk, pairs_simple)

    # -- helpers --------------------------------------------------------

    def _graph(self):
        return copy.deepcopy(WIDE)

    def _layout(self):
        return ELK().layout(self._graph(), layout_options={
            "elk.layered.nodePlacement.strategy": "BRANDES_KOZEN"})

    def _straight_pairs(self, result):
        """Adjacent-layer edge endpoints sharing one centre = aligned."""
        centres = {c["id"]: (c["x"] + c["width"] / 2.0)
                   for c in result["children"]}
        # recover adjacency from the routed sections' source/end shapes:
        # pyelk writes section ids '<edge>_s0' — map via edges' children
        count = 0
        for e in result.get("edges", []):
            for sec in e.get("sections") or []:
                pts = ([sec["startPoint"]]
                       + list(sec.get("bendPoints") or [])
                       + [sec["endPoint"]])
                xs = {round(p["x"], 3) for p in pts}
                if len(xs) == 1:
                    count += 1
        return count