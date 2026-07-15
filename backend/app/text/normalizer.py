import unicodedata


class TextNormalizer:

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Unicode normalization (NFKC)
        text = unicodedata.normalize("NFKC", text)

        # Smart quotes map
        smart_quotes_map = {
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "„": '"',
            "‟": '"',
            "‚": "'",
            "‛": "'",
        }
        for q_from, q_to in smart_quotes_map.items():
            text = text.replace(q_from, q_to)

        # Em dash and en dash normalization
        text = text.replace("—", "-").replace("–", "-")

        # Zero-width space and other invisible spaces removal
        text = text.replace("\u200b", "").replace("\ufeff", "")

        # Normalize tabs to 4 spaces
        text = text.replace("\t", "    ")

        return text
