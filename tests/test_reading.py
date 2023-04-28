import unittest
from lxml import etree as et

from teiphy import Reading


class ReadingTestCase(unittest.TestCase):
    def test_init_rdg_xml_id(self):
        xml = et.fromstring("<rdg xml:id=\"B10K1V1U2R1\" n=\"1\"><w>παυλος</w></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.id, "B10K1V1U2R1")

    def test_init_rdg_n_id(self):
        xml = et.fromstring("<rdg n=\"1\"><w>παυλος</w></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.id, "1")

    def test_init_rdg_text_id(self):
        xml = et.fromstring("<lem><w>παυλος</w></lem>")  # lem elements should be processed like rdg elements
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.id, "παυλος")

    def test_init_wit_detail_xml_id(self):
        xml = et.fromstring("<witDetail xml:id=\"B10K1V1U2RW1-2\"/>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.id, "B10K1V1U2RW1-2")

    def test_init_wit_detail_n_id(self):
        xml = et.fromstring("<witDetail n=\"Z\"/>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.id, "Z")

    def test_init_wit_detail_text_id(self):
        xml = et.fromstring("<witDetail type=\"lac\"/>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.id, "")

    def test_init_type_default(self):
        xml = et.fromstring("<rdg n=\"1\"><w>εν</w><w>εφεσω</w></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.type, "substantive")

    def test_init_type_specified(self):
        xml = et.fromstring("<rdg n=\"1-v1\" type=\"reconstructed\"><w>εν</w><w><unclear>ε</unclear>φεσω</w></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.type, "reconstructed")

    def test_init_wits_id(self):
        xml = et.fromstring(
            "<rdg n=\"1-v1\" type=\"reconstructed\" wit=\"#L2010\"><w>εν</w><w><unclear>ε</unclear>φεσω</w></rdg>"
        )
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.wits, ["L2010"])

    def test_init_wits_n(self):
        xml = et.fromstring("<rdg n=\"2\" wit=\"P46 01* 03* 6 424C1 1739 BasilOfCaesarea Ephrem Marcion Origen\"/>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(
            reading.wits, ["P46", "01*", "03*", "6", "424C1", "1739", "BasilOfCaesarea", "Ephrem", "Marcion", "Origen"]
        )

    def test_init_targets_id(self):
        xml = et.fromstring("<witDetail target=\"#B10K1V1U2R1 #B10K1V1U2R2\"/>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.targets, ["B10K1V1U2R1", "B10K1V1U2R2"])

    def test_init_targets_n(self):
        xml = et.fromstring("<witDetail target=\"1 2 3\"/>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.targets, ["1", "2", "3"])

    def test_init_certainties_default(self):
        xml = et.fromstring("<witDetail target=\"1 2\"/>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.certainties, {"1": 0.0, "2": 0.0})

    def test_init_certainties_specified(self):
        xml = et.fromstring(
            "<witDetail target=\"1 2\"><certainty target=\"1\" degree=\"0.75\"/><certainty target=\"2\" degree=\"0.25\"/></witDetail>"
        )
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.certainties, {"1": 0.75, "2": 0.25})

    def test_init_text_empty(self):
        xml = et.fromstring("<rdg/>")  # lem elements should be processed like rdg elements
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "")

    def test_init_text_unclear_supplied(self):
        xml = et.fromstring(
            "<rdg n=\"2-v2\" type=\"reconstructed\" wit=\"94\"><w><unclear>π</unclear><supplied reason=\"lacuna\">ρω</supplied>τον</w></rdg>"
        )
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "π̣[ρω]τον")

    def test_init_text_abbr_hi(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><w><abbr><hi rend=\"overline\">θυ</hi></abbr></w></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "θ̅υ̅")

    def test_init_text_ex(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><w>πα<ex>ρα</ex></w></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "πα(ρα)")

    def test_init_text_unclear_ex(self):
        xml = et.fromstring(
            "<rdg n=\"1-v1\" type=\"reconstructed\" wit=\"1\"><w>πα<unclear><ex>ρα</ex></unclear></w></rdg>"
        )
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "πα(̣ρ̣α̣)̣")

    def test_init_text_supplied_abbr_hi(self):
        xml = et.fromstring(
            "<rdg n=\"1-v2\" type=\"reconstructed\" wit=\"2\"><w><supplied reason=\"illegible\"><abbr><hi rend=\"overline\">θυ</hi></abbr></supplied></w></rdg>"
        )
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[θ̅υ̅]")

    def test_init_text_space_extent_reason(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><space unit=\"char\" extent=\"2-4\" reason=\"erased\"/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[2-4 char space (erased)]")

    def test_init_text_space_extent(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><space unit=\"line\" extent=\"part\"/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[part line space]")

    def test_init_text_space_reason(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><space reason=\"erased\"/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[space (erased)]")

    def test_init_text_space(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><space/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[space]")

    def test_init_text_gap_extent_reason(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><gap unit=\"verse\" extent=\"part\" reason=\"lacuna\"/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[part verse gap (lacuna)]")

    def test_init_text_gap_extent(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><gap unit=\"char\" extent=\"10\"/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[10 char gap]")

    def test_init_text_gap_reason(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><gap reason=\"illegible\"/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[... (illegible)]")

    def test_init_text_gap(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><gap/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[...]")

    def test_init_text_choice(self):
        xml = et.fromstring(
            "<rdg n=\"1\" wit=\"A\"><w><choice><unclear>οτι</unclear><unclear>ετι</unclear></choice></w></rdg>"
        )
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "[ο̣τ̣ι̣/ε̣τ̣ι̣]")

    def test_init_text_ref(self):
        xml = et.fromstring("<rdg n=\"1\" wit=\"A\"><ref target=\"#B1K1V1U2\"/><ref target=\"#B1K1V1U4\"/></rdg>")
        reading = Reading(xml, verbose=True)
        self.assertEqual(reading.text, "(B1K1V1U2)(B1K1V1U4)")


if __name__ == '__main__':
    unittest.main()
