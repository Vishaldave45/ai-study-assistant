import unittest
from unittest.mock import patch
from app.llm.testing import FakeProvider
from app.llm.service import LLMService
from app.engine.vision.service import VisionAnalysisService


class TestVisionAnalysis(unittest.TestCase):

    def setUp(self):
        self.fake_llm = FakeProvider()
        self.patcher = patch(
            "app.llm.service.LLMFactory.create",
            return_value=self.fake_llm,
        )
        self.patcher.start()
        self.llm_service = LLMService(provider_type="gemini")
        self.vision_service = VisionAnalysisService(llm_service=self.llm_service)

    def tearDown(self):
        self.patcher.stop()

    def test_parse_diagram_success(self):
        """Verify diagram visual parsing into structured DiagramMetadata."""
        mock_json_response = """
        ```json
        {
          "title": "OSI Model Architecture",
          "description": "7-layer network protocol architecture diagram.",
          "mermaid_code": "graph TD\\n  App --> Pres",
          "concepts": ["Application", "Presentation"],
          "relationships": [{"from": "Application", "to": "Presentation", "relation": "encapsulates"}]
        }
        ```
        """
        self.fake_llm.queue_response(mock_json_response)

        diagram = self.vision_service.parse_diagram(page_number=5, image_description="OSI Diagram")

        self.assertEqual(diagram.page_number, 5)
        self.assertEqual(diagram.title, "OSI Model Architecture")
        self.assertIn("Presentation", diagram.concepts)
        self.assertEqual(len(diagram.relationships), 1)

    def test_parse_table_success(self):
        """Verify table visual parsing into formatted Markdown table."""
        mock_table_markdown = "| Layer | Protocol |\n| --- | --- |\n| TCP | Transport |"
        self.fake_llm.queue_response(mock_table_markdown)

        table = self.vision_service.parse_table(page_number=2, table_context="Protocols")

        self.assertEqual(table.page_number, 2)
        self.assertIn("| TCP | Transport |", table.content_markdown)

    def test_parse_equation_success(self):
        """Verify equation visual parsing into LaTeX + explanation."""
        mock_eq_json = """
        {
          "latex": "\\\\frac{-b \\\\pm \\\\sqrt{b^2-4ac}}{2a}",
          "explanation": "Quadratic formula for finding polynomial roots."
        }
        """
        self.fake_llm.queue_response(mock_eq_json)

        eq = self.vision_service.parse_equation(page_number=3, equation_context="Quadratic")

        self.assertEqual(eq.page_number, 3)
        self.assertIn("sqrt{b^2-4ac}", eq.latex)
        self.assertIn("Quadratic formula", eq.explanation)

    def test_parse_diagram_malformed_json_fallback(self):
        """Verify fallback behavior when LLM returns unparseable text."""
        self.fake_llm.queue_response("Invalid raw non-json text response.")

        diagram = self.vision_service.parse_diagram(page_number=1, image_description="System Chart")

        self.assertEqual(diagram.page_number, 1)
        self.assertEqual(diagram.title, "Diagram Image")
        self.assertIn("System Chart", diagram.description)


if __name__ == "__main__":
    unittest.main()
