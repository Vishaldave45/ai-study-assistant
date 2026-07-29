import json
import logging
from typing import List, Dict, Any
from pydantic import BaseModel
from app.llm.service import LLMService

logger = logging.getLogger(__name__)


class GraphTriplet(BaseModel):
    source: str
    relation: str
    target: str


GRAPH_EXTRACT_PROMPT = (
    "You are an expert Knowledge Graph Triplet Extractor.\n"
    "Extract all key concept entities and their relationships from the text.\n"
    "Return ONLY a valid JSON array matching this schema:\n"
    "[\n"
    '  {"source": "CPU", "relation": "uses", "target": "L1 Cache"},\n'
    '  {"source": "L1 Cache", "relation": "stores", "target": "RAM"}\n'
    "]"
)


class KnowledgeGraphService:
    """
    Structured Knowledge Graph Engine extracting entity-relationship triplets
    from study materials and providing multi-hop relationship traversal.
    """

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService(provider_type="gemini")
        self.graph_adjacency: Dict[str, List[Dict[str, str]]] = {}

    def extract_triplets(self, text_content: str) -> List[GraphTriplet]:
        """
        Extracts GraphTriplet entities and relationships from raw study text.
        """
        prompt = f"{GRAPH_EXTRACT_PROMPT}\n\nStudy Text:\n{text_content}"
        try:
            response = self.llm_service.generate(prompt)
            raw = self._clean_json(response.answer)
            data = json.loads(raw)

            triplets = [
                GraphTriplet(
                    source=item.get("source", "Unknown"),
                    relation=item.get("relation", "relates_to"),
                    target=item.get("target", "Unknown"),
                )
                for item in data
                if "source" in item and "target" in item
            ]
            self.add_triplets_to_graph(triplets)
            return triplets
        except Exception as e:
            logger.warning(f"Failed extracting graph triplets: {e}")
            return []

    def add_triplets_to_graph(self, triplets: List[GraphTriplet]) -> None:
        """
        Populates in-memory adjacency list graph representation.
        """
        for t in triplets:
            src = t.source.strip().title()
            tgt = t.target.strip().title()
            rel = t.relation.strip().lower()

            if src not in self.graph_adjacency:
                self.graph_adjacency[src] = []
            self.graph_adjacency[src].append({"relation": rel, "target": tgt})

    def get_entity_neighbors(self, entity: str) -> List[Dict[str, str]]:
        """
        Returns all outgoing concept relationships from a target entity node.
        """
        key = entity.strip().title()
        return self.graph_adjacency.get(key, [])

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
