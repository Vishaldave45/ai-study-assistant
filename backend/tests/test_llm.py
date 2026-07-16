import unittest
from unittest.mock import patch, MagicMock
from google.genai.errors import APIError

from app.llm.factory import LLMFactory
from app.llm.gemini import GeminiProvider
from app.llm.service import LLMService
from app.llm.exceptions import LLMError, LLMRateLimit, LLMTimeout, InvalidModelError


class TestLLM(unittest.TestCase):

    def test_factory_creation(self):
        provider = LLMFactory.create("gemini")
        self.assertIsInstance(provider, GeminiProvider)

        with self.assertRaises(ValueError):
            LLMFactory.create("unsupported_provider")

    @patch("app.llm.gemini.genai.Client")
    def test_generate_success(self, mock_client_class):
        # Setup mock client and mock response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = "Hello! I am an AI."
        mock_response.model_version = "gemini-2.5-flash-test"
        
        mock_usage = MagicMock()
        mock_usage.model_dump.return_value = {"prompt_tokens": 10, "output_tokens": 20}
        mock_response.usage_metadata = mock_usage

        mock_candidate = MagicMock()
        mock_candidate.finish_reason = "STOP"
        mock_response.candidates = [mock_candidate]

        mock_client.models.generate_content.return_value = mock_response

        # Execute generate
        provider = GeminiProvider()
        response = provider.generate("Hi")

        self.assertEqual(response.answer, "Hello! I am an AI.")
        self.assertEqual(response.model, "gemini-2.5-flash-test")
        self.assertEqual(response.usage["prompt_tokens"], 10)
        self.assertEqual(response.finish_reason, "STOP")

    @patch("app.llm.gemini.genai.Client")
    def test_stream_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Hello "
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "World"

        mock_client.models.generate_content_stream.return_value = [mock_chunk1, mock_chunk2]

        provider = GeminiProvider()
        chunks = list(provider.stream("Hi"))

        self.assertEqual(chunks, ["Hello ", "World"])

    @patch("app.llm.gemini.genai.Client")
    def test_generate_rate_limit_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock APIError with code 429
        mock_error = APIError(
            code=429,
            response_json={"error": {"message": "Resource has been exhausted"}},
        )
        mock_client.models.generate_content.side_effect = mock_error

        provider = GeminiProvider()
        with self.assertRaises(LLMRateLimit):
            provider.generate("Hi")

    @patch("app.llm.gemini.genai.Client")
    def test_generate_not_found_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock APIError with code 404
        mock_error = APIError(
            code=404,
            response_json={"error": {"message": "Model not found"}},
        )
        mock_client.models.generate_content.side_effect = mock_error

        provider = GeminiProvider()
        with self.assertRaises(InvalidModelError):
            provider.generate("Hi")

    @patch("app.llm.gemini.genai.Client")
    def test_service_validation(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        service = LLMService(provider_type="gemini")
        
        with self.assertRaises(LLMError):
            service.generate("")

        with self.assertRaises(LLMError):
            service.stream("  ")


if __name__ == "__main__":
    unittest.main()
