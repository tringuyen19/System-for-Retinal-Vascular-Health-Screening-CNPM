"""
API Schemas for AURA - AI-Powered Retinal Disease Detection System
All Marshmallow schemas for request validation and response serialization
"""

# Authentication Schemas
from .auth_schema import (
    LoginRequestSchema,
    RegisterRequestSchema,
    AuthResponseSchema
)

# Core Management Schemas
from .role_schema import (
    RoleRequestSchema,
    RoleResponseSchema
)

from .account_schema import (
    AccountCreateRequestSchema,
    AccountUpdateRequestSchema,
    AccountResponseSchema
)

from .patient_schema import (
    PatientProfileCreateRequestSchema,
    PatientProfileUpdateRequestSchema,
    PatientProfileResponseSchema
)

from .doctor_schema import (
    DoctorProfileCreateRequestSchema,
    DoctorProfileUpdateRequestSchema,
    DoctorProfileResponseSchema
)

from .clinic_schema import (
    ClinicCreateRequestSchema,
    ClinicUpdateRequestSchema,
    ClinicResponseSchema
)

# Medical & AI Schemas
from .retinal_image_schema import (
    RetinalImageCreateRequestSchema,
    RetinalImageUpdateRequestSchema,
    RetinalImageResponseSchema,
    RetinalImageBulkCreateRequestSchema
)

from .ai_analysis_schema import (
    AiAnalysisCreateRequestSchema,
    AiAnalysisUpdateRequestSchema,
    AiAnalysisResponseSchema
)

from .ai_result_schema import (
    AiResultCreateRequestSchema,
    AiResultUpdateRequestSchema,
    AiResultResponseSchema
)

from .ai_annotation_schema import (
    AiAnnotationCreateRequestSchema,
    AiAnnotationUpdateRequestSchema,
    AiAnnotationResponseSchema
)

from .ai_model_version_schema import (
    AiModelVersionCreateRequestSchema,
    AiModelVersionUpdateRequestSchema,
    AiModelVersionResponseSchema
)

from .medical_report_schema import (
    MedicalReportCreateRequestSchema,
    MedicalReportUpdateRequestSchema,
    MedicalReportResponseSchema
)

from .doctor_review_schema import (
    DoctorReviewCreateRequestSchema,
    DoctorReviewUpdateRequestSchema,
    DoctorReviewResponseSchema
)

# Communication Schemas
from .notification_schema import (
    NotificationCreateRequestSchema,
    NotificationUpdateRequestSchema,
    NotificationResponseSchema
)

from .conversation_schema import (
    ConversationCreateRequestSchema,
    ConversationUpdateRequestSchema,
    ConversationResponseSchema
)

from .message_schema import (
    MessageCreateRequestSchema,
    MessageResponseSchema
)

# Billing Schemas
from .service_package_schema import (
    ServicePackageCreateRequestSchema,
    ServicePackageUpdateRequestSchema,
    ServicePackageResponseSchema
)

from .subscription_schema import (
    SubscriptionCreateRequestSchema,
    SubscriptionUpdateRequestSchema,
    SubscriptionResponseSchema
)

from .payment_schema import (
    PaymentCreateRequestSchema,
    PaymentUpdateRequestSchema,
    PaymentResponseSchema
)

# Admin Schemas
from .admin_schema import (
    AiConfigurationUpdateRequestSchema,
    AdminDashboardResponseSchema,
    AdminAnalyticsResponseSchema
)

__all__ = [
    # Authentication
    'LoginRequestSchema',
    'RegisterRequestSchema',
    'AuthResponseSchema',
    # Core Management
    'RoleRequestSchema',
    'RoleResponseSchema',
    'AccountCreateRequestSchema',
    'AccountUpdateRequestSchema',
    'AccountResponseSchema',
    'PatientProfileCreateRequestSchema',
    'PatientProfileUpdateRequestSchema',
    'PatientProfileResponseSchema',
    'DoctorProfileCreateRequestSchema',
    'DoctorProfileUpdateRequestSchema',
    'DoctorProfileResponseSchema',
    'ClinicCreateRequestSchema',
    'ClinicUpdateRequestSchema',
    'ClinicResponseSchema',
    
    # Medical & AI
    'RetinalImageCreateRequestSchema',
    'RetinalImageUpdateRequestSchema',
    'RetinalImageResponseSchema',
    'RetinalImageBulkCreateRequestSchema',
    'AiAnalysisCreateRequestSchema',
    'AiAnalysisUpdateRequestSchema',
    'AiAnalysisResponseSchema',
    'AiResultCreateRequestSchema',
    'AiResultUpdateRequestSchema',
    'AiResultResponseSchema',
    'AiAnnotationCreateRequestSchema',
    'AiAnnotationUpdateRequestSchema',
    'AiAnnotationResponseSchema',
    'AiModelVersionCreateRequestSchema',
    'AiModelVersionUpdateRequestSchema',
    'AiModelVersionResponseSchema',
    'MedicalReportCreateRequestSchema',
    'MedicalReportUpdateRequestSchema',
    'MedicalReportResponseSchema',
    'DoctorReviewCreateRequestSchema',
    'DoctorReviewUpdateRequestSchema',
    'DoctorReviewResponseSchema',
    
    # Communication
    'NotificationCreateRequestSchema',
    'NotificationUpdateRequestSchema',
    'NotificationResponseSchema',
    'ConversationCreateRequestSchema',
    'ConversationUpdateRequestSchema',
    'ConversationResponseSchema',
    'MessageCreateRequestSchema',
    'MessageResponseSchema',
    
    # Billing
    'ServicePackageCreateRequestSchema',
    'ServicePackageUpdateRequestSchema',
    'ServicePackageResponseSchema',
    'SubscriptionCreateRequestSchema',
    'SubscriptionUpdateRequestSchema',
    'SubscriptionResponseSchema',
    'PaymentCreateRequestSchema',
    'PaymentUpdateRequestSchema',
    'PaymentResponseSchema',

    # Admin
    'AiConfigurationUpdateRequestSchema',
    'AdminDashboardResponseSchema',
    'AdminAnalyticsResponseSchema',
]

