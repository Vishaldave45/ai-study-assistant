import time
import logging

logger = logging.getLogger(__name__)


class ExecutionTimer:
    """
    Simple context manager to measure and log execution duration of code blocks.
    """
    def __init__(self, operation_name: str = "Operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.duration_ms = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        self.duration_ms = int((end_time - self.start_time) * 1000)
        logger.info(f"{self.operation_name} completed in {self.duration_ms} ms.")


def sort_citations(citations: list[dict]) -> list[dict]:
    """
    Sort citations descending by relevance score.
    """
    return sorted(citations, key=lambda x: x.get("score", 0.0), reverse=True)


def remove_duplicate_citations(citations: list[dict]) -> list[dict]:
    """
    Remove duplicate citations that match same file/page, keeping the higher score.
    """
    seen = {}
    for citation in citations:
        key = (citation.get("document"), citation.get("page"))
        if key not in seen or citation.get("score", 0.0) > seen[key].get("score", 0.0):
            seen[key] = citation
    return list(seen.values())
