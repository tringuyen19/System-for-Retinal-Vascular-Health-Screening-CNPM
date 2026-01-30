from flask import Flask, jsonify
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from infrastructure.databases import init_db
from api.routes import register_routes
from config import Config, SwaggerConfig
from cors import init_cors

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 0. CORS - cho phép frontend (cổng khác hoặc file) gọi API
    init_cors(app)
    print("✅ CORS enabled for frontend")
    
    
    # 1. Initialize JWT
    jwt = JWTManager(app)
    print("✅ JWT Authentication initialized")
    
    # 2. Cấu hình Swagger/Flasgger cho API Documentation
    Swagger(app, template=SwaggerConfig.template, config=SwaggerConfig.swagger_config)
    print("✅ Swagger UI enabled at: /docs")
    
    # 3. Khởi tạo Database và Tạo bảng
    try:
        init_db(app)
        print("✅ Database initialized and tables created successfully.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    
    # 4. Đăng ký tất cả API Routes (19 controllers including auth)
    try:
        register_routes(app)
        print("✅ All API routes registered successfully.")
    except Exception as e:
        print(f"❌ Error registering routes: {e}")
    
    # 4. Root endpoint - API Information
    @app.route("/")
    def index():
        """API Root - Shows system information"""
        return jsonify({
            "message": "🏥 AURA - AI-Powered Retinal Disease Detection System",
            "version": "1.0.0",
            "status": "running",
            "database": "connected",
            "documentation": "/docs",
            "health_check": "/health",
            "features": {
                "core": ["Roles", "Accounts", "Patients", "Doctors", "Clinics"],
                "medical": ["Retinal Images", "AI Analysis", "AI Results", "Medical Reports"],
                "communication": ["Notifications", "Messaging", "Doctor Reviews"],
                "billing": ["Service Packages", "Subscriptions", "Payments"]
            },
            "total_endpoints": "178+",
            "architecture": "Clean Architecture"
        })
    
    # 5. Health check endpoint
    @app.route("/health")
    def health():
        """Health check endpoint for monitoring"""
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "api": "operational"
        })
    
    # 6. API Info endpoint
    @app.route("/api")
    def api_info():
        """API endpoints summary"""
        return jsonify({
            "message": "AURA API Endpoints",
            "base_paths": {
                "roles": "/api/roles",
                "accounts": "/api/accounts", 
                "patients": "/api/patient-profiles",
                "doctors": "/api/doctor-profiles",
                "clinics": "/api/clinics",
                "images": "/api/retinal-images",
                "ai_analysis": "/api/ai-analyses",
                "ai_results": "/api/ai-results",
                "reports": "/api/medical-reports",
                "reviews": "/api/doctor-reviews",
                "notifications": "/api/notifications",
                "conversations": "/api/conversations",
                "messages": "/api/messages",
                "packages": "/api/packages",
                "subscriptions": "/api/subscriptions",
                "payments": "/api/payments",
                "auth": "/api/auth"
            },
            "documentation": "/docs"
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    
    # Chạy ứng dụng trên cổng 9999
    app.run(host='0.0.0.0', port=9999, debug=True)
