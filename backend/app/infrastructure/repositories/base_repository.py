"""
Generic abstract repository.

Type parameters
---------------
T   - domain model type (e.g. User, Order)
ID  - primary key type (str or int)
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class BaseRepository(ABC, Generic[T, ID]):
    """
    Defines the minimum CRUD interface every repository must implement.
    """

    @abstractmethod
    def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Return a single domain object by its primary key, or None."""

    @abstractmethod
    def get_all(self) -> List[T]:
        """Return every record as a list of domain objects."""

    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Persist a new entity or update an existing one.
        Returns the saved entity (with any DB-generated fields populated).
        """

    @abstractmethod
    def delete(self, entity_id: ID) -> bool:
        """
        Remove the record with the given primary key.
        Returns True if a row was deleted, False if it did not exist.
        """
