import unittest

from teiphy import Format


class FormatTestCase(unittest.TestCase):
    def test_infer_success(self):
        self.assertEqual(Format.infer(".csv"), Format.CSV)

    def test_infer_failure(self):
        self.assertRaises(Exception, Format.infer, ".unk")


if __name__ == '__main__':
    unittest.main()
