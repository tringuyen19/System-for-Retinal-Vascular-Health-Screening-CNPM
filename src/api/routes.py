from api.controllers.auth_controller import auth_bp
from api.controllers.role_controller import role_bp
from api.controllers.account_controller import account_bp
from api.controllers.patient_controller import patient_bp
from api.controllers.doctor_controller import doctor_bp
from api.controllers.clinic_controller import clinic_bp
from api.controllers.retinal_image_controller import retinal_image_bp
from api.controllers.ai_analysis_controller import ai_analysis_bp
from api.controllers.ai_annotation_controller import ai_annotation_bp
from api.controllers.ai_model_version_controller import ai_model_version_bp
from api.controllers.ai_result_controller import ai_result_bp
from api.controllers.medical_report_controller import medical_report_bp
from api.controllers.doctor_review_controller import doctor_review_bp
from api.controllers.notification_controller import notification_bp
from api.controllers.conversation_controller import conversation_bp
from api.controllers.message_controller import message_bp
from api.controllers.service_package_controller import service_package_bp
from api.controllers.subscription_controller import subscription_bp
from api.controllers.payment_controller import payment_bp
from api.controllers.admin_controller import admin_bp
from api.controllers.audit_log_controller import audit_log_bp

def register_routes(app):
    """Register all API blueprints"""
    
    # AURA System routes - Authentication
    app.register_blueprint(auth_bp)
    
    # AURA System routes - Core
    app.register_blueprint(role_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(clinic_bp)
    
    # AURA System routes - Medical & AI
    app.register_blueprint(retinal_image_bp)
    app.register_blueprint(ai_analysis_bp)
    app.register_blueprint(ai_annotation_bp)
    app.register_blueprint(ai_model_version_bp)
    app.register_blueprint(ai_result_bp)
    app.register_blueprint(doctor_review_bp)
    app.register_blueprint(medical_report_bp)
    
    # AURA System routes - Communication & Billing
    app.register_blueprint(notification_bp)
    app.register_blueprint(conversation_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(service_package_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(payment_bp)
    
    # AURA System routes - Admin
    app.register_blueprint(admin_bp)
    app.register_blueprint(audit_log_bp)