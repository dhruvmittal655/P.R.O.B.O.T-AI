import unittest

from database import Database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.database = Database(":memory:")

    def tearDown(self):
        self.database.close()

    def test_article_lifecycle(self):
        self.database.save_article("Python", "Python is a language.")

        article = self.database.get_article("Python")
        self.assertIsNotNone(article)
        self.assertEqual(article[2], "Python is a language.")
        self.assertTrue(self.database.article_exists("Python"))

        self.database.add_favorite("Python")
        self.assertEqual(self.database.get_favorites(), [("Python",)])

        self.database.update_views("Python")
        self.assertEqual(self.database.get_most_viewed()[0][0], "Python")

    def test_local_title_search(self):
        self.database.save_article("Python Programming", "Article")

        self.assertEqual(
            self.database.search_titles("python"),
            [("Python Programming",)]
        )

    def test_research_source_replacement(self):
        self.database.save_research_source(
            "Python", "arXiv Papers", "https://example.test", "First", "now"
        )
        self.database.save_research_source(
            "Python", "arXiv Papers", "https://example.test", "Updated", "later"
        )

        self.assertEqual(
            self.database.get_research_sources("Python"),
            [("arXiv Papers", "https://example.test", "Updated")]
        )


if __name__ == "__main__":
    unittest.main()
