"""
Cloudinary service - upload ảnh lên Cloudinary (dùng cho luồng Kaggle: ảnh công khai cho notebook đọc).
"""
import os
from typing import Union, Optional, Any

from config import Config


def is_cloudinary_configured() -> bool:
    return bool(
        getattr(Config, 'CLOUDINARY_CLOUD_NAME', None)
        and getattr(Config, 'CLOUDINARY_API_KEY', None)
        and getattr(Config, 'CLOUDINARY_API_SECRET', None)
    )


def upload_image(
    file_or_path: Union[bytes, str, Any],
    folder: str = "retina_input",
    public_id: Optional[str] = None,
) -> str:
    """
    Upload ảnh lên Cloudinary.
    :param file_or_path: File object (có .read()), đường dẫn file (str), hoặc bytes.
    :param folder: Thư mục trên Cloudinary (mặc định retina_input).
    :param public_id: Tùy chọn public_id (nếu không có sẽ dùng tên file hoặc auto).
    :return: secure_url của ảnh đã upload.
    :raises ValueError: Nếu chưa cấu hình Cloudinary hoặc upload lỗi.
    """
    if not is_cloudinary_configured():
        raise ValueError(
            "Cloudinary chưa được cấu hình. Đặt CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET trong .env"
        )

    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET,
    )

    opts = {"folder": folder}
    if public_id:
        opts["public_id"] = public_id

    if hasattr(file_or_path, "read"):
        # File-like (e.g. FileStorage from request.files)
        result = cloudinary.uploader.upload(file_or_path, **opts)
    elif isinstance(file_or_path, bytes):
        result = cloudinary.uploader.upload(file_or_path, **opts)
    elif isinstance(file_or_path, str):
        result = cloudinary.uploader.upload(file_or_path, **opts)
    else:
        raise ValueError("file_or_path phải là file object, bytes, hoặc đường dẫn str")

    url = result.get("secure_url")
    if not url:
        raise ValueError("Cloudinary không trả về secure_url")
    return url
