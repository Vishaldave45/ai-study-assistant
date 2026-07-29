import unittest
from unittest.mock import patch
from app.llm.testing import FakeProvider
from app.llm.service import LLMService
from app.engine.schemas import DiagramMetadata
from app.engine.features.service import DiagramFeatureService


class TestDiagramFeatures(unittest.TestCase):

    def setUp(self):
        self.fake_llm = FakeProvider()
        self.patcher = patch(
            "app.llm.service.LLMFactory.create",
            return_value=self.fake_llm,
        )
        self.patcher.start()
        self.llm_service = LLMService(provider_type="gemini")
        self.feature_service = DiagramFeatureService(llm_service=self.llm_service)
        self.sample_diagram = DiagramMetadata(
            page_number=1,
            title="OSI Model Architecture",
            description="7-layer protocol stack diagram.",
            concepts=["Application", "Presentation", "Transport"],
            relationships=[{"from": "Application", "to": "Presentation", "relation": "encapsulates"}],
        )

    def tearDown(self):
        self.patcher.stop()

    def test_generate_diagram_quiz_success(self):
        """Verify quiz generation from a DiagramMetadata object."""
        mock_quiz_json = """
        [
          {
            "question": "What is the primary role of Transport layer?",
            "options": ["Routing", "Encapsulation", "End-to-end delivery", "Physical link"],
            "correct_index": 2,
            "explanation": "Transport layer provides host-to-host delivery."
          }
        ]
        """
        self.fake_llm.queue_response(mock_quiz_json)

        quiz = self.feature_service.generate_diagram_quiz(self.sample_diagram)

        self.assertEqual(len(quiz), 1)
        self.assertEqual(quiz[0]["correct_index"], 2)
        self.assertIn("Transport layer", quiz[0]["question"])

    def test_generate_diagram_flashcards_success(self):
        """Verify flashcard generation from a DiagramMetadata object."""
        mock_cards_json = """
        [
          {
            "front": "What concept connects Application to Presentation?",
            "back": "Session encapsulation and formatting."
          }
        ]
        """
        self.fake_llm.queue_response(mock_cards_json)

        cards = self.feature_service.generate_diagram_flashcards(self.sample_diagram)

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["front"], "What concept connects Application to Presentation?")

    def test_generate_diagram_explanation_success(self):
        """Verify step-by-step conceptual explanation generation."""
        mock_exp = "Step 1: Application layer passes data to Presentation layer..."
        self.fake_llm.queue_response(mock_exp)

        exp = self.feature_service.generate_diagram_explanation(self.sample_diagram)

        self.assertIn("Step 1: Application layer", exp)


if __name__ == "__main__":
    unittest.main()
