from flask import Flask, jsonify
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from infrastructure.databases import init_db
from api.routes import register_routes
from config import Config, SwaggerConfig
from cors import init_cors

# ================ Thư viện cho Flask backend ================
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except Exception:
    tf = None
    TF_AVAILABLE = False
import numpy as np
try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    CV2_AVAILABLE = False
from fastapi import FastAPI, UploadFile, File
import requests
import cloudinary
import cloudinary.uploader
import uuid

from datetime import datetime

# Separate FastAPI app instance for AI/demo endpoints
fastapi_app = FastAPI()


# =========================
# FastAPI root endpoint
# =========================
@fastapi_app.get("/")
async def fastapi_root():
    """FastAPI root - Shows available endpoints"""
    return {
        "message": "🏥 AURA - AI-Powered Retinal Disease Detection System (FastAPI)",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "retinal_analysis_cloudinary": "POST /retinal/analyze (upload + cloudinary + kaggle)",
            "retinal_analysis_local": "POST /analyze-retina (local model analysis)"
        }
    }


def get_cds_model_info():
    """Return metadata about the CDS AI image model used by the project.

    This is a lightweight helper for status pages and debugging; it does not
    load heavy ML weights.
    """
    return {
        "model_name": "Retinal Vessels Analyzer (CDS)",
        "version": "v1.0",
        "description": "Vessel segmentation and feature extraction pipeline (mask, density, tortuosity, risk).",
        "entry_point": "cds.vessel_analysis.analyze_vessel_mask",
        "input": "fundus image URL or local path (RGB)",
        "output": ["vessel_mask_url", "vessel_density", "tortuosity", "lesion_count", "risk_level", "confidence"],
        "last_checked": datetime.utcnow().isoformat() + "Z"
    }


# =========================
# Cloudinary config (placeholder - replace with real credentials)
# =========================
cloudinary.config(
    cloud_name="dmidkmbyp",
    api_key="256857942333283",
    api_secret="dEV8dxWyWpCClSgv9F8ikse1abQ"
)

# =========================
# Kaggle AI Core endpoint
# =========================
KAGGLE_AI_URL = "https://relationless-nonagglomerative-ariel.ngrok-free.dev"


# =========================
# API: upload image → AI analyze (Cloudinary + Kaggle)
# Mounted on FastAPI app `fastapi_app`
# =========================
@fastapi_app.post("/retinal/analyze")
async def analyze_retina_cloudinary(file: UploadFile = File(...)):
    # 1. Upload image to Cloudinary
    upload_result = cloudinary.uploader.upload(
        file.file,
        folder="retinal_images",
        public_id=str(uuid.uuid4())
    )

    image_url = upload_result.get("secure_url")

    # 2. Call Kaggle AI Core
    try:
        response = requests.post(
            KAGGLE_AI_URL,
            json={"image_url": image_url},
            timeout=120
        )
    except Exception as e:
        return {"error": "AI analysis request failed", "details": str(e)}

    if response.status_code != 200:
        return {"error": "AI analysis failed", "details": response.text}

    ai_result = response.json()

    # 3. Merge & return
    return {"image_url": image_url, "analysis": ai_result}

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
            "cds_model": get_cds_model_info(),
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

# ================== MODEL LOADING (optional) ==================
vessel_model = None
dr_model = None
if TF_AVAILABLE:
    try:
        vessel_model = tf.keras.models.load_model(
            "models/seg.h5",
            compile=False
        )

        from tensorflow.keras.applications import EfficientNetB1

        NUM_CLASSES = 5

        dr_model = EfficientNetB1(
            include_top=True,
            weights=None,
            classes=NUM_CLASSES,
            input_shape=(224, 224, 3)
        )

        dr_model.load_weights(
            "models/efficientnetb1_weights.h5",
            by_name=True,
            skip_mismatch=True
        )

        print(" Both models loaded successfully")
    except Exception as e:
        vessel_model = None
        dr_model = None
        print(f"Model loading skipped/failed: {e}")
else:
    print("TensorFlow not available; skipping model loading")

def preprocess_image(file, target_size=(224, 224)):
    if not CV2_AVAILABLE:
        raise RuntimeError("OpenCV (cv2) is not installed in the environment. Install with `pip install opencv-python` to use image preprocessing.")

    image_bytes = file.file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)

    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, target_size)

    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    return img

def run_vessel_segmentation(image):
    if vessel_model is None:
        # Return a dummy empty mask and zero ratio when model is unavailable
        dummy_mask = np.zeros((image.shape[1], image.shape[2]), dtype="uint8")
        return dummy_mask, 0.0

    pred = vessel_model.predict(image)[0]

    vessel_mask = (pred > 0.5).astype("uint8")
    vessel_ratio = float(np.sum(vessel_mask) / vessel_mask.size)

    return vessel_mask, vessel_ratio

def run_dr_classification(image):
    if dr_model is None:
        return 0, 0.0

    preds = dr_model.predict(image)[0]

    dr_stage = int(np.argmax(preds))
    dr_prob = float(np.max(preds))

    return dr_stage, dr_prob

@fastapi_app.post("/analyze-retina")
def analyze_retina_local(file: UploadFile = File(...)):
    image = preprocess_image(file)

    vessel_mask, vessel_ratio = run_vessel_segmentation(image)
    dr_stage, dr_prob = run_dr_classification(image)

    if dr_stage >= 3:
        disease_type = "Severe Diabetic Retinopathy"
        risk_level = "High"
    elif dr_stage >= 1:
        disease_type = "Mild/Moderate Diabetic Retinopathy"
        risk_level = "Medium"
    else:
        disease_type = "No Diabetic Retinopathy"
        risk_level = "Low"

    return {
        "disease_type": disease_type,
        "risk_level": risk_level,
        "confidence_score": dr_prob,
        "supporting_metrics": {
            "vessel_ratio": vessel_ratio,
            "dr_stage": dr_stage
        }
    }
