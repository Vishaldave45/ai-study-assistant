import re


class TextCleaner:

    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return ""

        
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

       
        text = re.sub(r"[ \t]+", " ", text)

        
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
