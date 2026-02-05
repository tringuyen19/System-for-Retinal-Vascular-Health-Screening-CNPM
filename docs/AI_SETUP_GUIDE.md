# Hướng dẫn chạy AI chuẩn đoán bệnh võng mạc (AURA)

Tài liệu mô tả cấu trúc thư mục **aimodels**, hai cách chạy AI (local và Kaggle + Cloudinary), và cách tích hợp với luồng dự án (upload ảnh → AI phân tích → lưu kết quả vào backend).

---

## 1. Cấu trúc thư mục `aimodels/`

```
aimodels/
├── service_ai/                 # Core AI inference (chạy local)
│   ├── AI_IMAGE_MODEL.md       # Mô tả pipeline CDS, luồng Kaggle/Cloudinary
│   ├── dr_server.py            # EfficientNetB1 – phân loại bệnh DR (5 giai đoạn)
│   ├── vessel.py               # U-Net – phân đoạn mạch máu + heatmap
│   └── models/                 # (cần tạo) Đặt file weights tại đây
│       ├── efficientnetb1_weights.h5
│       └── seg.h5
├── utils_ai/
│   └── reprocess.py            # Tiền xử lý ảnh: resize 224x224, chuẩn hóa
└── upload_to_cloudinary.py     # Script upload ảnh lên Cloudinary (dùng cho luồng Kaggle)
```

**Bảo mật:** `upload_to_cloudinary.py` đã dùng biến môi trường (xem mục 4.2). Không commit API secret lên git.

**Lưu ý:** `dr_server.py` và `vessel.py` đang tham chiếu tới `models/` cùng cấp (ví dụ `models/efficientnetb1_weights.h5`). Khi chạy local, cần đặt đúng đường dẫn (ví dụ `aimodels/service_ai/models/`).

---

## 2. Luồng dự án (tổng quan)

Luồng chuẩn trong dự án:

1. **User / Frontend** upload ảnh võng mạc.
2. **Backend (Flask)** nhận ảnh, lưu bản ghi `retinal_images` và (nếu có active AI model) tạo `ai_analysis` + `ai_results`.
3. **AI** có thể chạy theo hai hướng:
   - **Cách A – Local:** Backend (hoặc service tách) gọi code trong `aimodels/service_ai` (cần file weights).
   - **Cách B – Kaggle + Cloudinary:** Backend upload ảnh lên Cloudinary → Kaggle Notebook nhận URL, chạy 2 model (U-Net + EfficientNet) → upload mask/heatmap/JSON lên Cloudinary → Backend lấy JSON và lưu vào `ai_analysis` / `ai_results`.

Hiện tại backend đang dùng **dữ liệu giả (mock)** khi tạo `ai_analysis` và `ai_results`. Để “chạy đúng AI” cần thay bước tạo kết quả bằng gọi AI thật (local hoặc từ Kaggle/Cloudinary).

---

## 3. Cách 1: Chạy AI local (aimodels + weights)

### 3.1. Chuẩn bị

- Python 3.8+ (cùng môi trường có TensorFlow 2.x).
- Hai file weights:
  - **U-Net (vessel):** `seg.h5` – dùng trong `vessel.py`.
  - **EfficientNetB1 (DR):** `efficientnetb1_weights.h5` – dùng trong `dr_server.py`.

Đặt vào thư mục (ví dụ):

- `aimodels/service_ai/models/seg.h5`
- `aimodels/service_ai/models/efficientnetb1_weights.h5`

Sửa trong `dr_server.py` và `vessel.py` đường dẫn load model cho đúng (ví dụ `models/seg.h5` → `models/seg.h5` với working directory là `aimodels/service_ai`).

### 3.2. Cài đặt thư viện

```bash
pip install tensorflow opencv-python numpy
```

(Các gói khác đã có trong `backend/requirements.txt` có thể dùng chung.)

### 3.3. Gọi pipeline local

- **Tiền xử lý:** dùng `utils_ai/reprocess.py` để đọc ảnh (file hoặc bytes) → resize 224x224, chuẩn hóa.
- **Vessel:** `vessel_segmentation(image)` → vessel_mask, vessel_ratio, heatmap.
- **DR:** `dr_classification(image)` → dr_stage (0–4), dr_probability.

