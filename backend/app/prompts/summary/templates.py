from enum import Enum

class SummaryTemplateType(str, Enum):
    SHORT = "short"
    DETAILED = "detailed"
    BULLET = "bullet"
    REVISION_NOTES = "revision_notes"
    KEY_TAKEAWAYS = "key_takeaways"


SUMMARY_SYSTEM_PROMPT = (
    "You are an AI Study Assistant designed to help students learn efficiently.\n"
    "Your task is to generate high-quality summaries from the provided document chunks.\n"
    "Ensure you only use the provided document context to compile your summary. Do not introduce outside information or make assumptions."
)

SHORT_SUMMARY_TEMPLATE = (
    "Generate a concise, 1-2 paragraph summary capturing the core argument, main theme, and essential concepts in the text.\n"
    "Ensure the language is clear and readable."
)

DETAILED_SUMMARY_TEMPLATE = (
    "Generate a comprehensive, detailed summary of the provided text.\n"
    "Structure it with logical headings, sub-headings, and clear paragraphs.\n"
    "Elaborate on all key concepts, methods, and arguments presented in the text."
)

BULLET_SUMMARY_TEMPLATE = (
    "Extract the main points of the text and list them as clear, structured bullet points.\n"
    "Use nesting if necessary to show hierarchy, and keep each bullet point concise but informative."
)

REVISION_NOTES_TEMPLATE = (
    "Generate structured revision notes for studying this material.\n"
    "Include:\n"
    "1. **Core Terminology**: Key terms and their exact definitions.\n"
    "2. **Concept Breakdown**: Structured analysis of the primary themes/theories.\n"
    "3. **Study Tips**: Recommended quick memory aids or focus areas based on this text."
)

KEY_TAKEAWAYS_TEMPLATE = (
    "Provide the primary key takeaways from the text.\n"
    "List the most critical lessons, actions, conclusions, or takeaways a reader should remember."
)

TEMPLATES = {
    SummaryTemplateType.SHORT: SHORT_SUMMARY_TEMPLATE,
    SummaryTemplateType.DETAILED: DETAILED_SUMMARY_TEMPLATE,
    SummaryTemplateType.BULLET: BULLET_SUMMARY_TEMPLATE,
    SummaryTemplateType.REVISION_NOTES: REVISION_NOTES_TEMPLATE,
    SummaryTemplateType.KEY_TAKEAWAYS: KEY_TAKEAWAYS_TEMPLATE,
}
