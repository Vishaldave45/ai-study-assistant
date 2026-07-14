from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(ABC, Generic[ModelType]):
   
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self,model: type[ModelType],entity_id: UUID,) -> ModelType | None:
       return self.db.get(model, entity_id)

    def add(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.db.delete(entity)

    def flush(self) -> None:
        self.db.flush()

    def refresh(self, entity: ModelType) -> None:
        self.db.refresh(entity)