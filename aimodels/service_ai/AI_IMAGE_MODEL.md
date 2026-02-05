 
# Mô hình Ảnh AI - CDS (Hỗ trợ Quyết định Lâm sàng)

Tài liệu này mô tả mô hình AI phân tích ảnh võng mạc và các thành phần Hỗ trợ Quyết định Lâm sàng (CDS) có trong kho mã tại thư mục `backend/src/cds/`.

## Tổng quan

- Vị trí: `backend/src/cds/`
- Điểm vào chính:
  - `vessel_analysis.py` - các hàm cho phân đoạn mạch máu và phân tích mặt nạ mạch (ví dụ `analyze_vessel_mask`)
  - `final_decision.py` - logic cấp cao hơn để tổng hợp kết quả phân tích thành khuyến nghị lâm sàng
  - `AI_IMAGE_MODEL.md` (tệp này) - tài liệu

## Mục đích

Pipeline CDS phân tích ảnh fundus võng mạc để phát hiện bất thường mạch máu và sinh ra các kết quả có cấu trúc, phục vụ cho các hệ thống hạ nguồn (báo cáo, cảnh báo, dashboard). Nó hỗ trợ phân tích theo lô hoặc theo ảnh đơn lẻ và cung cấp giao diện lập trình đơn giản để tích hợp với ứng dụng Flask và một endpoint demo FastAPI.

## Các thành phần

- Tiền xử lý: chuẩn hóa ảnh, thay đổi kích thước, tăng cường tương phản.
- Phân đoạn: trích xuất mặt nạ mạch máu (mô hình tương tự U-Net hoặc tương đương).
- Trích xuất đặc trưng: đo mật độ mạch, độ xoắn (tortuosity), số điểm phân nhánh, và các thống kê theo vùng.
- Đánh giá rủi ro / quyết định cuối: áp dụng qui tắc hoặc mô hình ML để tổng hợp và phân loại mức rủi ro (thấp/trung bình/cao) và đưa ra khuyến nghị theo dõi.

## Đầu vào / Đầu ra

- Đầu vào: URL ảnh hoặc đường dẫn cục bộ tới ảnh fundus (RGB). Một số tiện ích nhận URL mặt nạ đã tính trước.
- Đầu ra: đối tượng JSON với các khóa ví dụ như:
  - `vessel_mask_url` (tuỳ chọn)
  - `vessel_density`
  - `tortuosity`
  - `lesion_count`
  - `risk_level` (low/medium/high)
  - `confidence` (0..1)
  - `analysis_timestamp`

Ví dụ kết quả:

```json
{
  "vessel_mask_url": "https://.../mask.png",
  "vessel_density": 0.18,
  "tortuosity": 1.32,
  "lesion_count": 2,
  "risk_level": "medium",
  "confidence": 0.86
}
```

## Cách gọi pipeline

Từ mã Python trong dự án này:

```python
from cds.vessel_analysis import analyze_vessel_mask

result = analyze_vessel_mask('https://example.com/fundus.jpg')
```

Dự án cũng có một endpoint demo FastAPI tại `/analyze-retina` gọi `analyze_vessel_mask` và trả về kết quả (xem `backend/src/app.py`).

## Phụ thuộc

- Các gói Python dùng cho thành phần CDS được liệt kê trong `backend/src/requirements.txt` (các thư viện mô hình như `torch`, `opencv-python`, v.v.). Hãy đảm bảo môi trường ảo đã cài các phụ thuộc này.

## Kiểm thử

- Giai đoạn 1 chưa bao gồm unit-test cho CDS; để kiểm thử thủ công, dùng endpoint demo FastAPI hoặc gọi trực tiếp các hàm trong mã nguồn.

## Ghi chú & bước tiếp theo

- Bổ sung quản lý phiên bản mô hình và metadata (tên dữ liệu huấn luyện, ngày huấn luyện, các chỉ số) vào kho lưu trữ hoặc hệ thống đăng ký mô hình.
- Thêm bộ kiểm thử tự động và tập ảnh mẫu (bộ nhỏ) để kiểm tra CI.
- Cân nhắc chuyển tác vụ suy diễn nặng sang các worker bất đồng bộ (Celery/RQ) khi chạy ở quy mô lớn.

---
Tạo: 2026-02-03 — Ghi chú: helper `get_cds_model_info()` đã được thêm vào `backend/src/app.py` để cung cấp metadata mô hình dưới dạng chương trình.



# Kiến trúc tổng quan xây dựng output và heatmap
Ảnh võng mạc
   ↓
[KAGGLE NOTEBOOK]
   ├─ Model 1: U-Net → vessel_mask + vessel_heatmap
   ├─ Model 2: EfficientNet → DR probabilities + Grad-CAM
   ├─ Logic y khoa → disease_type / risk / confidence
   ├─ Upload outputs → Cloudinary
   └─ Xuất JSON
        ↓
[BACKEND PYTHON Ở MÁY]
   └─ Call JSON → hiển thị / lưu DB

# Cấu trúc kì vọng khi chạy 
[User / Frontend]
     |
     | (1) Upload ảnh võng mạc
     ↓
[Backend (Python / FastAPI)]
     |
     | (2) Upload ảnh lên Cloudinary
     ↓
[Cloudinary - FREE CDN]
     |
     | (3) Gửi URL ảnh → Kaggle
     ↓
[Kaggle Notebook = AI Core]
     |
     | (4) Chạy 2 model + heatmap
     |     - U-Net (vessel)
     |     - EfficientNet (DR)
     ↓
[Kaggle]
     |
     | (5) Upload kết quả (mask, heatmap, JSON) → Cloudinary
     ↓
[Backend]
     |
     | (6) Call JSON kết quả
     ↓
[Frontend]
     |
     | (7) Hiển thị kết quả + ảnh heatmap
