import unittest
from lxml import etree as et

from teiphy import VariationUnit


class VariationUnitTestCase(unittest.TestCase):
    def test_init_xml_id(self):
        xml = et.fromstring(
            """
        <app xml:id="B10K6V20U12">
            <lem><w>ινα</w></lem>
            <rdg n="1" wit="P46 01 02 03 06 010 012 016 018 020 025 044 049 056 075 0142 0150 0151 0278 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1739 1751 1831 1836 1837 1840 1851 1860 1877 1881 1886 1893 1908 1912 1918 1939 1942 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2834 2865 L156 L169 L587 L809 L1159 L1178 L1188 L1440 L2010 L2058 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copsa copbo Ambrosiaster BasilOfCaesarea Chrysostom Jerome MariusVictorinus Pelagius TheodoreOfMopsuestia"><w>ινα</w></rdg>
            <witDetail n="Z" type="lac" wit="P49 P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 048 075S 082 0159 0230 0285 0320 203S 424C1 1838 1910 2865S L23 L60 L1126 L1298 VL51 VL54 VL58 VL59 VL61 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria ClementOfAlexandria Cyprian CyrilOfAlexandria CyrilOfJerusalem Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion MariusVictorinus Origen Primasius Procopius PseudoAthanasius Severian Speculum Tertullian Theodoret"/>
        </app>
        """
        )
        vu = VariationUnit(xml)
        self.assertEqual(vu.id, "B10K6V20U12")
        self.assertEqual(str(vu), "B10K6V20U12")
        self.assertEqual(repr(vu), "B10K6V20U12")

    def test_init_n_id(self):
        xml = et.fromstring(
            """
        <app n="39">
            <lem><w>ινα</w></lem>
            <rdg n="1" wit="P46 01 02 03 06 010 012 016 018 020 025 044 049 056 075 0142 0150 0151 0278 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1739 1751 1831 1836 1837 1840 1851 1860 1877 1881 1886 1893 1908 1912 1918 1939 1942 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2834 2865 L156 L169 L587 L809 L1159 L1178 L1188 L1440 L2010 L2058 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copsa copbo Ambrosiaster BasilOfCaesarea Chrysostom Jerome MariusVictorinus Pelagius TheodoreOfMopsuestia"><w>ινα</w></rdg>
            <witDetail n="Z" type="lac" wit="P49 P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 048 075S 082 0159 0230 0285 0320 203S 424C1 1838 1910 2865S L23 L60 L1126 L1298 VL51 VL54 VL58 VL59 VL61 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria ClementOfAlexandria Cyprian CyrilOfAlexandria CyrilOfJerusalem Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion MariusVictorinus Origen Primasius Procopius PseudoAthanasius Severian Speculum Tertullian Theodoret"/>
        </app>
        """
        )
        vu = VariationUnit(xml)
        self.assertEqual(vu.id, "39")

    def test_init_readings_lem_wits(self):
        xml = et.fromstring(
            """
        <app xml:id="B10K5V19U17">
            <lem n="1" wit="P46 01 03 06 010 012 018 020 025 044 049 056 075 0142 0150 0151 0278 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203S 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1739 1751 1831 1836 1837 1840 1851 1860 1877 1881 1886 1893 1908 1910 1912 1918 1939 1942 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2865S L23 L156 L169 L1126 L1159 L1178 L1188 L1298 L1440 L2058 VL61 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copsa copbo Ambrosiaster BasilOfCaesarea Chrysostom CyrilOfJerusalem Jerome MariusVictorinus Origen Pelagius TheodoreOfMopsuestia"/>
            <rdg n="2" wit="02"><w>εν</w><w>χαριτι</w></rdg>
            <witDetail n="Z" type="lac" wit="P49 P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 016 048 075S 082 0159 0230 0285 0320 203 256 424C1 1838 2805 2834 2865 L60 L587 L809 L2010 VL51 VL54 VL58 VL59 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria ClementOfAlexandria Cyprian CyrilOfAlexandria Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion Primasius Procopius PseudoAthanasius Severian Speculum Tertullian Theodoret"/>
        </app>
        """
        )
        vu = VariationUnit(xml)
        self.assertEqual(len(vu.readings), 3)

    def test_init_readings(self):
        xml = et.fromstring(
            """
        <app xml:id="B10K5V19U17">
            <lem/>
            <rdg n="1" wit="P46 01 03 06 010 012 018 020 025 044 049 056 075 0142 0150 0151 0278 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203S 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1739 1751 1831 1836 1837 1840 1851 1860 1877 1881 1886 1893 1908 1910 1912 1918 1939 1942 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2865S L23 L156 L169 L1126 L1159 L1178 L1188 L1298 L1440 L2058 VL61 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copsa copbo Ambrosiaster BasilOfCaesarea Chrysostom CyrilOfJerusalem Jerome MariusVictorinus Origen Pelagius TheodoreOfMopsuestia"/>
            <rdg n="2" wit="02"><w>εν</w><w>χαριτι</w></rdg>
            <witDetail n="Z" type="lac" wit="P49 P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 016 048 075S 082 0159 0230 0285 0320 203 256 424C1 1838 2805 2834 2865 L60 L587 L809 L2010 VL51 VL54 VL58 VL59 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria ClementOfAlexandria Cyprian CyrilOfAlexandria Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion Primasius Procopius PseudoAthanasius Severian Speculum Tertullian Theodoret"/>
        </app>
        """
        )
        vu = VariationUnit(xml)
        self.assertEqual(
            len(vu.readings), 3
        )  # this time, the lem element does not count, because it has no wit attribute

    def test_init_readings_rdg_grp(self):
        xml = et.fromstring(
            """
        <app xml:id="B10K1V1U24-26">
            <lem><w>εν</w><w>εφεσω</w></lem>
            <rdg n="1" wit="01C2 02 03C2 06 012 018 020 025 044 049 056 075S 0142 0150 0151 0319 1 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 296 322 326 330 337 363 365 383 398 424* 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1751 1831 1836 1837 1838 1840 1851 1860 1877 1881 1886 1893 1908 1910 1912 1918 1939 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2865S L169 L587 L809 L1159 L1178 L1188 L1440 L2058 VL61 VL64 VL75 VL77 VL78 VL89 vgcl vgst vgww syrh syrp copsa copbo gothA gothB Ambrosiaster Chrysostom Jerome MariusVictorinus Pelagius PseudoAthanasius TheodoreOfMopsuestia"><w>εν</w><w>εφεσω</w></rdg>
            <rdgGrp type="reconstructed">
                <rdg n="1-v1" wit="L2010"><w>εν</w><w><unclear>ε</unclear>φεσω</w></rdg>
                <rdg n="1-v2" wit="2344"><w><unclear>εν</unclear></w><w>εφεσω</w></rdg>
                <rdg n="1-v3" wit="256"><w><supplied reason="lacuna">εν</supplied></w><w><supplied reason="lacuna">εφεσ</supplied>ω</w></rdg>
            </rdgGrp>
            <rdgGrp type="defective">
                <rdg n="1-f1" cause="parablepsis" wit="010"><w>εν</w><w>εφεω</w></rdg>
                <rdg n="1-f2" cause="dittography" wit="263"><w>εν</w><w>νεφεσω</w></rdg>
            </rdgGrp>
            <rdgGrp type="orthographic">
                <rdg n="1-o1" wit="0278"><w>εν</w><w>εφεσωι</w></rdg>
            </rdgGrp>
            <rdgGrp type="subreading">
                <rdg n="1-s1" cause="clarification" wit=""><w>εν</w><w>τω</w><w>εφεσω</w></rdg>
                <rdgGrp type="reconstructed">
                    <rdg n="1-s1-v1" wit="1115"><w>εν</w><w>τ<unclear>ω</unclear></w><w>εφεσω</w></rdg>
                </rdgGrp>
            </rdgGrp>
            <rdg n="2" wit="P46 01* 03* 6 424C1 1739 BasilOfCaesarea Ephrem Marcion Origen"/>
        </app>
        """
        )
        vu = VariationUnit(xml)
        self.assertEqual(len(vu.readings), 10)


if __name__ == '__main__':
    unittest.main()
