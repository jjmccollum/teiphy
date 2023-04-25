import unittest
from datetime import datetime
from lxml import etree as et

from teiphy import tei_ns, Witness


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

    def test_init_date_range_when(self):
        xml = et.fromstring("<witness xmlns:tei=\"%s\" n=\"18\"><tei:origDate when=\"1364\"/></witness>" % tei_ns)
        witness = Witness(xml)
        self.assertEqual(witness.date_range[0], 1364)
        self.assertEqual(witness.date_range[1], 1365)

    def test_init_date_range_from_to(self):
        xml = et.fromstring(
            "<witness xmlns:tei=\"%s\" type=\"father\" n=\"Ambrosiaster\"><tei:origDate from=\"366\" to=\"384\"/></witness>"
            % tei_ns
        )
        witness = Witness(xml)
        # from and to indicate the time during which a witness was being produced, so the upper and lower bounds should both be set to the time when the work was finished:
        self.assertEqual(witness.date_range[0], 384)
        self.assertEqual(witness.date_range[1], 385)

    def test_init_date_range_not_before_not_after(self):
        xml = et.fromstring(
            "<witness xmlns:tei=\"%s\" type=\"father\" n=\"Ambrosiaster\"><tei:origDate notBefore=\"366\" notAfter=\"384\"/></witness>"
            % tei_ns
        )
        witness = Witness(xml)
        self.assertEqual(witness.date_range[0], 366)
        self.assertEqual(witness.date_range[1], 384)

    def test_init_date_range_empty(self):
        xml = et.fromstring("<witness xmlns:tei=\"%s\" n=\"A\"/>" % tei_ns)
        witness = Witness(xml)
        self.assertIsNone(witness.date_range[0])
        self.assertEqual(witness.date_range[1], datetime.now().year)

    def test_init_date_range_start_only(self):
        xml = et.fromstring("<witness xmlns:tei=\"%s\" n=\"A\"><tei:origDate notBefore=\"50\"/></witness>" % tei_ns)
        witness = Witness(xml)
        self.assertEqual(witness.date_range[0], 50)
        self.assertEqual(witness.date_range[1], datetime.now().year)

    def test_init_date_range_end_only(self):
        xml = et.fromstring("<witness xmlns:tei=\"%s\" n=\"A\"><tei:origDate notAfter=\"100\"/></witness>" % tei_ns)
        witness = Witness(xml)
        self.assertIsNone(witness.date_range[0])
        self.assertEqual(witness.date_range[1], 100)


if __name__ == '__main__':
    unittest.main()
