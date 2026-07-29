import json
import logging
from typing import List, Dict, Any
from app.llm.service import LLMService
from app.engine.schemas import DiagramMetadata

logger = logging.getLogger(__name__)

QUIZ_GEN_PROMPT = (
    "You are an expert Educational Quiz Generator.\n"
    "Based on the provided diagram visual information, generate 3 multiple-choice questions.\n"
    "Return ONLY a valid JSON array matching this schema:\n"
    "[\n"
    "  {\n"
    '    "question": "What is the primary role of the Transport layer?",\n'
    '    "options": ["Encapsulation", "Routing", "End-to-end delivery", "Physical signals"],\n'
    '    "correct_index": 2,\n'
    '    "explanation": "Transport layer provides host-to-host communication."\n'
    "  }\n"
    "]"
)

FLASHCARD_GEN_PROMPT = (
    "You are an expert Spaced Repetition Flashcard Creator.\n"
    "Based on the provided diagram visual concepts and relationships, generate 3 study flashcards.\n"
    "Return ONLY a valid JSON array matching this schema:\n"
    "[\n"
    "  {\n"
    '    "front": "What concept connects Application to Presentation layer?",\n'
    '    "back": "Session encapsulation and data formatting."\n'
    "  }\n"
    "]"
)


class DiagramFeatureService:
    """
    Multimodal AI Study Feature Service transforming visual diagrams into
    interactive quizzes, flashcards, mind maps, and explanations.
    """

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService(provider_type="gemini")

    def generate_diagram_quiz(self, diagram: DiagramMetadata) -> List[Dict[str, Any]]:
        """
        Generates interactive quiz questions from a DiagramMetadata visual.
        """
        prompt = (
            f"{QUIZ_GEN_PROMPT}\n\n"
            f"Diagram Title: {diagram.title}\n"
            f"Description: {diagram.description}\n"
            f"Concepts: {', '.join(diagram.concepts)}\n"
            f"Relationships: {json.dumps(diagram.relationships)}"
        )
        try:
            response = self.llm_service.generate(prompt)
            raw = self._clean_json(response.answer)
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Failed generating quiz from diagram {diagram.title}: {e}")
            return [
                {
                    "question": f"What is the main topic of '{diagram.title}'?",
                    "options": [diagram.title or "Diagram", "Unrelated Topic", "N/A", "None"],
                    "correct_index": 0,
                    "explanation": diagram.description or "Visual diagram question.",
                }
            ]

    def generate_diagram_flashcards(self, diagram: DiagramMetadata) -> List[Dict[str, str]]:
        """
        Generates active-recall study flashcards from a DiagramMetadata visual.
        """
        prompt = (
            f"{FLASHCARD_GEN_PROMPT}\n\n"
            f"Diagram Title: {diagram.title}\n"
            f"Description: {diagram.description}\n"
            f"Concepts: {', '.join(diagram.concepts)}"
        )
        try:
            response = self.llm_service.generate(prompt)
            raw = self._clean_json(response.answer)
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Failed generating flashcards from diagram {diagram.title}: {e}")
            return [
                {
                    "front": f"Explain the concept of {diagram.title}",
                    "back": diagram.description or "Diagram visual overview.",
                }
            ]

    def generate_diagram_explanation(self, diagram: DiagramMetadata) -> str:
        """
        Generates a step-by-step conceptual walkthrough of a diagram visual.
        """
        prompt = (
            f"Provide a clear, step-by-step educational breakdown of the following diagram:\n"
            f"Title: {diagram.title}\n"
            f"Description: {diagram.description}\n"
            f"Concepts: {', '.join(diagram.concepts)}"
        )
        response = self.llm_service.generate(prompt)
        return response.answer.strip()

    @staticmethod
    def _clean_json(raw_text: str) -> str:
        text = raw_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