Ví dụ tích hợp vào backend (ý tưởng):

- Sau khi lưu ảnh (có `image_id`, `image_url` hoặc đường dẫn file), backend gọi:
  - Load ảnh → `reprocess.preprocess_image(...)`.
  - Gọi `vessel.vessel_segmentation(...)` và `dr_server.dr_classification(...)`.
  - Map `dr_stage` → `disease_type`, tính `risk_level`, `confidence_score`.
  - Tạo `ai_analysis` (status `completed`) và `ai_result` qua `AiAnalysisService` / `AiResultService` với dữ liệu thật thay cho mock.

Chi tiết API backend (create_analysis, create_result) xem tại `backend/src/services/ai_analysis_service.py` và `ai_result_service.py`.

---

## 4. Cách 2: Chạy AI qua Kaggle Notebook + Cloudinary

Đây là luồng mô tả trong `AI_IMAGE_MODEL.md`: ảnh lên Cloudinary → Kaggle xử lý → kết quả (mask, heatmap, JSON) lên lại Cloudinary → Backend đọc JSON.

### 4.1. Kaggle Notebook (AI Core)

- Notebook tham khảo: **[AI Core - Kaggle](https://www.kaggle.com/code/akangtri/ai-core-tien/edit?fromFork=1)**  
- Notebook này cần:
  - Nhận **URL ảnh** (sau khi backend upload lên Cloudinary).
  - Chạy **Model 1 – U-Net:** vessel mask + vessel heatmap.
  - Chạy **Model 2 – EfficientNet:** DR probabilities + Grad-CAM (nếu có).
  - Áp **logic y khoa** để ra `disease_type` / `risk_level` / `confidence`.
  - Upload kết quả (mask, heatmap, JSON) lên Cloudinary.
  - Xuất JSON mô tả kết quả (ví dụ `disease_type`, `risk_level`, `confidence`, URL mask/heatmap).

### 4.2. Cấu hình Cloudinary và Backend (.env)

1. Đăng ký tài khoản tại [cloudinary.com](https://cloudinary.com).
2. Lấy **Cloud name**, **API Key**, **API Secret** từ Dashboard.
3. Thêm vào `backend/src/.env` (và/hoặc `.env` ở thư mục gốc nếu chạy script `aimodels/upload_to_cloudinary.py`):

```env
# Cloudinary (bắt buộc cho Cách 2)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Bật luồng Kaggle: tạo analysis pending, chờ submit-kaggle-result
AI_RESULT_SOURCE=kaggle

# Secret để Kaggle notebook gọi submit-kaggle-result (đổi trong production)
KAGGLE_WEBHOOK_SECRET=your_secret_string
```

Script `aimodels/upload_to_cloudinary.py` đã đọc từ biến môi trường (và tự load `.env` nếu có).

### 4.3. Backend endpoints đã thiết lập (Cách 2)

| Endpoint | Mô tả |
|----------|--------|
| `POST /api/retinal-images/upload-for-ai` | Multipart: `file` + `patient_id`, `clinic_id`, `uploaded_by`, `image_type`, `eye_side`. Upload file lên Cloudinary, tạo `retinal_image` + `ai_analysis` (pending). Trả về `image_id`, `analysis_id`, `image_url` (Cloudinary) để dùng trong Kaggle. Cần JWT. |
| `POST /api/ai-analysis/submit-kaggle-result` | Body JSON: `image_id`, `disease_type`, `risk_level`, `confidence_score` [, `processing_time`, `vessel_mask_url`, `heatmap_url` ]. Header: `X-Kaggle-Secret: <KAGGLE_WEBHOOK_SECRET>`. Không dùng JWT. Cập nhật analysis → completed và tạo `ai_result`. |

- Khi `AI_RESULT_SOURCE=kaggle`, cả `POST /api/retinal-images` (JSON với `image_url`) cũng tạo analysis **pending** thay vì completed + mock.

### 4.4. Luồng từng bước (đã tích hợp)

| Bước | Thành phần | Hành động |
|------|------------|-----------|
| 1 | Frontend / User | Gọi `POST /api/retinal-images/upload-for-ai` (multipart: file + metadata) hoặc upload ảnh rồi gửi `image_url` qua `POST /api/retinal-images` (khi `AI_RESULT_SOURCE=kaggle`). |
| 2 | Backend | Upload file lên Cloudinary (upload-for-ai) hoặc nhận `image_url`; lưu `retinal_images`; tạo `ai_analysis` với status **pending**. Trả về `image_id`, `analysis_id`, `image_url` (Cloudinary). |
| 3 | Bạn / Kaggle | Mở notebook [AI Core](https://www.kaggle.com/code/akangtri/ai-core-tien/edit?fromFork=1), nhập **image_url** (và **image_id** để gửi lại). Chạy notebook. |
| 4 | Kaggle Notebook | Đọc ảnh từ URL → chạy U-Net + EfficientNet → ra disease_type, risk_level, confidence; upload mask/heatmap lên Cloudinary (tuỳ chọn). |
| 5 | Kaggle Notebook | Gọi `POST /api/ai-analysis/submit-kaggle-result` với header `X-Kaggle-Secret: <KAGGLE_WEBHOOK_SECRET>` và body `{ "image_id": ..., "disease_type": "...", "risk_level": "...", "confidence_score": ... }`. Backend phải accessible (localhost chỉ chạy được nếu Kaggle không gọi về; dùng ngrok hoặc deploy để Kaggle gọi được). |
| 6 | Backend | Nhận submit-kaggle-result → đánh dấu analysis **completed**, tạo `ai_result`, đánh dấu ảnh **analyzed**, gửi thông báo (FR-9, FR-29). |
| 7 | Frontend | Gọi API lấy kết quả (ai-results, ai-analysis) và hiển thị + ảnh heatmap/mask. |

### 4.4. Cách “gửi” ảnh tới Kaggle và lấy kết quả

- **Kaggle Notebook không có API public** để backend gọi trực tiếp. Các cách thực tế:
  - **Thủ công:** Chạy notebook trên Kaggle, nhập URL ảnh (từ Cloudinary), chạy xong notebook upload kết quả lên Cloudinary; backend định kỳ kiểm tra thư mục/URL kết quả trên Cloudinary và cập nhật DB.
  - **Tự động một phần:** Backend upload ảnh lên Cloudinary rồi ghi vào bảng “hàng đợi” (ví dụ `pending_ai_jobs` với `image_id`, `image_url`). Một script chạy trên máy có Kaggle CLI / hoặc đồng bộ với Kaggle dataset sẽ đọc hàng đợi, chạy notebook (hoặc chạy code tương tự local), upload kết quả lên Cloudinary rồi gọi API backend (webhook) để cập nhật `ai_analysis` + `ai_result`.
  - **Chuyển logic sang backend/local:** Export code từ Kaggle notebook sang repo (ví dụ vào `aimodels/service_ai`), chạy inference trên server/worker (như Cách 1), không phụ thuộc Kaggle runtime.

### 4.5. Gọi submit-kaggle-result từ Kaggle (Python)

Cuối notebook, sau khi có `image_id`, `disease_type`, `risk_level`, `confidence_score`:

```python
import requests
BACKEND_URL = "http://localhost:9999"  # hoặc ngrok / URL deploy
KAGGLE_SECRET = "your_secret_string"   # trùng KAGGLE_WEBHOOK_SECRET trong .env
resp = requests.post(
    f"{BACKEND_URL}/api/ai-analysis/submit-kaggle-result",
    json={"image_id": image_id, "disease_type": "diabetic_retinopathy", "risk_level": "medium", "confidence_score": 85.5},
    headers={"X-Kaggle-Secret": KAGGLE_SECRET},
)
print(resp.status_code, resp.json())
```

Kaggle chạy trên server; để gọi về localhost cần ngrok hoặc deploy backend.

### 4.6. Định dạng JSON gửi lên submit-kaggle-result

Ví dụ body:

```json
{
  "image_id": 123,
  "vessel_mask_url": "https://res.cloudinary.com/.../mask.png",
  "vessel_density": 0.18,
  "heatmap_url": "https://res.cloudinary.com/.../heatmap.png",
  "disease_type": "diabetic_retinopathy",
  "dr_stage": 2,
  "risk_level": "medium",
  "confidence": 0.86,
  "analysis_timestamp": "2026-02-05T10:00:00Z"
}
```

Endpoint `submit-kaggle-result` nhận:
- **Bắt buộc:** `image_id`, `disease_type`, `risk_level`, `confidence_score` (0–100).
- **Tuỳ chọn:** `processing_time` (giây), `vessel_mask_url`, `heatmap_url` (chưa lưu DB nhưng có thể dùng sau).

---

## 5. Tích hợp với Backend (luồng đúng dự án)

### 5.1. Luồng hiện tại (mock)

- `POST /api/retinal-images`: tạo `retinal_image`, nếu có **active AI model version** thì gọi `analysis_service.create_analysis(...)` với `status='completed'` và `processing_time` random.
- `AiAnalysisService.create_analysis` gọi `_auto_create_result(analysis_id)` → tạo `ai_result` với dữ liệu giả từ `_generate_mock_result_data()`.

### 5.2. Chuyển sang AI thật (gợi ý)

- **Option A – Gọi AI ngay trong request (đồng bộ):**  
  Sau khi lưu ảnh, gọi `aimodels` (Cách 1) hoặc gọi service nội bộ đã bọc Kaggle/Cloudinary. Nhận `disease_type`, `risk_level`, `confidence_score` → tạo `ai_analysis` (status `completed`) và `ai_result` qua `AiResultService.create_result(...)` thay vì mock.  
  Lưu ý: request có thể chậm (vài giây đến vài chục giây), nên giới hạn kích thước ảnh và timeout.

- **Option B – Bất đồng bộ (khuyến nghị khi dùng Kaggle):**  
  1. Upload ảnh → lưu `retinal_image`, tạo `ai_analysis` với `status='pending'` (không tạo `ai_result` ngay).  
  2. Đẩy job vào queue (Redis/Celery hoặc bảng `pending_ai_jobs`).  
  3. Worker: lấy job → upload ảnh lên Cloudinary (nếu cần) → gửi URL cho Kaggle hoặc chạy local AI → nhận JSON → gọi `mark_as_completed` + `AiResultService.create_result(...)` với dữ liệu thật.  
  4. Frontend polling `GET /api/ai-analyses/:id` hoặc nhận thông báo khi trạng thái chuyển sang `completed`.

---

## 6. Checklist chạy AI theo đúng luồng dự án

**Cách 2 (Kaggle) – đã thiết lập trong repo:**

- [ ] **Cloudinary:** Tạo tài khoản, thêm `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` vào `backend/src/.env`.
- [ ] **Backend .env:** Thêm `AI_RESULT_SOURCE=kaggle` và `KAGGLE_WEBHOOK_SECRET=<chuỗi bí mật>`.
- [ ] **Backend:** Cài `pip install cloudinary`, chạy Flask từ `backend/src` (có active AI model version trong DB).
- [ ] **Upload ảnh:** Dùng `POST /api/retinal-images/upload-for-ai` (file + metadata) hoặc `POST /api/retinal-images` với `image_url` (Cloudinary); nhận `image_id`, `image_url` cho Kaggle.
- [ ] **Kaggle:** Trong notebook [ai-core-tien](https://www.kaggle.com/code/akangtri/ai-core-tien/edit?fromFork=1), nhập `image_url` (và lưu `image_id`), chạy model, gọi `POST .../submit-kaggle-result` với header `X-Kaggle-Secret` (backend phải accessible từ Kaggle: dùng ngrok hoặc deploy).
- [ ] **Frontend:** Gọi API ai-results / ai-analysis để hiển thị kết quả và ảnh heatmap/mask.

---

## 7. Tài liệu và link tham khảo

- **Kaggle notebook (AI Core):**  
  https://www.kaggle.com/code/akangtri/ai-core-tien/edit?fromFork=1  
- **Mô tả pipeline CDS và luồng Kaggle/Cloudinary:**  
  `aimodels/service_ai/AI_IMAGE_MODEL.md`  
- **Backend – AI analysis:**  
  `backend/src/services/ai_analysis_service.py`  
- **Backend – AI result:**  
  `backend/src/services/ai_result_service.py`  
- **Backend – Upload ảnh và auto-trigger analysis:**  
  `backend/src/api/controllers/retinal_image_controller.py`
