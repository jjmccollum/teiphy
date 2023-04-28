import unittest
from unittest.mock import patch
from io import StringIO
from pathlib import Path
from datetime import datetime
import numpy as np
from lxml import etree as et

from teiphy import tei_ns, Collation

test_dir = Path(__file__).parent
root_dir = test_dir.parent
input_example = root_dir / "example/ubs_ephesians.xml"
malformed_categories_example = test_dir / "malformed_categories_example.xml"


class CollationDefaultTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.xml_witnesses = xml.xpath("//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
        self.xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})
        self.xml_readings = xml.xpath("//tei:rdg", namespaces={"tei": tei_ns})
        self.xml_intrinsic_relations = xml.xpath(
            "//tei:interpGrp[@type=\"intrinsic\"]/tei:interp", namespaces={"tei": tei_ns}
        )
        self.xml_transcriptional_relations = xml.xpath(
            "//tei:interpGrp[@type=\"transcriptional\"]/tei:interp", namespaces={"tei": tei_ns}
        )
        self.collation = Collation(xml)

    def test_witnesses(self):
        self.assertEqual(len(self.collation.witnesses), len(self.xml_witnesses))

    def test_witness_index_by_id(self):
        self.assertEqual(len(self.collation.witness_index_by_id), len(self.xml_witnesses))

    def test_variation_units(self):
        self.assertEqual(len(self.collation.variation_units), len(self.xml_variation_units))

    def test_readings_by_witness(self):
        self.assertEqual(len(self.collation.readings_by_witness), len(self.xml_witnesses))

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(len(self.collation.variation_unit_ids), len(self.xml_variation_units))

    def test_substantive_readings_by_variation_unit_id(self):
        self.assertEqual(len(self.collation.substantive_readings_by_variation_unit_id), len(self.xml_variation_units))

    def test_substantive_variation_unit_reading_tuples(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_reading_tuples), len(self.xml_readings))

    def test_intrinsic_categories(self):
        self.assertEqual(len(self.collation.intrinsic_categories), len(self.xml_intrinsic_relations))

    def test_intrinsic_odds_by_id(self):
        self.assertEqual(len(self.collation.intrinsic_odds_by_id), len(self.xml_intrinsic_relations))

    def test_transcriptional_categories(self):
        self.assertEqual(len(self.collation.transcriptional_categories), len(self.xml_transcriptional_relations))

    def test_transcriptional_rates_by_id(self):
        self.assertEqual(len(self.collation.transcriptional_rates_by_id), len(self.xml_transcriptional_relations))

    def test_origin_date_range(self):
        self.assertEqual(self.collation.origin_date_range[0], 50)
        self.assertEqual(self.collation.origin_date_range[1], 80)


class CollationMalformedCategoriesTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(malformed_categories_example, parser=parser)
        self.xml_intrinsic_relations = xml.xpath(
            "//tei:interpGrp[@type=\"intrinsic\"]/tei:interp", namespaces={"tei": tei_ns}
        )
        self.xml_transcriptional_relations = xml.xpath(
            "//tei:interpGrp[@type=\"transcriptional\"]/tei:interp", namespaces={"tei": tei_ns}
        )
        self.collation = Collation(xml)

    def test_intrinsic_categories(self):
        self.assertEqual(len(self.collation.intrinsic_categories), len(self.xml_intrinsic_relations) - 1)

    def test_transcriptional_categories(self):
        self.assertEqual(len(self.collation.transcriptional_categories), len(self.xml_transcriptional_relations) - 1)


class CollationWhenDateTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml)

    def test_origin_date_range(self):
        source_desc_xml = et.fromstring(
            "<fileDesc xmlns:tei=\"%s\"><tei:sourceDesc><tei:bibl><tei:title>Πρὸς Ἐφεσίους</tei:title><tei:date when=\"50\"/></tei:bibl></tei:sourceDesc></fileDesc>"
            % tei_ns
        )
        self.collation.parse_origin_date_range(source_desc_xml)
        self.assertEqual(self.collation.origin_date_range[0], 50)
        self.assertEqual(self.collation.origin_date_range[1], 50)


class CollationFromToDatesTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml)

    def test_origin_date_range(self):
        source_desc_xml = et.fromstring(
            "<fileDesc xmlns:tei=\"%s\"><tei:sourceDesc><tei:bibl><tei:title>Πρὸς Ἐφεσίους</tei:title><tei:date from=\"50\" to=\"80\"/></tei:bibl></tei:sourceDesc></fileDesc>"
            % tei_ns
        )
        self.collation.parse_origin_date_range(source_desc_xml)
        self.assertEqual(self.collation.origin_date_range[0], 80)
        self.assertEqual(self.collation.origin_date_range[1], 80)


class CollationDateRangeStartOnlyTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml)

    def test_origin_date_range(self):
        source_desc_xml = et.fromstring(
            "<fileDesc xmlns:tei=\"%s\"><tei:sourceDesc><tei:bibl><tei:title>Πρὸς Ἐφεσίους</tei:title><tei:date notBefore=\"50\"/></tei:bibl></tei:sourceDesc></fileDesc>"
            % tei_ns
        )
        self.collation.parse_origin_date_range(source_desc_xml)
        self.assertEqual(self.collation.origin_date_range[0], 50)
        self.assertEqual(self.collation.origin_date_range[1], datetime.now().year)


class CollationDateRangeEndOnlyTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml)

    def test_origin_date_range(self):
        source_desc_xml = et.fromstring(
            "<fileDesc xmlns:tei=\"%s\"><tei:sourceDesc><tei:bibl><tei:title>Πρὸς Ἐφεσίους</tei:title><tei:date notAfter=\"80\"/></tei:bibl></tei:sourceDesc></fileDesc>"
            % tei_ns
        )
        self.collation.parse_origin_date_range(source_desc_xml)
        self.assertIsNone(self.collation.origin_date_range[0])
        self.assertEqual(self.collation.origin_date_range[1], 80)


class CollationNoDatesTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml)

    def test_origin_date_range(self):
        source_desc_xml = et.fromstring(
            "<fileDesc xmlns:tei=\"%s\"><tei:sourceDesc><tei:bibl><tei:title>Πρὸς Ἐφεσίους</tei:title></tei:bibl></tei:sourceDesc></fileDesc>"
            % tei_ns
        )
        # After the parse_origin_date_range method is called, the origin date upper bound should default to the current year:
        self.collation.parse_origin_date_range(source_desc_xml)
        self.assertIsNone(self.collation.origin_date_range[0])
        self.assertEqual(self.collation.origin_date_range[1], datetime.now().year)


class CollationTrivialReconstructedTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.xml_readings = xml.xpath("//tei:rdg[not(@type) or @type!=\"reconstructed\"]", namespaces={"tei": tei_ns})
        self.collation = Collation(xml, trivial_reading_types=["reconstructed"])

    def test_substantive_variation_unit_reading_tuples(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_reading_tuples), len(self.xml_readings))


class CollationTrivialDefectiveTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.xml_readings = xml.xpath(
            "//tei:rdg[not(@type) or (@type!=\"reconstructed\" and @type!=\"defective\")]", namespaces={"tei": tei_ns}
        )
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective"])

    def test_substantive_variation_unit_reading_tuples(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_reading_tuples), len(self.xml_readings))


class CollationTrivialOrthographicTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.xml_readings = xml.xpath(
            "//tei:rdg[not(@type) or (@type!=\"reconstructed\" and @type!=\"defective\" and @type !=\"orthographic\")]",
            namespaces={"tei": tei_ns},
        )
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective", "orthographic"])

    def test_substantive_variation_unit_reading_tuples(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_reading_tuples), len(self.xml_readings))


class CollationTrivialSubreadingTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.xml_readings = xml.xpath(
            "//tei:rdg[not(@type) or (@type!=\"reconstructed\" and @type!=\"defective\" and @type !=\"orthographic\" and @type !=\"subreading\")]",
            namespaces={"tei": tei_ns},
        )
        self.collation = Collation(
            xml, trivial_reading_types=["reconstructed", "defective", "orthographic", "subreading"]
        )

    def test_substantive_variation_unit_reading_tuples(self):
        self.assertEqual(len(self.collation.substantive_variation_unit_reading_tuples), len(self.xml_readings))


class CollationMissingTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml, missing_reading_types=["lac", "overlap"])

    def test_missing_lac(self):
        vu_ind = self.collation.variation_unit_ids.index("B10K1V1U24-26")
        rdg_support = self.collation.readings_by_witness["04"][vu_ind]
        self.assertEqual(
            sum(rdg_support), 0
        )  # all entries in the reading support vector for this lacunose witness should be 0

    def test_missing_overlap(self):
        vu_ind = self.collation.variation_unit_ids.index("B10K3V20U8-10")
        rdg_support = self.collation.readings_by_witness["606"][vu_ind]
        self.assertEqual(
            sum(rdg_support), 0
        )  # all entries in the reading support vector for this witness to an overlapping reading should be 0

    def test_missing_get_readings_by_witness_for_unit(self):
        vu = self.collation.variation_units[0]
        assert vu.id == "B10K1V1U24-26"
        result = self.collation.get_readings_by_witness_for_unit(vu)
        assert len(result) == 38


class CollationManuscriptSuffixesTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(
            xml, manuscript_suffixes=["*", "T", "C", "C0", "C1", "C2", "C2a", "C2b", "A", "/1", "/2", "/3"]
        )

    def test_get_base_wit_no_suffix(self):
        self.assertEqual(self.collation.get_base_wit("424"), "424")

    def test_get_base_wit_apparent_suffix(self):
        self.assertEqual(
            self.collation.get_base_wit("424C"), "424C"
        )  # "C" is a suffix, but "424C" is a distinct witness

    def test_get_base_wit_one_suffix(self):
        self.assertEqual(self.collation.get_base_wit("424*"), "424")

    def test_get_base_wit_multiple_suffixes(self):
        self.assertEqual(self.collation.get_base_wit("424T*"), "424")

    def test_merged_attestations(self):
        vu_ind = self.collation.variation_unit_ids.index("B10K3V14U14-18")
        rdg_support = self.collation.readings_by_witness["1910"][vu_ind]
        self.assertEqual(
            rdg_support, [1, 1, 0]
        )  # all entries in the reading support vector for this witness with multiple attestations should have all attested readings supported


class CollationFillCorrectorLacunaeTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(
            xml, missing_reading_types=["overlap", "lac"], manuscript_suffixes=["*", "T"], fill_corrector_lacunae=True
        )

    def test_inactive_corrector(self):
        vu_ind = self.collation.variation_unit_ids.index("B10K4V8U12-18")
        rdg_support = self.collation.readings_by_witness["06C1"][vu_ind]
        self.assertEqual(
            rdg_support, [0, 0, 1, 0, 0, 0, 0, 0, 0]
        )  # this corrector is inactive in this unit and should default to the first-hand reading

    def test_active_corrector(self):
        vu_ind = self.collation.variation_unit_ids.index("B10K4V8U12-18")
        rdg_support = self.collation.readings_by_witness["06C2"][vu_ind]
        self.assertEqual(
            rdg_support, [0, 0, 0, 0, 0, 1, 0, 0, 0]
        )  # this corrector is active in this unit and should have its own reading


class CollationVerboseTestCase(unittest.TestCase):
    def test_verbose(self):
        with patch("sys.stdout", new=StringIO()) as out:
            parser = et.XMLParser(remove_comments=True)
            xml = et.parse(input_example, parser=parser)
            self.collation = Collation(xml, verbose=True)
            self.assertTrue(out.getvalue().startswith("Initializing collation..."))


class CollationOutputTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})
        self.collation = Collation(
            xml,
            trivial_reading_types=["reconstructed", "defective", "orthographic", "subreading"],
            missing_reading_types=["lac", "overlap"],
            manuscript_suffixes=["*", "T", "/1", "/2", "/3"],
            fill_corrector_lacunae=True,
        )

    def test_get_nexus_symbols(self):
        nexus_symbols = self.collation.get_nexus_symbols()
        self.assertEqual(nexus_symbols, ["0", "1", "2", "3", "4", "5"])

    def test_get_nexus_symbols_empty(self):
        empty_collation = self.collation
        empty_collation.witnesses = []
        nexus_symbols = empty_collation.get_nexus_symbols()
        self.assertEqual(nexus_symbols, [])

    # def test_get_nexus_equates(self):
    #     nexus_symbols = self.collation.get_nexus_symbols()
    #     equates, equate_mapping = self.collation.get_nexus_equates(nexus_symbols)
    #     self.assertEqual(equates, ["9", "a", "b", "c", "d", "e", "f"])
    #     self.assertEqual(
    #         equate_mapping,
    #         {(0, 1): "9", (0, 1, 2): "a", (0, 1, 2, 3): "b", (0, 2): "c", (0, 3): "d", (0, 4): "e", (3, 4): "f"},
    #     )

    # def test_get_nexus_equates_empty(self):
    #     empty_collation = self.collation
    #     empty_collation.witnesses = []
    #     nexus_symbols = empty_collation.get_nexus_symbols()
    #     equates, equate_mapping = empty_collation.get_nexus_equates(nexus_symbols)
    #     self.assertEqual(equates, [])
    #     self.assertEqual(equate_mapping, {})

    def test_get_hennig86_symbols(self):
        hennig86_symbols = self.collation.get_hennig86_symbols()
        self.assertEqual(hennig86_symbols, ["0", "1", "2", "3", "4", "5"])

    def test_get_hennig86_symbols_empty(self):
        empty_collation = self.collation
        empty_collation.witnesses = []
        hennig86_symbols = empty_collation.get_hennig86_symbols()
        self.assertEqual(hennig86_symbols, [])

    def test_get_phylip_symbols(self):
        phylip_symbols = self.collation.get_phylip_symbols()
        self.assertEqual(phylip_symbols, ["0", "1", "2", "3", "4", "5"])

    def test_get_phylip_symbols_empty(self):
        empty_collation = self.collation
        empty_collation.witnesses = []
        phylip_symbols = empty_collation.get_phylip_symbols()
        self.assertEqual(phylip_symbols, [])

    def test_get_fasta_symbols(self):
        fasta_symbols = self.collation.get_fasta_symbols()
        self.assertEqual(fasta_symbols, ["0", "1", "2", "3", "4", "5"])

    def test_get_fasta_symbols_empty(self):
        empty_collation = self.collation
        empty_collation.witnesses = []
        fasta_symbols = empty_collation.get_fasta_symbols()
        self.assertEqual(fasta_symbols, [])

    def test_get_beast_symbols(self):
        beast_symbols = self.collation.get_beast_symbols()
        self.assertEqual(beast_symbols, ["0", "1", "2", "3", "4", "5"])

    def test_get_beast_symbols_empty(self):
        empty_collation = self.collation
        empty_collation.witnesses = []
        beast_symbols = empty_collation.get_beast_symbols()
        self.assertEqual(beast_symbols, [])

    def test_to_numpy_ignore_missing(self):
        matrix, reading_labels, witness_labels = self.collation.to_numpy(split_missing=False)
        self.assertTrue(
            matrix.sum(axis=0)[5] < len(self.collation.variation_unit_ids)
        )  # lacuna in the first witness should result in its column summing to less than the total number of substantive variation units

    def test_to_numpy_split_missing(self):
        matrix, reading_labels, witness_labels = self.collation.to_numpy(split_missing=True)
        self.assertTrue(
            abs(matrix.sum(axis=0)[5] - len(self.collation.variation_unit_ids)) < 1e-4
        )  # the column for the first witness should sum to the total number of substantive variation units (give or take some rounding error)

    def test_to_distance_matrix(self):
        matrix, witness_labels = self.collation.to_distance_matrix()
        self.assertEqual(np.trace(matrix), 0)  # diagonal entries should be 0
        self.assertTrue(np.all(matrix == matrix.T))  # matrix should be symmetrical
        self.assertEqual(
            matrix[0, 1], 13
        )  # entry for UBS and P46 should be 13 (remember not to count P46 lacunae and ambiguities and P46 defective readings under the UBS reading)

    def test_to_distance_matrix_drop_constant(self):
        matrix, witness_labels = self.collation.to_distance_matrix(drop_constant=True)
        self.assertEqual(np.trace(matrix), 0)  # diagonal entries should be 0
        self.assertTrue(np.all(matrix == matrix.T))  # matrix should be symmetrical
        self.assertEqual(
            matrix[0, 1], 13
        )  # entry for UBS and P46 should be 13 (remember not to count P46 lacunae and ambiguities and P46 defective readings under the UBS reading)

    def test_to_distance_matrix_proportion(self):
        matrix, witness_labels = self.collation.to_distance_matrix(proportion=True)
        self.assertEqual(np.trace(matrix), 0)  # diagonal entries should be 0
        self.assertTrue(np.all(matrix == matrix.T))  # matrix should be symmetrical
        self.assertTrue(np.all(matrix >= 0.0) and np.all(matrix <= 1.0))  # all elements should be between 0 and 1
        self.assertTrue(
            abs(matrix[0, 1] - 13 / (len(self.xml_variation_units) - 2)) < 1e-4
        )  # entry for UBS and P46 should be 13 divided by the number of variation units where neither witness is lacunose or ambiguous

    def test_to_distance_matrix_drop_constant_proportion(self):
        matrix, witness_labels = self.collation.to_distance_matrix(drop_constant=True, proportion=True)
        self.assertEqual(np.trace(matrix), 0)  # diagonal entries should be 0
        self.assertTrue(np.all(matrix == matrix.T))  # matrix should be symmetrical
        self.assertTrue(np.all(matrix >= 0.0) and np.all(matrix <= 1.0))  # all elements should be between 0 and 1
        self.assertTrue(
            abs(matrix[0, 1] - 13 / (len(self.xml_variation_units) - 2 - 2)) < 1e-4
        )  # entry for UBS and P46 should be 13 divided by the number of non-constant variation units where neither witness is lacunose or ambiguous

    def test_to_long_table(self):
        long_table, column_labels = self.collation.to_long_table()
        self.assertEqual(
            column_labels, ["taxon", "character", "state", "value"]
        )  # lacuna in the first witness should result in its column summing to less than the total number of substantive variation units
        self.assertEqual(long_table[0, 0], "UBS")  # first row should contain UBS,B10K1V1U24-26,0,εν εφεσω
        self.assertEqual(long_table[0, 1], "B10K1V1U24-26")  # first row should contain UBS,B10K1V1U24-26,0,εν εφεσω
        self.assertEqual(long_table[0, 2], "0")  # first row should contain UBS,B10K1V1U24-26,0,εν εφεσω
        self.assertEqual(long_table[0, 3], "εν εφεσω")  # first row should contain UBS,B10K1V1U24-26,0,εν εφεσω


if __name__ == '__main__':
    unittest.main()
