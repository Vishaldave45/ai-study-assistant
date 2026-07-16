import logging
from typing import Generator
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.core.config import settings
from app.llm.provider import LLMProvider
from app.llm.schemas import LLMResponse
from app.llm.config import GEMINI_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS, TOP_P
from app.llm.exceptions import LLMError, LLMTimeout, LLMRateLimit, InvalidModelError

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise LLMError("GEMINI_API_KEY environment variable is not set.")
        try:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {e}")
            raise LLMError(f"Failed to initialize Gemini Client: {e}") from e

    def generate(self, prompt: str) -> LLMResponse:
        if not prompt:
            raise LLMError("Prompt cannot be empty.")

        try:
            config = types.GenerateContentConfig(
                temperature=TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                top_p=TOP_P,
            )
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )

            answer = response.text or ""
            usage = response.usage_metadata.model_dump() if response.usage_metadata else None
            finish_reason = None
            if response.candidates:
                fr = response.candidates[0].finish_reason
                finish_reason = str(fr) if fr else None

            return LLMResponse(
                answer=answer,
                usage=usage,
                finish_reason=finish_reason,
                model=response.model_version or GEMINI_MODEL,
            )
        except APIError as e:
            logger.error(f"Gemini APIError ({e.code}): {e.message}")
            if e.code == 429:
                raise LLMRateLimit(f"Gemini rate limit exceeded (429): {e.message}") from e
            elif e.code == 404:
                raise InvalidModelError(f"Model not found or invalid (404): {e.message}") from e
            elif e.code == 408 or e.code == 504:
                raise LLMTimeout(f"Gemini request timed out: {e.message}") from e
            else:
                raise LLMError(f"Gemini API error ({e.code}): {e.message}") from e
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            err_msg = str(e).lower()
            if "timeout" in err_msg:
                raise LLMTimeout(f"Gemini request timed out: {e}") from e
            elif "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
                raise LLMRateLimit(f"Gemini rate limit exceeded: {e}") from e
            elif "model" in err_msg or "not found" in err_msg:
                raise InvalidModelError(f"Invalid model name or model not found: {e}") from e
            else:
                raise LLMError(f"Gemini generation failed: {e}") from e

    def stream(self, prompt: str) -> Generator[str, None, None]:
        if not prompt:
            raise LLMError("Prompt cannot be empty.")

        try:
            config = types.GenerateContentConfig(
                temperature=TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                top_p=TOP_P,
            )
            response_stream = self.client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except APIError as e:
            logger.error(f"Gemini stream APIError ({e.code}): {e.message}")
            if e.code == 429:
                raise LLMRateLimit(f"Gemini stream rate limit exceeded (429): {e.message}") from e
            else:
                raise LLMError(f"Gemini stream API error ({e.code}): {e.message}") from e
        except Exception as e:
            logger.error(f"Gemini stream request failed: {e}")
            err_msg = str(e).lower()
            if "timeout" in err_msg:
                raise LLMTimeout(f"Gemini stream timed out: {e}") from e
            elif "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
                raise LLMRateLimit(f"Gemini stream rate limit exceeded: {e}") from e
            else:
                raise LLMError(f"Gemini stream failed: {e}") from e

    def model_name(self) -> str:
        return GEMINI_MODEL
