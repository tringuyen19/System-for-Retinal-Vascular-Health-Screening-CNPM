from marshmallow import Schema, fields

class PaymentCreateRequestSchema(Schema):
    """Schema for creating a Payment"""
    subscription_id = fields.Int(required=True, metadata={'description': "Subscription ID"})
    amount = fields.Decimal(required=True, as_string=True, metadata={'description': "Payment amount"})
    payment_method = fields.Str(required=True, metadata={'description': "Payment method (credit_card/bank_transfer/e-wallet)"})
    status = fields.Str(load_default="pending", metadata={'description': "Payment status (pending/completed/failed/refunded)"})

class PaymentUpdateRequestSchema(Schema):
    """Schema for updating a Payment"""
    status = fields.Str(metadata={'description': "Payment status"})

class PaymentResponseSchema(Schema):
    """Schema for Payment response"""
    payment_id = fields.Int(required=True, metadata={'description': "Unique payment identifier"})
    subscription_id = fields.Int(required=True, metadata={'description': "Subscription ID"})
    amount = fields.Decimal(required=True, as_string=True, metadata={'description': "Payment amount"})
    payment_method = fields.Str(required=True, metadata={'description': "Payment method"})
    payment_time = fields.DateTime(required=True, metadata={'description': "Payment timestamp"})
    status = fields.Str(required=True, metadata={'description': "Payment status"})

