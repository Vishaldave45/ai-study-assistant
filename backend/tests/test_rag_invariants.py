import unittest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from app.rag.pipeline import RAGPipeline
from app.rag.exceptions import GenerationFailed
from app.retrieval.models import RetrievalResult, RetrievedChunk
from app.llm.testing import FakeProvider
from app.llm.exceptions import LLMRateLimit, LLMError


class TestRAGInvariants(unittest.TestCase):

    def setUp(self):
        self.fake_llm_provider = FakeProvider(default_text="Mocked grounded answer.")
        self.mock_db = MagicMock()

        # Patch LLMFactory in llm service so it uses FakeProvider
        self.factory_patcher = patch(
            "app.llm.service.LLMFactory.create",
            return_value=self.fake_llm_provider
        )
        self.factory_patcher.start()

        # Patch RetrievalService in RAGPipeline
        self.retrieval_patcher = patch("app.rag.pipeline.RetrievalService")
        self.mock_retrieval_class = self.retrieval_patcher.start()
        self.mock_retrieval_service = self.mock_retrieval_class.return_value

    def tearDown(self):
        self.factory_patcher.stop()
        self.retrieval_patcher.stop()

    def test_multi_document_citation_ordering_and_metadata_fallback(self):
        """
        Verify citations preserve retrieval rank and handle missing filename metadata.
        """
        chunk1 = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(uuid4()),
            text="First chunk content.",
            score=0.95,
            page=1,
            chunk_index=0,
            metadata={"original_filename": "biology_notes.pdf"}
        )
        chunk2 = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(uuid4()),
            text="Second chunk content.",
            score=0.88,
            page=4,
            chunk_index=2,
            metadata={}  # Missing filename metadata
        )

        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="What is photosynthesis?",
            chunks=[chunk1, chunk2]
        )

        pipeline = RAGPipeline(self.mock_db)
        result = pipeline.answer_question(uuid4(), "What is photosynthesis?")

        # Assert citations order & scores match retrieval order
        self.assertEqual(len(result["citations"]), 2)
        self.assertEqual(result["citations"][0].document, "biology_notes.pdf")
        self.assertEqual(result["citations"][0].score, 0.95)
        self.assertEqual(result["citations"][1].document, "Unknown Document")
        self.assertEqual(result["citations"][1].score, 0.88)

    def test_prompt_inclusion_invariant(self):
        """
        Verify that all retrieved chunk text is physically included in the LLM prompt.
        """
        chunk1_text = "Photosynthesis converts light into chemical energy."
        chunk2_text = "Chlorophyll absorbs red and blue light wavelengths."

        chunk1 = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(uuid4()),
            text=chunk1_text,
            score=0.91,
            page=1,
            chunk_index=0,
            metadata={"original_filename": "botany.pdf"}
        )
        chunk2 = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(uuid4()),
            text=chunk2_text,
            score=0.85,
            page=2,
            chunk_index=1,
            metadata={"original_filename": "botany.pdf"}
        )

        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="How does chlorophyll work?",
            chunks=[chunk1, chunk2]
        )

        pipeline = RAGPipeline(self.mock_db)
        pipeline.answer_question(uuid4(), "How does chlorophyll work?")

        # Inspect prompt received by FakeProvider
        self.assertEqual(len(self.fake_llm_provider.calls), 1)
        received_prompt = self.fake_llm_provider.calls[0]["prompt"]

        self.assertIn(chunk1_text, received_prompt)
        self.assertIn(chunk2_text, received_prompt)
        self.assertIn("How does chlorophyll work?", received_prompt)

    def test_llm_failure_raises_generation_failed(self):
        """
        Verify that an unhandled LLM error raises GenerationFailed exception.
        """
        chunk = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(uuid4()),
            text="Some relevant text.",
            score=0.90,
            page=1,
            chunk_index=0,
            metadata={"original_filename": "doc.pdf"}
        )
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="Test query",
            chunks=[chunk]
        )

        # Queue an LLM error on FakeProvider
        self.fake_llm_provider.queue_response(LLMError("API Connection Refused"))

        pipeline = RAGPipeline(self.mock_db)
        pipeline.llm_service.max_retries = 1

        with self.assertRaises(GenerationFailed) as ctx:
            pipeline.answer_question(uuid4(), "Test query")

        self.assertIn("LLM service unavailable", str(ctx.exception))

    def test_llm_rate_limit_retry_backoff_success(self):
        """
        Verify LLMService retries on transient LLMRateLimit 429 errors and succeeds.
        """
        chunk = RetrievedChunk(
            chunk_id=str(uuid4()),
            document_id=str(uuid4()),
            text="Retry backoff chunk text.",
            score=0.90,
            page=1,
            chunk_index=0,
            metadata={"original_filename": "doc.pdf"}
        )
        self.mock_retrieval_service.retrieve.return_value = RetrievalResult(
            query="Test query",
            chunks=[chunk]
        )

        # Queue 429 RateLimit exception followed by valid LLM response
        self.fake_llm_provider.queue_response(LLMRateLimit("429 Too Many Requests"))
        self.fake_llm_provider.queue_response("Recovered answer after retry.")

        pipeline = RAGPipeline(self.mock_db)
        pipeline.llm_service.max_retries = 3
        pipeline.llm_service.retry_delay = 0.01

        result = pipeline.answer_question(uuid4(), "Test query")

        self.assertEqual(result["answer"], "Recovered answer after retry.")
        self.assertEqual(len(self.fake_llm_provider.calls), 2)


if __name__ == "__main__":
    unittest.main()
