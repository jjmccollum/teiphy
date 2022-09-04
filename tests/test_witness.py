import unittest
from lxml import etree as et

from teiphy import Witness


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


if __name__ == '__main__':
    unittest.main()
