from decimal import Decimal


class ServicePackage:
    def __init__(
        self,
        package_id: int,
        name: str,
        price: Decimal,
        image_limit: int,
        duration_days: int,
        package_type: str = "patient",
        is_active: bool = True,
    ):
        self.package_id = package_id
        self.name = name
        self.price = price
        self.image_limit = image_limit
        self.duration_days = duration_days
        self.package_type = package_type
        self.is_active = is_active

