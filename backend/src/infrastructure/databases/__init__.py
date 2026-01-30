# Import Base first to ensure it's available for all models
from infrastructure.databases.base import Base

# Import AURA System models (Retinal Health Screening)
# These imports register models with SQLAlchemy Base
# Import models BEFORE importing mssql to avoid circular import issues
from infrastructure.models.role_model import RoleModel
from infrastructure.models.clinic_model import ClinicModel
from infrastructure.models.account_model import AccountModel
from infrastructure.models.notification_model import NotificationModel

from infrastructure.models.profiles.patient_profile_model import PatientProfileModel
from infrastructure.models.profiles.doctor_profile_model import DoctorProfileModel

from infrastructure.models.imaging.retinal_image_model import RetinalImageModel

from infrastructure.models.ai.ai_model_version_model import AiModelVersionModel
from infrastructure.models.ai.ai_analysis_model import AiAnalysisModel
from infrastructure.models.ai.ai_result_model import AiResultModel
from infrastructure.models.ai.ai_annotation_model import AiAnnotationModel

from infrastructure.models.medical.doctor_review_model import DoctorReviewModel
from infrastructure.models.medical.medical_report_model import MedicalReportModel

from infrastructure.models.messaging.conversation_model import ConversationModel
from infrastructure.models.messaging.message_model import MessageModel

from infrastructure.models.billing.service_package_model import ServicePackageModel
from infrastructure.models.billing.subscription_model import SubscriptionModel
from infrastructure.models.billing.payment_model import PaymentModel


def init_db(app):
    """Initialize database and create all tables"""
    # Lazy import to avoid circular import issues
    from infrastructure.databases.mssql import init_mssql
    init_mssql(app)