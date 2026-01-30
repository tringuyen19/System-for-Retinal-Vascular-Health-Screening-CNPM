"""
Domain Validators - Business Rule Validation
Pure domain logic for validating business rules
"""

from datetime import datetime, date
from typing import Optional
from domain.exceptions import ValidationException, BusinessRuleException


class AccountValidator:
    """Validator for Account domain entity"""
    
    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format"""
        if not email:
            raise ValidationException("Email is required")
        
        if '@' not in email or '.' not in email.split('@')[1]:
            raise ValidationException("Invalid email format")
        
        if len(email) > 255:
            raise ValidationException("Email must be less than 255 characters")
    
    @staticmethod
    def validate_password(password: str) -> None:
        """Validate password strength"""
        if not password:
            raise ValidationException("Password is required")
        
        if len(password) < 6:
            raise ValidationException("Password must be at least 6 characters")
        
        if len(password) > 128:
            raise ValidationException("Password must be less than 128 characters")


class PatientValidator:
    """Validator for PatientProfile domain entity"""
    
    @staticmethod
    def validate_date_of_birth(dob: Optional[date]) -> None:
        """Validate date of birth"""
        if dob is None:
            return  # Optional field
        
        if dob > datetime.now().date():
            raise ValidationException("Date of birth cannot be in the future")
        
        # Check if age is reasonable (not more than 150 years)
        age = (datetime.now().date() - dob).days // 365
        if age > 150:
            raise ValidationException("Invalid date of birth (age exceeds 150 years)")
    
    @staticmethod
    def validate_gender(gender: Optional[str]) -> None:
        """Validate gender value"""
        if gender is None:
            return  # Optional field
        
        valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']
        if gender.lower() not in valid_genders:
            raise ValidationException(f"Gender must be one of: {', '.join(valid_genders)}")
    
    @staticmethod
    def validate_patient_name(name: str) -> None:
        """Validate patient name"""
        if not name:
            raise ValidationException("Patient name is required")
        
        if len(name) > 255:
            raise ValidationException("Patient name must be less than 255 characters")
        
        if len(name.strip()) < 2:
            raise ValidationException("Patient name must be at least 2 characters")


class RetinalImageValidator:
    """Validator for RetinalImage domain entity"""
    
    @staticmethod
    def validate_image_type(image_type: str) -> None:
        """Validate image type"""
        valid_types = ['fundus', 'oct', 'fluorescein', 'angiography']
        if image_type.lower() not in valid_types:
            raise ValidationException(f"Image type must be one of: {', '.join(valid_types)}")
    
    @staticmethod
    def validate_eye_side(eye_side: str) -> None:
        """Validate eye side"""
        valid_sides = ['left', 'right', 'both']
        if eye_side.lower() not in valid_sides:
            raise ValidationException(f"Eye side must be one of: {', '.join(valid_sides)}")
    
    @staticmethod
    def validate_image_url(image_url: str) -> None:
        """Validate image URL"""
        if not image_url:
            raise ValidationException("Image URL is required")
        
        if len(image_url) > 500:
            raise ValidationException("Image URL must be less than 500 characters")
        
        # Basic URL format check
        if not (image_url.startswith('http://') or image_url.startswith('https://')):
            raise ValidationException("Image URL must start with http:// or https://")


class SubscriptionValidator:
    """Validator for Subscription domain entity"""
    
    @staticmethod
    def validate_credits(credits: int) -> None:
        """Validate credit amount"""
        if credits < 0:
            raise BusinessRuleException("Credits cannot be negative")
        
        if credits > 1000000:  # Reasonable upper limit
            raise BusinessRuleException("Credits exceed maximum allowed")
    
    @staticmethod
    def validate_dates(start_date: date, end_date: date) -> None:
        """Validate subscription dates"""
        if end_date <= start_date:
            raise ValidationException("End date must be after start date")
        
        if start_date < datetime.now().date():
            raise ValidationException("Start date cannot be in the past")


class PaymentValidator:
    """Validator for Payment domain entity"""
    
    @staticmethod
    def validate_amount(amount: float) -> None:
        """Validate payment amount"""
        if amount <= 0:
            raise ValidationException("Payment amount must be greater than 0")
        
        if amount > 1000000:  # Reasonable upper limit
            raise ValidationException("Payment amount exceeds maximum allowed")
    
    @staticmethod
    def validate_payment_method(method: str) -> None:
        """Validate payment method"""
        valid_methods = ['credit_card', 'debit_card', 'bank_transfer', 'paypal', 'other']
        if method.lower() not in valid_methods:
            raise ValidationException(f"Payment method must be one of: {', '.join(valid_methods)}")

