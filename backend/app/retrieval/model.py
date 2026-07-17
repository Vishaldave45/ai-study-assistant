from dataclasses import dataclass
from uuid import UUID
from typing import Dict,Any


@dataclass
class RetrievedChunks:
    text:str
    score:float
    page:int
    chunk_index:int
    document_id:UUID
    metadata:Dict[str,Any]
    
@dataclass
class RetivalResult:
    query:str
    chunks:list[RetrievedChunks]