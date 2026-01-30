from abc import ABC, abstractmethod
from .service_package import ServicePackage
from typing import List, Optional
from decimal import Decimal

class IServicePackageRepository(ABC):
    @abstractmethod
    def add(self, name: str, price: Decimal, image_limit: int, 
            duration_days: int) -> ServicePackage:
        pass

    @abstractmethod
    def get_by_id(self, package_id: int) -> Optional[ServicePackage]:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[ServicePackage]:
        pass

    @abstractmethod
    def get_all(self) -> List[ServicePackage]:
        pass

    @abstractmethod
    def get_active_packages(self) -> List[ServicePackage]:
        pass

    @abstractmethod
    def update(self, package_id: int, **kwargs) -> Optional[ServicePackage]:
        pass

    @abstractmethod
    def update_price(self, package_id: int, new_price: Decimal) -> Optional[ServicePackage]:
        pass

    @abstractmethod
    def delete(self, package_id: int) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def get_most_popular(self) -> Optional[ServicePackage]:
        pass
    
    @abstractmethod
    def get_cheapest(self) -> Optional[ServicePackage]:
        """Get cheapest package (lowest price)"""
        pass
    
    @abstractmethod
    def get_most_expensive(self) -> Optional[ServicePackage]:
        """Get most expensive package (highest price)"""
        pass

