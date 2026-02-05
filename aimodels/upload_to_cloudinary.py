"""
Upload ảnh lên Cloudinary (dùng cho luồng Kaggle).
Đọc cấu hình từ biến môi trường: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET.
Có thể chạy: python upload_to_cloudinary.py [đường_dẫn_ảnh]
"""
import os
import sys

# Load .env nếu có (từ thư mục gốc dự án hoặc backend/src)
def _load_dotenv():
    try:
        from dotenv import load_dotenv
        for path in [os.path.join(os.path.dirname(__file__), '..', '.env'),
                     os.path.join(os.path.dirname(__file__), '..', 'backend', 'src', '.env')]:
            if os.path.isfile(path):
                load_dotenv(path)
                break
    except ImportError:
        pass

_load_dotenv()

import cloudinary
import cloudinary.uploader

cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
api_key = os.environ.get("CLOUDINARY_API_KEY")
api_secret = os.environ.get("CLOUDINARY_API_SECRET")

if not all([cloud_name, api_key, api_secret]):
    print("Lỗi: Đặt CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET trong .env")
    sys.exit(1)

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
)

def upload_file(file_path: str, folder: str = "retina_input") -> str:
    result = cloudinary.uploader.upload(file_path, folder=folder)
    return result["secure_url"]

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "retina.jpg"
    if not os.path.isfile(path):
        print(f"File không tồn tại: {path}")
        sys.exit(1)
    url = upload_file(path)
    print(url)
