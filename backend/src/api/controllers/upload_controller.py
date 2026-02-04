import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Blueprint, request
from werkzeug.utils import secure_filename

from api.middleware.auth_middleware import require_roles
from api.responses import success_response, error_response
from config import Config


upload_bp = Blueprint("uploads", __name__, url_prefix="/api/uploads")


ALLOWED_CATEGORIES = {"retinal", "heatmaps", "clinic"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _get_ext(filename: str) -> str:
    return (Path(filename).suffix or "").lower()


def _ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def _build_public_urls(rel_path: str) -> dict:
    """
    rel_path: path relative to /static, e.g. 'uploads/heatmaps/abc.png'
    """
    rel_path = rel_path.replace("\\", "/").lstrip("/")
    relative_url = "/static/" + rel_path
    # request.host_url already ends with '/'
    full_url = request.host_url.rstrip("/") + relative_url
    return {"url": relative_url, "full_url": full_url}


@upload_bp.route("", methods=["POST"])
def upload_file():
    """
    Upload a file to backend static/uploads and return a public URL.
    
    For clinic registration (category='clinic'), no authentication required.
    For other categories, authentication is required.

    Multipart form-data:
      - file: file binary
      - category: 'retinal' | 'heatmaps' | 'clinic' (default: 'retinal')
    """
    try:
        if "file" not in request.files:
            return error_response("Missing file. Use multipart/form-data with field name 'file'.", 400)

        f = request.files["file"]
        if not f or not f.filename:
            return error_response("Empty file.", 400)

        category = (request.form.get("category") or "retinal").strip().lower()
        if category not in ALLOWED_CATEGORIES:
            return error_response(f"Invalid category. Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}.", 400)
        
        # For clinic logo upload during registration, no auth required
        # For other categories, require authentication
        if category != "clinic":
            # Check authentication for non-clinic uploads
            try:
                from api.middleware.auth_middleware import verify_jwt_in_request
                verify_jwt_in_request()
            except Exception as e:
                return error_response("Authentication required for this category.", 401)

        ext = _get_ext(f.filename)
        if ext not in ALLOWED_EXTENSIONS:
            return error_response(
                f"Invalid file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
                400,
            )

        base_dir = getattr(Config, "STATIC_UPLOAD_DIR", None) or os.path.join(os.path.dirname(__file__), "..", "..", "static", "uploads")
        base_dir = os.path.abspath(base_dir)
        target_dir = os.path.join(base_dir, category)
        _ensure_dir(target_dir)

        safe_name = secure_filename(Path(f.filename).stem) or "file"
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        uniq = uuid.uuid4().hex[:10]
        filename = f"{safe_name}_{ts}_{uniq}{ext}"

        abs_path = os.path.join(target_dir, filename)
        f.save(abs_path)

        # Build URL relative to /static
        rel_path = f"uploads/{category}/{filename}"
        urls = _build_public_urls(rel_path)

        return success_response(
            {
                "category": category,
                "filename": filename,
                "relative_path": rel_path,
                **urls,
            },
            "File uploaded successfully",
            201,
        )

    except Exception as e:
        return error_response(f"Internal server error: {str(e)}", 500)

