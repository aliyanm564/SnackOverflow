from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")

class BaseRepository(ABC, Generic[T, ID]):

    @abstractmethod
    def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Return an entity by its ID, or None if not found."""

    @abstractmethod
    def get_all(self) -> List[T]:
        """Return all entities in the repository."""

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity to the repository. Returns the saved entity (with ID if new)."""

    @abstractmethod
    def delete(self, entity_id: ID) -> bool:
        """Delete an entity by its ID. Returns True if deleted, False if not found."""
