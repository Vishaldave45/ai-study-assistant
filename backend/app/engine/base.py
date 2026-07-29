from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from app.engine.schemas import PageObject


class BaseDocumentProcessor(ABC):
    """
    Abstract Strategy Interface for Document Ingestion & Page Object Extraction.
    """

    @abstractmethod
    def process(self, file_source: Union[Path, bytes]) -> list[PageObject]:
        """
        Extract document pages into PageObject instances containing text and visual metadata.
        """
        pass
