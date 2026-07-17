import unittest
from unittest.mock import MagicMock
from app.llm.schemas import LLMResponse
from app.retrieval.rewriting.query_rewriter import QueryRewriter


class TestQueryRewriter(unittest.TestCase):

    def test_rewrite_basic(self):
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            answer="How does CNN work?",
            model="gemini",
            finish_reason="STOP",
            usage={},
        )

        rewriter = QueryRewriter(mock_llm)
        history = [
            {"role": "USER", "content": "Explain CNN"},
            {
                "role": "ASSISTANT",
                "content": "CNN stands for Convolutional Neural Network...",
            },
        ]

        rewritten = rewriter.rewrite("How does it work?", history)
        self.assertEqual(rewritten, "How does CNN work?")

        # Check prompt composition contains the history elements
        prompt = mock_llm.generate.call_args[0][0]
        self.assertIn("Explain CNN", prompt)
        self.assertIn("How does it work?", prompt)

    def test_rewrite_empty_history(self):
        mock_llm = MagicMock()
        rewriter = QueryRewriter(mock_llm)
        rewritten = rewriter.rewrite("How does it work?", [])
        self.assertEqual(rewritten, "How does it work?")
        mock_llm.generate.assert_not_called()
