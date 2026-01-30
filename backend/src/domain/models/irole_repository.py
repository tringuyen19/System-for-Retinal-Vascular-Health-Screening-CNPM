from abc import ABC, abstractmethod
from .role import Role
from typing import List, Optional

class IRoleRepository(ABC):
    @abstractmethod
    def add(self, role_name: str) -> Role:
        pass

    @abstractmethod
    def get_by_id(self, role_id: int) -> Optional[Role]:
        pass

    @abstractmethod
    def get_by_name(self, role_name: str) -> Optional[Role]:
        pass

    @abstractmethod
    def get_all(self) -> List[Role]:
        pass

    @abstractmethod
    def update(self, role_id: int, role_name: str) -> Optional[Role]:
        pass

    @abstractmethod
    def delete(self, role_id: int) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def check_exists(self, role_name: str) -> bool:
        pass

