import unittest
from unittest.mock import patch
from io import StringIO
from pathlib import Path
from lxml import etree as et

from teiphy import Collation

root_dir = Path("__file__").parent.parent
input_example = root_dir/"example/ubs_ephesians.xml"

class CollationDefaultTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
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
        xml = et.parse(input_example, parser=parser)
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
        xml = et.parse(input_example, parser=parser)
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
        xml = et.parse(input_example, parser=parser)
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
        xml = et.parse(input_example, parser=parser)
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
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml, missing_reading_types=["lac", "overlap"])
    
    def test_missing_lac(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V1U24-26")
        rdg_support = self.collation.readings_by_witness["01C1"][vu_ind]
        self.assertEqual(sum(rdg_support), 0) # all entries in the reading support vector for this lacunose witness should be 0

    def test_missing_overlap(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V6U22-26")
        rdg_support = self.collation.readings_by_witness["1398"][vu_ind]
        self.assertEqual(sum(rdg_support), 0) # all entries in the reading support vector for this witness to an overlapping reading should be 0

    def test_missing_get_readings_by_witness_for_unit(self):
        vu = self.collation.variation_units[0]
        assert vu.id == "B10K1V1U24-26"
        result = self.collation.get_readings_by_witness_for_unit(vu)
        assert(len(result) == 223)


class CollationManuscriptSuffixesTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
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
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml, fill_corrector_lacunae=True)

    def test_inactive_corrector(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V1U24-26")
        rdg_support = self.collation.readings_by_witness["01C1"][vu_ind]
        self.assertEqual(rdg_support, [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]) # this corrector is inactive in this unit and should default to the first-hand reading

    def test_active_corrector(self):
        vu_ind = self.collation.substantive_variation_unit_ids.index("B10K1V1U24-26")
        rdg_support = self.collation.readings_by_witness["01C2"][vu_ind]
        self.assertEqual(rdg_support, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # this corrector is active in this unit and should have its own reading

class CollationVerboseTestCase(unittest.TestCase):
    def test_verbose(self):
        with patch("sys.stdout", new = StringIO()) as out:
            parser = et.XMLParser(remove_comments=True)
            xml = et.parse(input_example, parser=parser)
            self.collation = Collation(xml, verbose=True)
            self.assertTrue(out.getvalue().startswith("Initializing collation..."))

class CollationOutputTestCase(unittest.TestCase):
    def setUp(self):
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_example, parser=parser)
        self.collation = Collation(xml, trivial_reading_types=["reconstructed", "defective", "orthographic", "subreading"], missing_reading_types=["lac", "overlap"], manuscript_suffixes=["*", "T", "/1", "/2", "/3"], fill_corrector_lacunae=True)

    def test_get_nexus_symbols(self):
        nexus_symbols = self.collation.get_nexus_symbols()
        self.assertEqual(nexus_symbols, ["0", "1", "2", "3", "4", "5", "6", "7", "8"])

    def test_get_nexus_symbols_empty(self):
        empty_xml = et.fromstring("<TEI/>")
        empty_collation = Collation(empty_xml)
        nexus_symbols = empty_collation.get_nexus_symbols()
        self.assertEqual(nexus_symbols, [])

    def test_to_numpy_ignore_missing(self):
        matrix, reading_labels, witness_labels = self.collation.to_numpy(split_missing=False)
        self.assertTrue(matrix.sum(axis=0)[0] < len(self.collation.substantive_variation_unit_ids)) # lacuna in the first witness should result in its column summing to less than the total number of substantive variation units

    def test_to_numpy_split_missing(self):
        matrix, reading_labels, witness_labels = self.collation.to_numpy(split_missing=True)
        self.assertTrue(abs(matrix.sum(axis=0)[0] - len(self.collation.substantive_variation_unit_ids) < 1e-4)) # the column for the first witness should sum to the total number of substantive variation units (give or take some rounding error)

if __name__ == '__main__':
    unittest.main()