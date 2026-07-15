from abc import ABC, abstractmethod
from io import BytesIO


class StorageProvider(ABC):
    """ save()

    delete()

    exists()

    open()

    url()"""
    
    @abstractmethod
    def save(self, path:str, data:BytesIO) -> bool:
        pass

    @abstractmethod
    def delete(self, path:str) -> bool:
        pass

    @abstractmethod
    def exists(self, path:str) -> bool:
        pass

    @abstractmethod
    def open(self, path:str) -> BytesIO:
        pass

    @abstractmethod
    def url(self, path:str) -> str:
        pass
                