from fastapi import FastAPI, UploadFile, File
import requests
import cloudinary
import cloudinary.uploader
import uuid
import os
from typing import Any

app = FastAPI()

# Configure Cloudinary from environment (fall back to existing values if present)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dmidkmbyp"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "256857942333283"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "dEV8dxWyWpCClSgv9F8ikse1abQ")
)

KAGGLE_AI_URL = os.getenv("KAGGLE_AI_URL", "https://relationless-nonagglomerative-ariel.ngrok-free.dev")

@app.get("/")
async def root() -> Any:
    return {"message": "AURA FastAPI (light) - Cloudinary + Kaggle AI", "docs": "/docs"}

@app.post("/retinal/analyze")
async def analyze_retina_cloudinary(file: UploadFile = File(...)) -> Any:
    # 1. Upload image to Cloudinary
    upload_result = cloudinary.uploader.upload(
        file.file,
        folder="retinal_images",
        public_id=str(uuid.uuid4())
    )

    image_url = upload_result.get("secure_url")

    # 2. Call external AI endpoint
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

    return {"image_url": image_url, "analysis": ai_result}

@app.post("/analyze-retina")
async def analyze_retina_local_stub(file: UploadFile = File(...)) -> Any:
    return {"error": "Local models unavailable. Use /retinal/analyze which calls remote Kaggle endpoint."}
