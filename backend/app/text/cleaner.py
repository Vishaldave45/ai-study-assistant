import re


class TextCleaner:

    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return ""

        # Strip leading and trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        # Collapse multiple spaces and tabs (non-newline spaces) into a single space
        text = re.sub(r"[ \t]+", " ", text)

        # Collapse multiple blank lines (3 or more newlines) to exactly 2 newlines
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        text = re.sub(r"[ \t]+", " ", text)

        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
