import unittest
from app.prompts.builder import PromptBuilder
from app.prompts.formatter import ContextFormatter
from app.prompts.citations import CitationFormatter
from app.prompts.exceptions import PromptTooLargeError
from app.prompts.templates import RAG_SYSTEM_PROMPT


class TestPrompts(unittest.TestCase):

    def setUp(self):
        # Instantiate a builder with custom small limits for easy testing of trimming
        self.builder_small = PromptBuilder(max_tokens=500, max_chunks=3)
        self.builder_normal = PromptBuilder()

    def test_context_formatter(self):
        formatted = ContextFormatter.format_chunk(
            content="This is some content.",
            filename="test_file.pdf",
            page="3",
        )
        expected = (
            "Document: test_file.pdf\n"
            "Page: 3\n"
            "Chunk:\n"
            "This is some content.\n"
        )
        self.assertEqual(formatted, expected)

    def test_citation_formatter(self):
        citation = CitationFormatter.format_citation(
            filename="test_file.pdf",
            page="5",
        )
        self.assertEqual(citation, "Source: test_file.pdf Page 5")

    def test_successful_prompt_build(self):
        chunks = [
            {"content": "Chunk one content.", "filename": "doc1.pdf", "page": "1"},
            {"content": "Chunk two content.", "filename": "doc2.pdf", "page": "2"},
        ]
        prompt = self.builder_normal.build("Explain AI.", chunks)

        self.assertIn("System Instruction", prompt)
        self.assertIn(RAG_SYSTEM_PROMPT, prompt)
        self.assertIn("Context", prompt)
        self.assertIn("Chunk one content.", prompt)
        self.assertIn("Chunk two content.", prompt)
        self.assertIn("Question", prompt)
        self.assertIn("Explain AI.", prompt)
        self.assertIn("Assistant", prompt)

    def test_empty_retrieval(self):
        # Empty context list should still construct a valid prompt
        prompt = self.builder_normal.build("Explain AI.", [])
        self.assertIn("System Instruction", prompt)
        self.assertIn("Context", prompt)
        self.assertIn("Question", prompt)
        self.assertIn("Explain AI.", prompt)

    def test_context_trimming(self):
        # Create chunks that are large enough to exceed our small budget (500 tokens)
        large_chunk_content = "This is a sentence that we will repeat to make it very large. " * 30
        chunks = [
            {"content": large_chunk_content, "filename": "large_doc.pdf", "page": "1"},
            {"content": "Small chunk content that shouldn't be included if we already exceeded budget.", "filename": "doc2.pdf", "page": "2"},
        ]

        # TokenBudgetManager will accept the first chunk but reject the second because it overflows 500 tokens
        prompt = self.builder_small.build("Explain AI.", chunks)
        
        self.assertIn("large_doc.pdf", prompt)
        self.assertNotIn("doc2.pdf", prompt)

    def test_query_too_large_error(self):
        # A query that is excessively large and immediately exceeds the budget
        huge_query = "What is " + ("AI " * 500)
        chunks = [
            {"content": "Some content", "filename": "doc1.pdf", "page": "1"}
        ]
        
        with self.assertRaises(PromptTooLargeError):
            self.builder_small.build(huge_query, chunks)


if __name__ == "__main__":
    unittest.main()
