import unittest
from unittest.mock import patch
from io import StringIO
from pathlib import Path
import numpy as np
from lxml import etree as et

from teiphy import Collation

root_dir = Path("__file__").parent.parent
input_example = root_dir / "example/ubs_ephesians.xml"


class CollationDefaultTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml)

    def test_witnesses(self):
        self.assertEqual(len(self.collation.witnesses), 38)

    def test_witness_index_by_id(self):
        self.assertEqual(len(self.collation.witness_index_by_id), 38)

    def test_variation_units(self):
        self.assertEqual(len(self.collation.variation_units), 42)

    def test_readings_by_witness(self):
        self.assertEqual(len(self.collation.readings_by_witness), 38)

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_ids), 40
        )  # apps B10K4V28U24-26 and B10K6V20U12 should always be ignored

    def test_substantive_reading_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_reading_tuples), 160
        )  # all readings except for the ones in apps B10K4V28U24-26 and B10K6V20U12


class CollationTrivialReconstructedTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed"])

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_ids), 40
        )  # apps B10K4V28U24-26 and B10K6V20U12 should always be ignored

    def test_substantive_reading_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_reading_tuples), 147
        )  # all readings except for the ones in apps B10K4V28U24-26 and B10K6V20U12 and all reconstructed readings


class CollationTrivialDefectiveTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective"])

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_ids), 40
        )  # apps B10K4V28U24-26 and B10K6V20U12 should always be ignored

    def test_substantive_reading_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_reading_tuples), 108
        )  # all readings except for the ones in apps B10K4V28U24-26 and B10K6V20U12 and all reconstructed and defective readings


class CollationTrivialOrthographicTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective", "orthographic"])

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_ids), 40
        )  # all units except B10K6V20U12 and B10K4V28U24-26

    def test_substantive_reading_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_reading_tuples), 105
        )  # all readings except for the ones in app B10K6V20U12 and B10K4V28U24-26 and all reconstructed, defective, and orthographic readings


class CollationTrivialSubreadingTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(
            xml, trivial_reading_types=["reconstructed", "defective", "orthographic", "subreading"]
        )

    def test_substantive_variation_unit_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_ids), 40
        )  # all units except B10K6V20U12 and B10K4V28U24-26

    def test_substantive_reading_ids(self):
        self.assertEqual(
            len(self.collation.substantive_variation_unit_reading_tuples), 100
        )  # all readings except for the ones in app B10K6V20U12 and B10K4V28U24-26 and all readings that have non-substantive types


class CollationMissingTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml, missing_reading_types=["lac", "overlap"])

    def test_missing_lac(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V1U24-26")
        rdg_support = self.collation.readings_by_witness["04"][vu_ind]
        self.assertEqual(
            sum(rdg_support), 0
        )  # all entries in the reading support vector for this lacunose witness should be 0

    def test_missing_overlap(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K3V20U8-10")
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
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K3V14U14-18")
        rdg_support = self.collation.readings_by_witness["1910"][vu_ind]
        self.assertEqual(
            rdg_support, [0.5, 0.5, 0]
        )  # all entries in the reading support vector for this witness to an overlapping reading should be 0


class CollationFillCorrectorLacunaeTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(
            xml, missing_reading_types=["overlap", "lac"], manuscript_suffixes=["*", "T"], fill_corrector_lacunae=True
        )

    def test_inactive_corrector(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K4V8U12-18")
        rdg_support = self.collation.readings_by_witness["06C1"][vu_ind]
        self.assertEqual(
            rdg_support, [0, 0, 1, 0, 0, 0, 0, 0, 0]
        )  # this corrector is inactive in this unit and should default to the first-hand reading

    def test_active_corrector(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K4V8U12-18")
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
        empty_xml = et.fromstring("<TEI/>")
        empty_collation = Collation(empty_xml)
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
    #     empty_xml = et.fromstring("<TEI/>")
    #     empty_collation = Collation(empty_xml)
    #     nexus_symbols = empty_collation.get_nexus_symbols()
    #     equates, equate_mapping = empty_collation.get_nexus_equates(nexus_symbols)
    #     self.assertEqual(equates, [])
    #     self.assertEqual(equate_mapping, {})

    def test_get_hennig86_symbols(self):
        hennig86_symbols = self.collation.get_hennig86_symbols()
        self.assertEqual(hennig86_symbols, ["0", "1", "2", "3", "4", "5"])

    def test_get_hennig86_symbols_empty(self):
        empty_xml = et.fromstring("<TEI/>")
        empty_collation = Collation(empty_xml)
        hennig86_symbols = empty_collation.get_hennig86_symbols()
        self.assertEqual(hennig86_symbols, [])

    def test_get_phylip_symbols(self):
        phylip_symbols = self.collation.get_phylip_symbols()
        self.assertEqual(phylip_symbols, ["0", "1", "2", "3", "4", "5"])

    def test_get_phylip_symbols_empty(self):
        empty_xml = et.fromstring("<TEI/>")
        empty_collation = Collation(empty_xml)
        phylip_symbols = empty_collation.get_phylip_symbols()
        self.assertEqual(phylip_symbols, [])

    def test_get_fasta_symbols(self):
        fasta_symbols = self.collation.get_fasta_symbols()
        self.assertEqual(fasta_symbols, ["0", "1", "2", "3", "4", "5"])

    def test_get_fasta_symbols_empty(self):
        empty_xml = et.fromstring("<TEI/>")
        empty_collation = Collation(empty_xml)
        fasta_symbols = empty_collation.get_fasta_symbols()
        self.assertEqual(fasta_symbols, [])

    def test_to_numpy_ignore_missing(self):
        matrix, reading_labels, witness_labels = self.collation.to_numpy(split_missing=False)
        self.assertTrue(
            matrix.sum(axis=0)[5] < len(self.collation.substantive_variation_unit_ids)
        )  # lacuna in the first witness should result in its column summing to less than the total number of substantive variation units

    def test_to_numpy_split_missing(self):
        matrix, reading_labels, witness_labels = self.collation.to_numpy(split_missing=True)
        self.assertTrue(
            abs(matrix.sum(axis=0)[5] - len(self.collation.substantive_variation_unit_ids) < 1e-4)
        )  # the column for the first witness should sum to the total number of substantive variation units (give or take some rounding error)

    def test_to_distance_matrix(self):
        matrix, witness_labels = self.collation.to_distance_matrix()
        self.assertEqual(np.trace(matrix), 0)  # diagonal entries should be 0
        self.assertTrue(np.all(matrix == matrix.T))  # matrix should be symmetrical
        self.assertEqual(
            matrix[0, 1], 13
        )  # entry for UBS and P46 should be 13 (remember not to count P46 lacunae and ambiguities, P46 defective readings under the UBS reading, and non-substantive variation units)

    def test_to_distance_matrix_proportion(self):
        matrix, witness_labels = self.collation.to_distance_matrix(proportion=True)
        self.assertEqual(np.trace(matrix), 0)  # diagonal entries should be 0
        self.assertTrue(np.all(matrix == matrix.T))  # matrix should be symmetrical
        self.assertTrue(np.all(matrix >= 0.0) and np.all(matrix <= 1.0))  # all elements should be between 0 and 1
        self.assertTrue(
            abs(matrix[0, 1] - 13 / 38) < 1e-4
        )  # entry for UBS and P46 should be close to 13/38 (of 40 substantive variation units, P46 is lacunose at one and ambiguous at another)


if __name__ == '__main__':
    unittest.main()
