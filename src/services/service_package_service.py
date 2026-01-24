"""
Service Package Service - Business Logic Layer
Handles service package management
"""

from typing import List, Optional
from decimal import Decimal
from domain.models.service_package import ServicePackage
from domain.models.iservice_package_repository import IServicePackageRepository


class ServicePackageService:
    def __init__(self, repository: IServicePackageRepository):
        self.repository = repository
    
    def create_package(self, name: str, price: Decimal, 
                      image_limit: int, duration_days: int) -> Optional[ServicePackage]:
        """Create service package"""
        # Validate price
        if price < 0:
            raise ValueError("Price must be positive")
        
        # Validate image limit
        if image_limit < 0:
            raise ValueError("Image limit must be positive")
        
        # Validate duration
        if duration_days < 1:
            raise ValueError("Duration must be at least 1 day")
        
        return self.repository.add(
            name=name,
            price=price,
            image_limit=image_limit,
            duration_days=duration_days
        )
    
    def get_package_by_id(self, package_id: int) -> Optional[ServicePackage]:
        """Get package by ID"""
        return self.repository.get_by_id(package_id)
    
    def get_package_by_name(self, name: str) -> Optional[ServicePackage]:
        """Get package by name"""
        return self.repository.get_by_name(name)
    
    def list_all_packages(self) -> List[ServicePackage]:
        """Get all packages"""
        return self.repository.get_all()
    
    def get_active_packages(self) -> List[ServicePackage]:
        """Get active packages (for display to users)"""
        return self.repository.get_active_packages()
    
    def update_package(self, package_id: int, **kwargs) -> Optional[ServicePackage]:
        """Update package"""
        return self.repository.update(package_id, **kwargs)
    
    def update_price(self, package_id: int, new_price: Decimal) -> Optional[ServicePackage]:
        """Update package price"""
        if new_price < 0:
            raise ValueError("Price must be positive")
        return self.repository.update_price(package_id, new_price)
    
    def delete_package(self, package_id: int) -> bool:
        """Delete package"""
        return self.repository.delete(package_id)
    
    def count_packages(self) -> int:
        """Count total packages"""
        return self.repository.count()
    
    def get_most_popular_package(self) -> Optional[ServicePackage]:
        """Get most popular package"""
        return self.repository.get_most_popular()
    
    def get_cheapest_package(self) -> Optional[ServicePackage]:
        """Get cheapest package"""
        return self.repository.get_cheapest()
    
    def get_most_expensive_package(self) -> Optional[ServicePackage]:
        """Get most expensive package"""
        return self.repository.get_most_expensive()
    
    def get_package_statistics(self) -> dict:
        """Get package statistics"""
        packages = self.repository.get_all()
        avg_price = sum([float(p.price) for p in packages]) / len(packages) if packages else 0
        return {
            'total': len(packages),
            'total_packages': len(packages),
            'active_packages': len(self.repository.get_active_packages()),
            'average_price': avg_price,
            'avg_price': avg_price
        }
