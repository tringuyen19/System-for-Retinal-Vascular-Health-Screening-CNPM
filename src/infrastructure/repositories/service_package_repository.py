from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.billing.service_package_model import ServicePackageModel
from domain.models.service_package import ServicePackage
from domain.models.iservice_package_repository import IServicePackageRepository


class ServicePackageRepository(IServicePackageRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: ServicePackageModel) -> ServicePackage:
        return ServicePackage(
            package_id=model.package_id, name=model.name, price=model.price,
            image_limit=model.image_limit, duration_days=model.duration_days
        )
    
    def add(self, name: str, price: Decimal, image_limit: int, duration_days: int) -> ServicePackage:
        try:
            pkg_model = ServicePackageModel(
                name=name, price=price, image_limit=image_limit, duration_days=duration_days
            )
            self.session.add(pkg_model)
            self.session.commit()
            self.session.refresh(pkg_model)
            return self._to_domain(pkg_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating service package: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, package_id: int) -> Optional[ServicePackage]:
        try:
            pkg_model = self.session.query(ServicePackageModel).filter_by(package_id=package_id).first()
            return self._to_domain(pkg_model) if pkg_model else None
        except Exception as e:
            raise ValueError(f'Error getting service package: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_name(self, name: str) -> Optional[ServicePackage]:
        try:
            pkg_model = self.session.query(ServicePackageModel).filter_by(name=name).first()
            return self._to_domain(pkg_model) if pkg_model else None
        except Exception as e:
            raise ValueError(f'Error getting package by name: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[ServicePackage]:
        try:
            pkg_models = self.session.query(ServicePackageModel).all()
            return [self._to_domain(model) for model in pkg_models]
        except Exception as e:
            raise ValueError(f'Error getting all packages: {str(e)}')
        finally:
            self.session.close()
    
    def get_active_packages(self) -> List[ServicePackage]:
        try:
            pkg_models = self.session.query(ServicePackageModel).all()
            return [self._to_domain(model) for model in pkg_models]
        except Exception as e:
            raise ValueError(f'Error getting active packages: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, package_id: int, **kwargs) -> Optional[ServicePackage]:
        try:
            pkg_model = self.session.query(ServicePackageModel).filter_by(package_id=package_id).first()
            if not pkg_model:
                return None
            for key, value in kwargs.items():
                if hasattr(pkg_model, key) and key != 'package_id':
                    setattr(pkg_model, key, value)
            self.session.commit()
            self.session.refresh(pkg_model)
            return self._to_domain(pkg_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating package: {str(e)}')
        finally:
            self.session.close()
    
    def update_price(self, package_id: int, new_price: Decimal) -> Optional[ServicePackage]:
        try:
            pkg_model = self.session.query(ServicePackageModel).filter_by(package_id=package_id).first()
            if not pkg_model:
                return None
            pkg_model.price = new_price
            self.session.commit()
            self.session.refresh(pkg_model)
            return self._to_domain(pkg_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating price: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, package_id: int) -> bool:
        try:
            pkg_model = self.session.query(ServicePackageModel).filter_by(package_id=package_id).first()
            if not pkg_model:
                return False
            self.session.delete(pkg_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting package: {str(e)}')
        finally:
            self.session.close()
    
    def count(self) -> int:
        try:
            return self.session.query(ServicePackageModel).count()
        except Exception as e:
            raise ValueError(f'Error counting packages: {str(e)}')
        finally:
            self.session.close()
    
    def get_most_popular(self) -> Optional[ServicePackage]:
        try:
            pkg_model = self.session.query(ServicePackageModel).order_by(
                ServicePackageModel.price.asc()
            ).first()
            return self._to_domain(pkg_model) if pkg_model else None
        except Exception as e:
            raise ValueError(f'Error getting most popular package: {str(e)}')
        finally:
            self.session.close()
    
    def get_cheapest(self) -> Optional[ServicePackage]:
        """Get cheapest package (lowest price)"""
        try:
            pkg_model = self.session.query(ServicePackageModel).order_by(
                ServicePackageModel.price.asc()
            ).first()
            return self._to_domain(pkg_model) if pkg_model else None
        except Exception as e:
            raise ValueError(f'Error getting cheapest package: {str(e)}')
        finally:
            self.session.close()
    
    def get_most_expensive(self) -> Optional[ServicePackage]:
        """Get most expensive package (highest price)"""
        try:
            pkg_model = self.session.query(ServicePackageModel).order_by(
                ServicePackageModel.price.desc()
            ).first()
            return self._to_domain(pkg_model) if pkg_model else None
        except Exception as e:
            raise ValueError(f'Error getting most expensive package: {str(e)}')
        finally:
            self.session.close()