import unittest

from teiphy import Format


class FormatTestCase(unittest.TestCase):
    def test_infer_success(self):
        self.assertEqual(Format.infer(".nex"), Format.NEXUS)
        self.assertEqual(Format.infer(".nxs"), Format.NEXUS)
        self.assertEqual(Format.infer(".nexus"), Format.NEXUS)
        self.assertEqual(Format.infer(".tnt"), Format.HENNIG86)
        self.assertEqual(Format.infer(".csv"), Format.CSV)
        self.assertEqual(Format.infer(".tsv"), Format.TSV)
        self.assertEqual(Format.infer(".xlsx"), Format.EXCEL)

    def test_infer_failure(self):
        self.assertRaises(Exception, Format.infer, ".unk")


if __name__ == '__main__':
    unittest.main()
