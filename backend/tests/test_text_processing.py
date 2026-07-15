import unittest
from app.text.normalizer import TextNormalizer
from app.text.cleaner import TextCleaner
from app.text.pipeline import TextProcessingPipeline


class TestTextProcessing(unittest.TestCase):

    def test_unicode_normalization_ligatures(self):
        # "ﬁ" and "ﬂ" should normalize to "fi" and "fl"
        raw_text = "ﬁrst ﬂight"
        normalized = TextNormalizer.normalize(raw_text)
        self.assertEqual(normalized, "first flight")

    def test_smart_quotes_and_dashes(self):
        # Smart quotes and em/en dashes
        raw_text = "“Hello”—he said, ‘World’."
        normalized = TextNormalizer.normalize(raw_text)
        self.assertEqual(normalized, '"Hello"-he said, \'World\'.')

    def test_zero_width_spaces_and_tabs(self):
        # Zero width spaces should be removed, tabs to 4 spaces
        raw_text = "A\u200bB\ufeffC\tD"
        normalized = TextNormalizer.normalize(raw_text)
        self.assertEqual(normalized, "ABC    D")

    def test_cleaner_whitespace_and_newlines(self):
        # Leading/trailing spaces per line, multiple spaces, multiple blank lines
        raw_text = "  Hello   World   \n\n\n\n  Next Line  \n"
        cleaned = TextCleaner.clean(raw_text)
        self.assertEqual(cleaned, "Hello World\n\nNext Line")

    def test_pipeline_statistics(self):
        # Full pipeline test with stats
        raw_text = "“ﬁrst”   ﬂight  \n\n\n  line  2  "
        processed = TextProcessingPipeline.process(raw_text)
        
        self.assertEqual(processed.text, '"first" flight\n\nline 2')
        self.assertEqual(processed.character_count, len('"first" flight\n\nline 2'))
        self.assertEqual(processed.line_count, 3)  # ["\"first\" flight", "", "line 2"]
        self.assertEqual(processed.word_count, 4)  # ["first", "flight", "line", "2"]

    def test_empty_input(self):
        processed = TextProcessingPipeline.process("")
        self.assertEqual(processed.text, "")
        self.assertEqual(processed.character_count, 0)
        self.assertEqual(processed.line_count, 0)
        self.assertEqual(processed.word_count, 0)


if __name__ == "__main__":
    unittest.main()
