from datetime import datetime
from decimal import Decimal

class Payment:
    def __init__(self, payment_id: int, subscription_id: int, amount: Decimal, 
                 payment_method: str, payment_time: datetime, status: str):
        self.payment_id = payment_id
        self.subscription_id = subscription_id
        self.amount = amount
        self.payment_method = payment_method
        self.payment_time = payment_time
        self.status = status

