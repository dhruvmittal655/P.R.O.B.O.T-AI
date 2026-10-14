import unittest
from unittest.mock import MagicMock
from ai_assistant import SmartAIAssistant


class TestScopedRAG(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.get_all_research_chunks_threadsafe.return_value = [
            ("arXiv: Cloud Computing", "Cloud computing delivers on-demand computing services over the internet."),
            ("PubMed: Quantum Science", "Quantum computing leverages qubits for super-position processing.")
        ]
        self.mock_db.get_all_articles_summaries_threadsafe.return_value = [
            ("Machine Learning", "Machine learning is a subset of AI focusing on data algorithms.")
        ]
        self.ai = SmartAIAssistant(self.mock_db)
        self.ai.current_article = "This is the current open article about Python software architecture."

    def test_scoped_context_current(self):
        ctx = self.ai.get_scoped_rag_context("Python software", scope="current")
        self.assertIsNotNone(ctx)

    def test_scoped_context_global(self):
        ctx = self.ai.get_scoped_rag_context("cloud services", scope="global")
        self.assertIsNotNone(ctx)


if __name__ == "__main__":
    unittest.main()
