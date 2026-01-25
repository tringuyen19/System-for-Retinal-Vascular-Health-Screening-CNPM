from marshmallow import Schema, fields

class SubscriptionCreateRequestSchema(Schema):
    """Schema for creating a Subscription"""
    account_id = fields.Int(required=True, metadata={'description': "Account ID"})
    package_id = fields.Int(required=True, metadata={'description': "Package ID"})
    start_date = fields.Date(allow_none=True, metadata={'description': "Subscription start date (optional, defaults to today)"})
    end_date = fields.Date(allow_none=True, metadata={'description': "Subscription end date (optional, auto-calculated from package duration)"})
    remaining_credits = fields.Int(required=True, metadata={'description': "Remaining image credits"})
    status = fields.Str(load_default="active", metadata={'description': "Subscription status (active/expired/cancelled)"})

class SubscriptionUpdateRequestSchema(Schema):
    """Schema for updating a Subscription"""
    end_date = fields.Date(metadata={'description': "Subscription end date"})
    remaining_credits = fields.Int(metadata={'description': "Remaining image credits"})
    status = fields.Str(metadata={'description': "Subscription status"})

class SubscriptionResponseSchema(Schema):
    """Schema for Subscription response"""
    subscription_id = fields.Int(required=True, metadata={'description': "Unique subscription identifier"})
    account_id = fields.Int(required=True, metadata={'description': "Account ID"})
    package_id = fields.Int(required=True, metadata={'description': "Package ID"})
    start_date = fields.Date(required=True, metadata={'description': "Subscription start date"})
    end_date = fields.Date(required=True, metadata={'description': "Subscription end date"})
    remaining_credits = fields.Int(required=True, metadata={'description': "Remaining image credits"})
    status = fields.Str(required=True, metadata={'description': "Subscription status"})

