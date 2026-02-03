"""Port of testChangeAwareArrayList.js - large graph layout test (Les Miserables)."""
import pytest
from pyelk import ELK


@pytest.fixture
def elk():
    return ELK()


def _make_node(name, group, node_id):
    return {
        "name": name, "group": group, "width": 10, "height": 10,
        "id": str(node_id), "ports": [], "labels": []
    }


def _make_edge(source, target, value, edge_id):
    return {"source": str(source), "target": str(target), "value": value, "id": str(edge_id)}


GRAPH = {
    "properties": {"layering.strategy": "NETWORK_SIMPLEX"},
    "id": "root",
    "children": [
        _make_node("Myriel", 1, 0), _make_node("Napoleon", 1, 1),
        _make_node("Mlle.Baptistine", 1, 2), _make_node("Mme.Magloire", 1, 3),
        _make_node("CountessdeLo", 1, 4), _make_node("Geborand", 1, 5),
        _make_node("Champtercier", 1, 6), _make_node("Cravatte", 1, 7),
        _make_node("Count", 1, 8), _make_node("OldMan", 1, 9),
        _make_node("Labarre", 2, 10), _make_node("Valjean", 2, 11),
        _make_node("Marguerite", 3, 12), _make_node("Mme.deR", 2, 13),
        _make_node("Isabeau", 2, 14), _make_node("Gervais", 2, 15),
        _make_node("Tholomyes", 3, 16), _make_node("Listolier", 3, 17),
        _make_node("Fameuil", 3, 18), _make_node("Blacheville", 3, 19),
        _make_node("Favourite", 3, 20), _make_node("Dahlia", 3, 21),
        _make_node("Zephine", 3, 22), _make_node("Fantine", 3, 23),
        _make_node("Mme.Thenardier", 4, 24), _make_node("Thenardier", 4, 25),
        _make_node("Cosette", 5, 26), _make_node("Javert", 4, 27),
        _make_node("Fauchelevent", 0, 28), _make_node("Bamatabois", 2, 29),
        _make_node("Perpetue", 3, 30), _make_node("Simplice", 2, 31),
        _make_node("Scaufflaire", 2, 32), _make_node("Woman1", 2, 33),
        _make_node("Judge", 2, 34), _make_node("Champmathieu", 2, 35),
        _make_node("Brevet", 2, 36), _make_node("Chenildieu", 2, 37),
        _make_node("Cochepaille", 2, 38), _make_node("Pontmercy", 4, 39),
        _make_node("Boulatruelle", 6, 40), _make_node("Eponine", 4, 41),
        _make_node("Anzelma", 4, 42), _make_node("Woman2", 5, 43),
        _make_node("MotherInnocent", 0, 44), _make_node("Gribier", 0, 45),
        _make_node("Jondrette", 7, 46), _make_node("Mme.Burgon", 7, 47),
        _make_node("Gavroche", 8, 48), _make_node("Gillenormand", 5, 49),
        _make_node("Magnon", 5, 50), _make_node("Mlle.Gillenormand", 5, 51),
        _make_node("Mme.Pontmercy", 5, 52), _make_node("Mlle.Vaubois", 5, 53),
        _make_node("Lt.Gillenormand", 5, 54), _make_node("Marius", 8, 55),
        _make_node("BaronessT", 5, 56), _make_node("Mabeuf", 8, 57),
        _make_node("Enjolras", 8, 58), _make_node("Combeferre", 8, 59),
        _make_node("Prouvaire", 8, 60), _make_node("Feuilly", 8, 61),
        _make_node("Courfeyrac", 8, 62), _make_node("Bahorel", 8, 63),
        _make_node("Bossuet", 8, 64), _make_node("Joly", 8, 65),
        _make_node("Grantaire", 8, 66), _make_node("MotherPlutarch", 9, 67),
        _make_node("Gueulemer", 4, 68), _make_node("Babet", 4, 69),
        _make_node("Claquesous", 4, 70), _make_node("Montparnasse", 4, 71),
        _make_node("Toussaint", 5, 72), _make_node("Child1", 10, 73),
        _make_node("Child2", 10, 74), _make_node("Brujon", 4, 75),
        _make_node("Mme.Hucheloup", 8, 76),
    ],
    "edges": [
        _make_edge(1, 0, 1, 77), _make_edge(2, 0, 8, 78), _make_edge(3, 0, 10, 79),
        _make_edge(3, 2, 6, 80), _make_edge(4, 0, 1, 81), _make_edge(5, 0, 1, 82),
        _make_edge(6, 0, 1, 83), _make_edge(7, 0, 1, 84), _make_edge(8, 0, 2, 85),
        _make_edge(9, 0, 1, 86), _make_edge(11, 10, 1, 87), _make_edge(11, 3, 3, 88),
        _make_edge(11, 2, 3, 89), _make_edge(11, 0, 5, 90), _make_edge(12, 11, 1, 91),
        _make_edge(13, 11, 1, 92), _make_edge(14, 11, 1, 93), _make_edge(15, 11, 1, 94),
        _make_edge(17, 16, 4, 95), _make_edge(18, 16, 4, 96), _make_edge(18, 17, 4, 97),
        _make_edge(19, 16, 4, 98), _make_edge(19, 17, 4, 99), _make_edge(19, 18, 4, 100),
        _make_edge(20, 16, 3, 101), _make_edge(20, 17, 3, 102), _make_edge(20, 18, 3, 103),
        _make_edge(20, 19, 4, 104), _make_edge(21, 16, 3, 105), _make_edge(21, 17, 3, 106),
        _make_edge(21, 18, 3, 107), _make_edge(21, 19, 3, 108), _make_edge(21, 20, 5, 109),
        _make_edge(22, 16, 3, 110), _make_edge(22, 17, 3, 111), _make_edge(22, 18, 3, 112),
        _make_edge(22, 19, 3, 113), _make_edge(22, 20, 4, 114), _make_edge(22, 21, 4, 115),
        _make_edge(23, 16, 3, 116), _make_edge(23, 17, 3, 117), _make_edge(23, 18, 3, 118),
        _make_edge(23, 19, 3, 119), _make_edge(23, 20, 4, 120), _make_edge(23, 21, 4, 121),
        _make_edge(23, 22, 4, 122), _make_edge(23, 12, 2, 123), _make_edge(23, 11, 9, 124),
        _make_edge(24, 23, 2, 125), _make_edge(24, 11, 7, 126), _make_edge(25, 24, 13, 127),
        _make_edge(25, 23, 1, 128), _make_edge(25, 11, 12, 129), _make_edge(26, 24, 4, 130),
        _make_edge(26, 11, 31, 131), _make_edge(26, 16, 1, 132), _make_edge(26, 25, 1, 133),
        _make_edge(27, 11, 17, 134), _make_edge(27, 23, 5, 135), _make_edge(27, 25, 5, 136),
        _make_edge(27, 24, 1, 137), _make_edge(27, 26, 1, 138), _make_edge(28, 11, 8, 139),
        _make_edge(28, 27, 1, 140), _make_edge(29, 23, 1, 141), _make_edge(29, 27, 1, 142),
        _make_edge(29, 11, 2, 143), _make_edge(30, 23, 1, 144), _make_edge(31, 30, 2, 145),
        _make_edge(31, 11, 3, 146), _make_edge(31, 23, 2, 147), _make_edge(31, 27, 1, 148),
        _make_edge(32, 11, 1, 149), _make_edge(33, 11, 2, 150), _make_edge(33, 27, 1, 151),
        _make_edge(34, 11, 3, 152), _make_edge(34, 29, 2, 153), _make_edge(35, 11, 3, 154),
        _make_edge(35, 34, 3, 155), _make_edge(35, 29, 2, 156), _make_edge(36, 34, 2, 157),
        _make_edge(36, 35, 2, 158), _make_edge(36, 11, 2, 159), _make_edge(36, 29, 1, 160),
        _make_edge(37, 34, 2, 161), _make_edge(37, 35, 2, 162), _make_edge(37, 36, 2, 163),
        _make_edge(37, 11, 2, 164), _make_edge(37, 29, 1, 165), _make_edge(38, 34, 2, 166),
        _make_edge(38, 35, 2, 167), _make_edge(38, 36, 2, 168), _make_edge(38, 37, 2, 169),
        _make_edge(38, 11, 2, 170), _make_edge(38, 29, 1, 171), _make_edge(39, 25, 1, 172),
        _make_edge(40, 25, 1, 173), _make_edge(41, 24, 2, 174), _make_edge(41, 25, 3, 175),
        _make_edge(42, 41, 2, 176), _make_edge(42, 25, 2, 177), _make_edge(42, 24, 1, 178),
        _make_edge(43, 11, 3, 179), _make_edge(43, 26, 1, 180), _make_edge(43, 27, 1, 181),
        _make_edge(44, 28, 3, 182), _make_edge(44, 11, 1, 183), _make_edge(45, 28, 2, 184),
        _make_edge(47, 46, 1, 185), _make_edge(48, 47, 2, 186), _make_edge(48, 25, 1, 187),
        _make_edge(48, 27, 1, 188), _make_edge(48, 11, 1, 189), _make_edge(49, 26, 3, 190),
        _make_edge(49, 11, 2, 191), _make_edge(50, 49, 1, 192), _make_edge(50, 24, 1, 193),
        _make_edge(51, 49, 9, 194), _make_edge(51, 26, 2, 195), _make_edge(51, 11, 2, 196),
        _make_edge(52, 51, 1, 197), _make_edge(52, 39, 1, 198), _make_edge(53, 51, 1, 199),
        _make_edge(54, 51, 2, 200), _make_edge(54, 49, 1, 201), _make_edge(54, 26, 1, 202),
        _make_edge(55, 51, 6, 203), _make_edge(55, 49, 12, 204), _make_edge(55, 39, 1, 205),
        _make_edge(55, 54, 1, 206), _make_edge(55, 26, 21, 207), _make_edge(55, 11, 19, 208),
        _make_edge(55, 16, 1, 209), _make_edge(55, 25, 2, 210), _make_edge(55, 41, 5, 211),
        _make_edge(55, 48, 4, 212), _make_edge(56, 49, 1, 213), _make_edge(56, 55, 1, 214),
        _make_edge(57, 55, 1, 215), _make_edge(57, 41, 1, 216), _make_edge(57, 48, 1, 217),
        _make_edge(58, 55, 7, 218), _make_edge(58, 48, 7, 219), _make_edge(58, 27, 6, 220),
        _make_edge(58, 57, 1, 221), _make_edge(58, 11, 4, 222), _make_edge(59, 58, 15, 223),
        _make_edge(59, 55, 5, 224), _make_edge(59, 48, 6, 225), _make_edge(59, 57, 2, 226),
        _make_edge(60, 48, 1, 227), _make_edge(60, 58, 4, 228), _make_edge(60, 59, 2, 229),
        _make_edge(61, 48, 2, 230), _make_edge(61, 58, 6, 231), _make_edge(61, 60, 2, 232),
        _make_edge(61, 59, 5, 233), _make_edge(61, 57, 1, 234), _make_edge(61, 55, 1, 235),
        _make_edge(62, 55, 9, 236), _make_edge(62, 58, 17, 237), _make_edge(62, 59, 13, 238),
        _make_edge(62, 48, 7, 239), _make_edge(62, 57, 2, 240), _make_edge(62, 41, 1, 241),
        _make_edge(62, 61, 6, 242), _make_edge(62, 60, 3, 243), _make_edge(63, 59, 5, 244),
        _make_edge(63, 48, 5, 245), _make_edge(63, 62, 6, 246), _make_edge(63, 57, 2, 247),
        _make_edge(63, 58, 4, 248), _make_edge(63, 61, 3, 249), _make_edge(63, 60, 2, 250),
        _make_edge(63, 55, 1, 251), _make_edge(64, 55, 5, 252), _make_edge(64, 62, 12, 253),
        _make_edge(64, 48, 5, 254), _make_edge(64, 63, 4, 255), _make_edge(64, 58, 10, 256),
        _make_edge(64, 61, 6, 257), _make_edge(64, 60, 2, 258), _make_edge(64, 59, 9, 259),
        _make_edge(64, 57, 1, 260), _make_edge(64, 11, 1, 261), _make_edge(65, 63, 5, 262),
        _make_edge(65, 64, 7, 263), _make_edge(65, 48, 3, 264), _make_edge(65, 62, 5, 265),
        _make_edge(65, 58, 5, 266), _make_edge(65, 61, 5, 267), _make_edge(65, 60, 2, 268),
        _make_edge(65, 59, 5, 269), _make_edge(65, 57, 1, 270), _make_edge(65, 55, 2, 271),
        _make_edge(66, 64, 3, 272), _make_edge(66, 58, 3, 273), _make_edge(66, 59, 1, 274),
        _make_edge(66, 62, 2, 275), _make_edge(66, 65, 2, 276), _make_edge(66, 48, 1, 277),
        _make_edge(66, 63, 1, 278), _make_edge(66, 61, 1, 279), _make_edge(66, 60, 1, 280),
        _make_edge(67, 57, 3, 281), _make_edge(68, 25, 5, 282), _make_edge(68, 11, 1, 283),
        _make_edge(68, 24, 1, 284), _make_edge(68, 27, 1, 285), _make_edge(68, 48, 1, 286),
        _make_edge(68, 41, 1, 287), _make_edge(69, 25, 6, 288), _make_edge(69, 68, 6, 289),
        _make_edge(69, 11, 1, 290), _make_edge(69, 24, 1, 291), _make_edge(69, 27, 2, 292),
        _make_edge(69, 48, 1, 293), _make_edge(69, 41, 1, 294), _make_edge(70, 25, 4, 295),
        _make_edge(70, 69, 4, 296), _make_edge(70, 68, 4, 297), _make_edge(70, 11, 1, 298),
        _make_edge(70, 24, 1, 299), _make_edge(70, 27, 1, 300), _make_edge(70, 41, 1, 301),
        _make_edge(70, 58, 1, 302), _make_edge(71, 27, 1, 303), _make_edge(71, 69, 2, 304),
        _make_edge(71, 68, 2, 305), _make_edge(71, 70, 2, 306), _make_edge(71, 11, 1, 307),
        _make_edge(71, 48, 1, 308), _make_edge(71, 41, 1, 309), _make_edge(71, 25, 1, 310),
        _make_edge(72, 26, 2, 311), _make_edge(72, 27, 1, 312), _make_edge(72, 11, 1, 313),
        _make_edge(73, 48, 2, 314), _make_edge(74, 48, 2, 315), _make_edge(74, 73, 3, 316),
        _make_edge(75, 69, 3, 317), _make_edge(75, 68, 3, 318), _make_edge(75, 25, 3, 319),
        _make_edge(75, 48, 1, 320), _make_edge(75, 41, 1, 321), _make_edge(75, 70, 1, 322),
        _make_edge(75, 71, 1, 323), _make_edge(76, 64, 1, 324), _make_edge(76, 65, 1, 325),
        _make_edge(76, 66, 1, 326), _make_edge(76, 63, 1, 327), _make_edge(76, 62, 1, 328),
        _make_edge(76, 48, 1, 329), _make_edge(76, 58, 1, 330),
    ],
}


class TestChangeAwareArrayList:
    """Test with large graph (Les Miserables) using NETWORK_SIMPLEX layering."""

    def test_should_finish(self, elk):
        result = elk.layout(GRAPH)
        assert result is not None
