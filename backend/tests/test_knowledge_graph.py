import unittest
from unittest.mock import patch
from app.llm.testing import FakeProvider
from app.llm.service import LLMService
from app.engine.graph.service import KnowledgeGraphService, GraphTriplet


class TestKnowledgeGraph(unittest.TestCase):

    def setUp(self):
        self.fake_llm = FakeProvider()
        self.patcher = patch(
            "app.llm.service.LLMFactory.create",
            return_value=self.fake_llm,
        )
        self.patcher.start()
        self.llm_service = LLMService(provider_type="gemini")
        self.graph_service = KnowledgeGraphService(llm_service=self.llm_service)

    def tearDown(self):
        self.patcher.stop()

    def test_extract_triplets_and_query_neighbors(self):
        """Verify extracting triplets and querying entity graph neighbors."""
        mock_graph_json = """
        [
          {"source": "CPU", "relation": "uses", "target": "L1 Cache"},
          {"source": "L1 Cache", "relation": "stores", "target": "RAM"}
        ]
        """
        self.fake_llm.queue_response(mock_graph_json)

        triplets = self.graph_service.extract_triplets("CPU uses L1 Cache which stores RAM.")

        self.assertEqual(len(triplets), 2)
        self.assertEqual(triplets[0].source, "CPU")
        self.assertEqual(triplets[0].relation, "uses")
        self.assertEqual(triplets[0].target, "L1 Cache")

        # Query graph adjacency list
        neighbors = self.graph_service.get_entity_neighbors("CPU")
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]["target"], "L1 Cache")
        self.assertEqual(neighbors[0]["relation"], "uses")

    def test_extract_triplets_malformed_json_fallback(self):
        """Verify fallback behavior when LLM returns unparseable text."""
        self.fake_llm.queue_response("Invalid raw text")

        triplets = self.graph_service.extract_triplets("Some text")

        self.assertEqual(len(triplets), 0)


if __name__ == "__main__":
    unittest.main()
