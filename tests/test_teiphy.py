import unittest
from lxml import etree as et

from teiphy import Witness, Reading, VariationUnit, Collation

class WitnessTestCase(unittest.TestCase):
    def test_init_xml_id(self):
        xml = et.fromstring("<witness xml:id=\"A\" n=\"1\">A witness</witness>")
        witness = Witness(xml)
        self.assertEqual(witness.id, "A")

    def test_init_n_id(self):
        xml = et.fromstring("<witness n=\"1\">A witness</witness>")
        witness = Witness(xml)
        self.assertEqual(witness.id, "1")

    def test_init_text_id(self):
        xml = et.fromstring("<witness>A witness</witness>")
        witness = Witness(xml)
        self.assertEqual(witness.id, "A witness")

    def test_init_type_default(self):
        xml = et.fromstring("<witness xml:id=\"A\"/>")
        witness = Witness(xml)
        self.assertEqual(witness.type, "manuscript")

    def test_init_type_specified(self):
        xml = et.fromstring("<witness n=\"424C1\" type=\"corrector\"/>")
        witness = Witness(xml)
        self.assertEqual(witness.type, "corrector")

class ReadingTestCase(unittest.TestCase):
    def test_init_xml_id(self):
        xml = et.fromstring("<rdg xml:id=\"B10K1V1U2R1\" n=\"1\"><w>παυλος</w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.id, "B10K1V1U2R1")

    def test_init_n_id(self):
        xml = et.fromstring("<rdg n=\"1\"><w>παυλος</w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.id, "1")

    def test_init_text_id(self):
        xml = et.fromstring("<lem><w>παυλος</w></lem>") # lem elements should be processed like rdg elements
        reading = Reading(xml)
        self.assertEqual(reading.id, "παυλος")

    def test_init_type_default(self):
        xml = et.fromstring("<rdg n=\"1\"><w>εν</w><w>εφεσω</w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.type, "substantive")

    def test_init_type_specified(self):
        xml = et.fromstring("<rdg n=\"1-v1\" type=\"reconstructed\"><w>εν</w><w><unclear>ε</unclear>φεσω</w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.type, "reconstructed")

    def test_init_wits_id(self):
        xml = et.fromstring("<rdg n=\"1-v1\" type=\"reconstructed\" wit=\"#L2010\"><w>εν</w><w><unclear>ε</unclear>φεσω</w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.wits, ["L2010"])

    def test_init_wits_n(self):
        xml = et.fromstring("<rdg n=\"2\" wit=\"P46 01* 03* 6 424C1 1739 BasilOfCaesarea Ephrem Marcion Origen\"/>")
        reading = Reading(xml)
        self.assertEqual(reading.wits, ["P46", "01*", "03*", "6", "424C1", "1739", "BasilOfCaesarea", "Ephrem", "Marcion", "Origen"])

    def test_init_targets_id(self):
        xml = et.fromstring("<witDetail target=\"#B10K1V1U2R1 #B10K1V1U2R2\"/>")
        reading = Reading(xml)
        self.assertEqual(reading.targets, ["B10K1V1U2R1", "B10K1V1U2R2"])

    def test_init_targets_n(self):
        xml = et.fromstring("<witDetail target=\"1 2 3\"/>")
        reading = Reading(xml)
        self.assertEqual(reading.targets, ["1", "2", "3"])

    def test_init_certainties_default(self):
        xml = et.fromstring("<witDetail target=\"1 2\"/>")
        reading = Reading(xml)
        self.assertEqual(reading.certainties, {"1": 0.5, "2": 0.5})

    def test_init_certainties_specified(self):
        xml = et.fromstring("<witDetail target=\"1 2\"><certainty target=\"1\" degree=\"0.75\"/><certainty target=\"2\" degree=\"0.25\"/></witDetail>")
        reading = Reading(xml)
        self.assertEqual(reading.certainties, {"1": 0.75, "2": 0.25})

    def test_init_text_unclear_supplied(self):
        xml = et.fromstring("<rdg n=\"2-v2\" type=\"reconstructed\" wit=\"94\"><w><unclear>π</unclear><supplied reason=\"lacuna\">ρω</supplied>τον</w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "π̣[ρω]τον")

    def test_init_text_abbr_hi(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><w><abbr><hi rend=\"overline\">θυ</hi></abbr></w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "θ̅υ̅")

    def test_init_text_ex(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><w>πα<ex>ρα</ex></w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "πα(ρα)")

    def test_init_text_space_extent_reason(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><space unit=\"char\" extent=\"2-4\" reason=\"erased\"/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[2-4 char space (erased)]")
    
    def test_init_text_space_extent(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><space unit=\"line\" extent=\"part\"/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[part line space]")

    def test_init_text_space_reason(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><space reason=\"erased\"/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[space (erased)]")

    def test_init_text_space(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><space/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[space]")

    def test_init_text_gap_extent_reason(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><gap unit=\"verse\" extent=\"part\" reason=\"lacuna\"/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[part verse gap (lacuna)]")

    def test_init_text_gap_extent(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><gap unit=\"char\" extent=\"10\"/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[10 char gap]")

    def test_init_text_gap_reason(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><gap reason=\"illegible\"/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[... (illegible)]")

    def test_init_text_gap(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><gap/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[...]")

    def test_init_text_choice(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><w><choice><unclear>οτι</unclear><unclear>ετι</unclear></choice></w></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "[ο̣τ̣ι̣/ε̣τ̣ι̣]")

    def test_init_text_ref(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><ref target=\"#B1K1V1U2\"/><ref target=\"#B1K1V1U4\"/></rdg>")
        reading = Reading(xml)
        self.assertEqual(reading.text, "<B1K1V1U2><B1K1V1U4>")

class VariationUnitTestCase(unittest.TestCase):
    def test_init_xml_id(self):
        xml = et.fromstring("""
        <app xml:id="B10K6V20U12">
            <lem><w>ινα</w></lem>
            <rdg n="1" wit="P46 01 02 03 06 010 012 016 018 020 025 044 049 056 075 0142 0150 0151 0278 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1739 1751 1831 1836 1837 1840 1851 1860 1877 1881 1886 1893 1908 1912 1918 1939 1942 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2834 2865 L156 L169 L587 L809 L1159 L1178 L1188 L1440 L2010 L2058 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copsa copbo Ambrosiaster BasilOfCaesarea Chrysostom Jerome MariusVictorinus Pelagius TheodoreOfMopsuestia"><w>ινα</w></rdg>
            <witDetail n="Z" type="lac" wit="P49 P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 048 075S 082 0159 0230 0285 0320 203S 424C1 1838 1910 2865S L23 L60 L1126 L1298 VL51 VL54 VL58 VL59 VL61 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria ClementOfAlexandria Cyprian CyrilOfAlexandria CyrilOfJerusalem Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion MariusVictorinus Origen Primasius Procopius PseudoAthanasius Severian Speculum Tertullian Theodoret"/>
        </app>
        """)
        vu = VariationUnit(xml)
        self.assertEqual(vu.id, "B10K6V20U12")

    def test_init_n_id(self):
        xml = et.fromstring("""
        <app n="39">
            <lem><w>ινα</w></lem>
            <rdg n="1" wit="P46 01 02 03 06 010 012 016 018 020 025 044 049 056 075 0142 0150 0151 0278 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1739 1751 1831 1836 1837 1840 1851 1860 1877 1881 1886 1893 1908 1912 1918 1939 1942 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2805 2834 2865 L156 L169 L587 L809 L1159 L1178 L1188 L1440 L2010 L2058 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copsa copbo Ambrosiaster BasilOfCaesarea Chrysostom Jerome MariusVictorinus Pelagius TheodoreOfMopsuestia"><w>ινα</w></rdg>
            <witDetail n="Z" type="lac" wit="P49 P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 048 075S 082 0159 0230 0285 0320 203S 424C1 1838 1910 2865S L23 L60 L1126 L1298 VL51 VL54 VL58 VL59 VL61 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria ClementOfAlexandria Cyprian CyrilOfAlexandria CyrilOfJerusalem Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion MariusVictorinus Origen Primasius Procopius PseudoAthanasius Severian Speculum Tertullian Theodoret"/>
        </app>
        """)
        vu = VariationUnit(xml)
        self.assertEqual(vu.id, "39")

    def test_init_readings_lem_wits(self):
        xml = et.fromstring("""
        <app xml:id="B10K5V19U17">
            <lem n="1" wit="P46 01 03 06 010 012 018 020 025 044 049 056 075 0142 0150 0151 0278 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203S 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1739 1751 1831 1836 1837 1840 1851 1860 1877 1881 1886 1893 1908 1910 1912 1918 1939 1942 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2865S L23 L156 L169 L1126 L1159 L1178 L1188 L1298 L1440 L2058 VL61 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copsa copbo Ambrosiaster BasilOfCaesarea Chrysostom CyrilOfJerusalem Jerome MariusVictorinus Origen Pelagius TheodoreOfMopsuestia"/>
            <rdg n="2" wit="02"><w>εν</w><w>χαριτι</w></rdg>
            <witDetail n="Z" type="lac" wit="P49 P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 016 048 075S 082 0159 0230 0285 0320 203 256 424C1 1838 2805 2834 2865 L60 L587 L809 L2010 VL51 VL54 VL58 VL59 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria ClementOfAlexandria Cyprian CyrilOfAlexandria Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion Primasius Procopius PseudoAthanasius Severian Speculum Tertullian Theodoret"/>
        </app>
        """)
        vu = VariationUnit(xml)
        self.assertEqual(len(vu.readings), 3)

    def test_init_readings(self):
        xml = et.fromstring("""
        <app xml:id="B10K5V19U17">
            <lem/>
            <rdg n="1" wit="P46 01 03 06 010 012 018 020 025 044 049 056 075 0142 0150 0151 0278 0319 1 6 18 33 35 38 61 69 81 88 93 94 102 104 177 181 203S 218 256 263 296 322 326 330 337 363 365 383 398 424 436 442 451 459 462 467 506 606 629 636 664 665 915 1069 1108 1115 1127 1175 1240 1241 1245 1311 1319 1398 1490 1505 1509 1573 1611 1617 1678 1718 1721 1729 1739 1751 1831 1836 1837 1840 1851 1860 1877 1881 1886 1893 1908 1910 1912 1918 1939 1942 1959 1962 1963 1985 1987 1991 1996 1999 2004 2005 2008 2011 2012 2127 2138 2180 2243 2344 2352 2400 2464 2492 2495 2516 2523 2544 2576 2865S L23 L156 L169 L1126 L1159 L1178 L1188 L1298 L1440 L2058 VL61 VL75 VL77 VL78 VL86 VL89 vgcl vgww vgst syrp syrh copsa copbo Ambrosiaster BasilOfCaesarea Chrysostom CyrilOfJerusalem Jerome MariusVictorinus Origen Pelagius TheodoreOfMopsuestia"/>
            <rdg n="2" wit="02"><w>εν</w><w>χαριτι</w></rdg>
            <witDetail n="Z" type="lac" wit="P49 P92 P132 01C1 01C2 03C1 03C2 04 06C1 06C2 016 048 075S 082 0159 0230 0285 0320 203 256 424C1 1838 2805 2834 2865 L60 L587 L809 L2010 VL51 VL54 VL58 VL59 VL62 VL64 VL65 VL67 VL76 VL83 VL85 syrhmg gothA gothB Adamantius AthanasiusOfAlexandria ClementOfAlexandria Cyprian CyrilOfAlexandria Ephrem Epiphanius GregoryOfNazianzus GregoryOfNyssa GregoryThaumaturgus Irenaeus Lucifer Marcion Primasius Procopius PseudoAthanasius Severian Speculum Tertullian Theodoret"/>
        </app>
        """)
        vu = VariationUnit(xml)
        self.assertEqual(len(vu.readings), 3) # this time, the lem element does not count, because it has no wit attribute

    def test_init_readings_rdg_grp(self):
        xml = et.fromstring("""
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
        """)
        vu = VariationUnit(xml)
        self.assertEqual(len(vu.readings), 10)

class CollationDefaultTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml)

    def test_witnesses(self):
        self.assertEqual(len(self.collation.witnesses), 223)

    def test_witness_index_by_id(self):
        self.assertEqual(len(self.collation.witness_index_by_id), 223)

    def test_variation_units(self):
        self.assertEqual(len(self.collation.variation_units), 42)
    
    def test_readings_by_witness(self):
        self.assertEqual(len(self.collation.readings_by_witness), 223)

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_ids), 41) # app B10K6V20U12 should always be ignored

    def test_substantive_reading_ids(self):
        self.assertEqual(len(self.collation.substantive_reading_ids), 443) # all readings except for the one in app B10K6V20U12

class CollationTrivialReconstructedTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed"])

    def test_witnesses(self):
        self.assertEqual(len(self.collation.witnesses), 223)

    def test_witness_index_by_id(self):
        self.assertEqual(len(self.collation.witness_index_by_id), 223)

    def test_variation_units(self):
        self.assertEqual(len(self.collation.variation_units), 42)
    
    def test_readings_by_witness(self):
        self.assertEqual(len(self.collation.readings_by_witness), 223)

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_ids), 41) # app B10K6V20U12 should always be ignored

    def test_substantive_reading_ids(self):
        self.assertEqual(len(self.collation.substantive_reading_ids), 319) # all readings except for the one in app B10K6V20U12 and all reconstructed readings

class CollationTrivialDefectiveTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective"])

    def test_witnesses(self):
        self.assertEqual(len(self.collation.witnesses), 223)

    def test_witness_index_by_id(self):
        self.assertEqual(len(self.collation.witness_index_by_id), 223)

    def test_variation_units(self):
        self.assertEqual(len(self.collation.variation_units), 42)
    
    def test_readings_by_witness(self):
        self.assertEqual(len(self.collation.readings_by_witness), 223)

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_ids), 40) # all units except B10K6V20U12 and B10K4V28U18-20

    def test_substantive_reading_ids(self):
        self.assertEqual(len(self.collation.substantive_reading_ids), 175) # all readings except for the ones in app B10K6V20U12 and B10K4V28U18-20 and all reconstructed and defective readings

class CollationTrivialOrthographicTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective", "orthographic"])

    def test_witnesses(self):
        self.assertEqual(len(self.collation.witnesses), 223)

    def test_witness_index_by_id(self):
        self.assertEqual(len(self.collation.witness_index_by_id), 223)

    def test_variation_units(self):
        self.assertEqual(len(self.collation.variation_units), 42)
    
    def test_readings_by_witness(self):
        self.assertEqual(len(self.collation.readings_by_witness), 223)

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_ids), 40) # all units except B10K6V20U12 and B10K4V28U18-20

    def test_substantive_reading_ids(self):
        self.assertEqual(len(self.collation.substantive_reading_ids), 163) # all readings except for the ones in app B10K6V20U12 and B10K4V28U18-20 and all reconstructed, defective, and orthographic readings

class CollationTrivialOrthographicTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective", "orthographic", "subreading"])

    def test_witnesses(self):
        self.assertEqual(len(self.collation.witnesses), 223)

    def test_witness_index_by_id(self):
        self.assertEqual(len(self.collation.witness_index_by_id), 223)

    def test_variation_units(self):
        self.assertEqual(len(self.collation.variation_units), 42)
    
    def test_readings_by_witness(self):
        self.assertEqual(len(self.collation.readings_by_witness), 223)

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_ids), 40) # all units except B10K6V20U12 and B10K4V28U18-20

    def test_substantive_reading_ids(self):
        self.assertEqual(len(self.collation.substantive_reading_ids), 113) # all readings except for the ones in app B10K6V20U12 and B10K4V28U18-20 and all readings that have non-substantive types

class CollationMissingTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml, missing_reading_types=["lac", "overlap"])
    
    def test_missing_lac(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V1U24-26")
        rdg_support = self.collation.readings_by_witness["01C1"][vu_ind]
        self.assertEqual(sum(rdg_support), 0) # all entries in the reading support vector for this lacunose witness should be 0

    def test_missing_overlap(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V6U22-26")
        rdg_support = self.collation.readings_by_witness["1398"][vu_ind]
        self.assertEqual(sum(rdg_support), 0) # all entries in the reading support vector for this witness to an overlapping reading should be 0

class CollationManuscriptSuffixesTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml, manuscript_suffixes=["*", "T", "C", "C0", "C1", "C2", "C2a", "C2b", "A", "/1", "/2", "/3"])

    def test_get_base_wit_no_suffix(self):
        self.assertEqual(self.collation.get_base_wit("424"), "424")

    def test_get_base_wit_apparent_suffix(self):
        self.assertEqual(self.collation.get_base_wit("424C1"), "424C1") # "C1" is a suffix, but "424C1" is a distinct witness

    def test_get_base_wit_one_suffix(self):
        self.assertEqual(self.collation.get_base_wit("424*"), "424")

    def test_get_base_wit_multiple_suffixes(self):
        self.assertEqual(self.collation.get_base_wit("424T*"), "424")

    def test_merged_attestations(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K3V14U14-28")
        rdg_support = self.collation.readings_by_witness["1910"][vu_ind]
        self.assertEqual(rdg_support, [0.5, 0, 0, 0, 0, 0, 0, 0.5, 0, 0]) # all entries in the reading support vector for this witness to an overlapping reading should be 0

class CollationFillCorrectorLacunaeTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml, fill_corrector_lacunae=True)

    def test_inactive_corrector(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V1U24-26")
        rdg_support = self.collation.readings_by_witness["01C1"][vu_ind]
        self.assertEqual(rdg_support, [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]) # this corrector is inactive in this unit and should default to the first-hand reading

    def test_active_corrector(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V1U24-26")
        rdg_support = self.collation.readings_by_witness["01C2"][vu_ind]
        self.assertEqual(rdg_support, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # this corrector is active in this unit and should have its own reading

class CollationOutputTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse("example/ubs_ephesians.xml", parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective", "orthographic", "subreading"], missing_reading_types=["lac", "overlap"], manuscript_suffixes=["*", "T", "/1", "/2", "/3"], fill_corrector_lacunae=True)

    def test_get_nexus_symbols(self):
        nexus_symbols = self.collation.get_nexus_symbols()
        self.assertEqual(nexus_symbols, ["0", "1", "2", "3", "4", "5", "6", "7", "8"])

    def test_to_numpy_ignore_missing(self):
        matrix, reading_labels, witness_labels = self.collation.to_numpy(split_missing=False)
        self.assertTrue(matrix.sum(axis=0)[0] < len(self.collation.substantive_variation_unit_ids)) # lacuna in the first witness should result in its column summing to less than the total number of substantive variation units

    def test_to_numpy_split_missing(self):
        matrix, reading_labels, witness_labels = self.collation.to_numpy(split_missing=True)
        self.assertTrue(abs(matrix.sum(axis=0)[0] - len(self.collation.substantive_variation_unit_ids) < 1e-4)) # the column for the first witness should sum to the total number of substantive variation units (give or take some rounding error)

if __name__ == '__main__':
    unittest.main()