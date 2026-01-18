# Configuration settings for the Flask application

import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours default
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    TESTING = os.environ.get('TESTING', 'False').lower() in ['true', '1']
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:123@127.0.0.1:1433/RetinalHealthDB'
    CORS_HEADERS = 'Content-Type'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:123@127.0.0.1:1433/RetinalHealthDB'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:123@127.0.0.1:1433/RetinalHealthDB'


class ProductionConfig(Config):
    """Production configuration."""
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:123@127.0.0.1:1433/RetinalHealthDB'

    
template = {
    "swagger": "2.0",
    "info": {
        "title": "Todo API",
        "description": "API for managing todos",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ]
}
class SwaggerConfig:
    """Swagger configuration for AURA system."""
    template = {
        "swagger": "2.0",
        "info": {
            "title": "AURA - AI-Powered Retinal Disease Detection API",
            "description": "Complete REST API for AURA medical system including AI analysis, patient management, doctor reviews, messaging, and billing services",
            "version": "1.0.0",
            "contact": {
                "name": "AURA Development Team",
                "email": "support@aura-health.com"
            }
        },
        "basePath": "/api",
        "schemes": [
            "http",
            "https"
        ],
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ],
        "tags": [
            {"name": "Authentication", "description": "User authentication and registration"},
            {"name": "Roles", "description": "Role management operations"},
            {"name": "Accounts", "description": "User account management"},
            {"name": "Patients", "description": "Patient profile operations"},
            {"name": "Doctors", "description": "Doctor profile operations"},
            {"name": "Clinics", "description": "Clinic management"},
            {"name": "Retinal Images", "description": "Medical image upload and management"},
            {"name": "AI Analysis", "description": "AI-powered retinal disease detection"},
            {"name": "AI Results", "description": "AI analysis results and predictions"},
            {"name": "Medical Reports", "description": "Medical report generation and management"},
            {"name": "Doctor Reviews", "description": "Doctor validation and review operations"},
            {"name": "Notifications", "description": "User notification system"},
            {"name": "Messaging", "description": "Patient-doctor communication"},
            {"name": "Billing", "description": "Service packages, subscriptions and payments"}
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Enter only the token value (without 'Bearer ' prefix). Swagger will automatically format it as 'Authorization: Bearer {token}'"
            }
        }
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }