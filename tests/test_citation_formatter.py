import unittest
from citation_formatter import CitationFormatter


class TestCitationFormatter(unittest.TestCase):

    def setUp(self):
        self.formatter = CitationFormatter()

    def test_ieee_formatting(self):
        res = self.formatter.format_ieee("Deep Learning Advances", "Ziwei Liu, Ping Luo", "2023", "arXiv", "http://arxiv.org/abs/1234")
        self.assertIn("Ziwei Liu and Ping Luo", res)
        self.assertIn('"Deep Learning Advances,"', res)
        self.assertIn("arXiv, 2023", res)

    def test_apa_formatting(self):
        res = self.formatter.format_apa("Quantum Computing Overview", "David Hsu", "2024", "IEEE Science", "https://doi.org/10.1038")
        self.assertIn("Hsu, D.", res)
        self.assertIn("(2024)", res)
        self.assertIn("Quantum Computing Overview.", res)

    def test_bibtex_formatting(self):
        res = self.formatter.format_bibtex("Neural Networks", "Yuhong Deng", "2022", "OpenAlex", "https://openalex.org/W123")
        self.assertIn("@article{deng2022,", res)
        self.assertIn("author = {Yuhong Deng}", res)
        self.assertIn("journal = {OpenAlex}", res)


if __name__ == "__main__":
    unittest.main()
