from app.text.normalizer import TextNormalizer
from app.text.cleaner import TextCleaner
from app.text.schemas import ProcessedText


class TextProcessingPipeline:

    @classmethod
    def process(cls, text: str) -> ProcessedText:
        normalized = TextNormalizer.normalize(text)
        cleaned = TextCleaner.clean(normalized)

        # Calculate statistics on clean text
        char_count = len(cleaned)
        lines = cleaned.split("\n") if cleaned else []
        line_count = len(lines)
        word_count = len(cleaned.split()) if cleaned else 0

        return ProcessedText(
            text=cleaned,
            character_count=char_count,
            line_count=line_count,
            word_count=word_count,
        )