from enum import Enum

class ExplainLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    INTERVIEW = "interview"
    ANALOGY = "analogy"


EXPLAIN_SYSTEM_PROMPT = (
    "You are an AI Study Assistant designed to explain academic and technical concepts clearly.\n"
    "Your response MUST be a valid JSON object matching the JSON schema below.\n"
    "Do not include any text outside of the JSON object.\n"
    "Ensure you only use the provided context to compile your explanations. "
    "If the context does not contain enough information to explain the concept, use the context as much as possible and clearly specify the limitations in the response.\n\n"
    "JSON RESPONSE SCHEMA:\n"
    "{\n"
    "  \"explanation\": \"A clear explanation of the concept aligned with the requested target depth/mode.\",\n"
    "  \"examples\": [\"List of illustrative examples or code snippets demonstrating the concept\"],\n"
    "  \"important_points\": [\"Key bullets or rules to remember about this concept\"],\n"
    "  \"references\": [\"Document names and page details used for this explanation (e.g., 'notes.pdf (Page 2)')\"],\n"
    "  \"follow_up_questions\": [\"List of 2-3 logical follow-up questions for the student to test their understanding\"]\n"
    "}"
)

BEGINNER_TEMPLATE = (
    "Explain the concept '{concept}' for a BEGINNER level.\n"
    "Use simple, conversational language, avoid complex jargon, and explain the core mechanics as if explaining to someone with no prior background."
)

INTERMEDIATE_TEMPLATE = (
    "Explain the concept '{concept}' for an INTERMEDIATE level.\n"
    "Use standard technical terms, explain how it works under the hood, and illustrate how it is commonly used in practice."
)

ADVANCED_TEMPLATE = (
    "Provide an ADVANCED explanation of '{concept}'.\n"
    "Deep dive into technical details, architecture, trade-offs, constraints, and optimization strategies. "
    "Include high-fidelity technical examples or pseudocode if relevant."
)

INTERVIEW_TEMPLATE = (
    "Explain '{concept}' from an INTERVIEW preparation perspective.\n"
    "Provide a concise, high-impact definition first, followed by typical interview questions/answers regarding the concept, "
    "common pitfalls, and key technical phrases interviewers look for."
)

ANALOGY_TEMPLATE = (
    "Explain the concept '{concept}' using a strong, relatable everyday ANALOGY.\n"
    "Compare the abstract technical concept to a familiar real-world scenario (e.g., comparing database indexes to a book's index), "
    "and map the parts of the analogy to the components of the concept."
)

TEMPLATES = {
    ExplainLevel.BEGINNER: BEGINNER_TEMPLATE,
    ExplainLevel.INTERMEDIATE: INTERMEDIATE_TEMPLATE,
    ExplainLevel.ADVANCED: ADVANCED_TEMPLATE,
    ExplainLevel.INTERVIEW: INTERVIEW_TEMPLATE,
    ExplainLevel.ANALOGY: ANALOGY_TEMPLATE,
}
