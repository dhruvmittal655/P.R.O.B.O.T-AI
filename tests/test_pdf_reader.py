import unittest
import os
from pdf_reader import PDFReader


class TestPDFReader(unittest.TestCase):

    def setUp(self):
        self.reader = PDFReader()

    def test_nonexistent_pdf(self):
        res = self.reader.extract_pdf_details("nonexistent_file_12345.pdf")
        self.assertIsNone(res)

    def test_format_size(self):
        self.assertEqual(self.reader._format_size(500), "500 Bytes")
        self.assertEqual(self.reader._format_size(2048), "2.0 KB")
        self.assertEqual(self.reader._format_size(2097152), "2.0 MB")


if __name__ == "__main__":
    unittest.main()
