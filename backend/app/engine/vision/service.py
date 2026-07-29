import json
import logging
from typing import Any
from app.llm.service import LLMService
from app.engine.schemas import DiagramMetadata, TableMetadata, EquationMetadata

logger = logging.getLogger(__name__)

DIAGRAM_VISION_PROMPT = (
    "You are an expert AI Vision Analyst.\n"
    "Analyze the provided diagram image and return ONLY a valid JSON object matching this schema:\n"
    "{\n"
    '  "title": "Diagram Title",\n'
    '  "description": "Comprehensive description of what the diagram illustrates.",\n'
    '  "mermaid_code": "graph TD\\n...",\n'
    '  "concepts": ["Concept1", "Concept2"],\n'
    '  "relationships": [{"from": "Concept1", "to": "Concept2", "relation": "connects"}]\n'
    "}"
)

TABLE_VISION_PROMPT = (
    "You are an expert AI Data Analyst.\n"
    "Convert the provided table image into a clean, formatted Markdown table.\n"
    "Do NOT include any commentary—return ONLY the markdown table."
)

EQUATION_VISION_PROMPT = (
    "You are an expert Mathematical Vision Analyst.\n"
    "Extract the mathematical formula from the image and return ONLY a valid JSON object matching this schema:\n"
    "{\n"
    '  "latex": "\\\\frac{-b \\\\pm \\\\sqrt{b^2-4ac}}{2a}",\n'
    '  "explanation": "Natural language mathematical explanation of the equation."\n'
    "}"
)


class VisionAnalysisService:
    """
    Multimodal Vision AI Service powered by Gemini Vision for analyzing diagrams,
    tables, and mathematical equations from study documents.
    """

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService(provider_type="gemini")

    def parse_diagram(self, page_number: int, image_description: str = "") -> DiagramMetadata:
        """
        Analyze a diagram visual and produce a structured DiagramMetadata object.
        """
        prompt = f"{DIAGRAM_VISION_PROMPT}\n\nDiagram Context: {image_description}"
        try:
            response = self.llm_service.generate(prompt)
            # Clean possible markdown code block wrappers
            raw_text = response.answer.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            data = json.loads(raw_text.strip())
            return DiagramMetadata(
                page_number=page_number,
                title=data.get("title", "Untitled Diagram"),
                description=data.get("description", ""),
                mermaid_code=data.get("mermaid_code"),
                concepts=data.get("concepts", []),
                relationships=data.get("relationships", []),
            )
        except Exception as e:
            logger.warning(f"Failed parsing diagram on page {page_number}: {e}")
            return DiagramMetadata(
                page_number=page_number,
                title="Diagram Image",
                description=image_description or "Visual diagram figure",
            )

    def parse_table(self, page_number: int, table_context: str = "") -> TableMetadata:
        """
        Analyze a table visual and produce a formatted Markdown Table.
        """
        prompt = f"{TABLE_VISION_PROMPT}\n\nContext: {table_context}"
        try:
            response = self.llm_service.generate(prompt)
            return TableMetadata(
                page_number=page_number,
                content_markdown=response.answer.strip(),
            )
        except Exception as e:
            logger.warning(f"Failed parsing table on page {page_number}: {e}")
            return TableMetadata(
                page_number=page_number,
                content_markdown="| Table Data |\n| --- |\n| Data unavailable |",
            )

    def parse_equation(self, page_number: int, equation_context: str = "") -> EquationMetadata:
        """
        Analyze a mathematical formula and produce LaTeX + Explanation.
        """
        prompt = f"{EQUATION_VISION_PROMPT}\n\nContext: {equation_context}"
        try:
            response = self.llm_service.generate(prompt)
            raw_text = response.answer.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            data = json.loads(raw_text.strip())
            return EquationMetadata(
                page_number=page_number,
                latex=data.get("latex", "\\text{N/A}"),
                explanation=data.get("explanation"),
            )
        except Exception as e:
            logger.warning(f"Failed parsing equation on page {page_number}: {e}")
            return EquationMetadata(
                page_number=page_number,
                latex="\\text{Formula}",
                explanation="Mathematical equation",
            )
