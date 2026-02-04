# 🏥 AURA - Luồng Upload Ảnh Và Chạy Models AI

## 📋 Mục Lục
1. [Kiến Trúc Tổng Quan](#kiến-trúc-tổng-quan)
2. [Luồng Upload Ảnh](#luồng-upload-ảnh)
3. [Luồng Chạy AI Models](#luồng-chạy-ai-models)
4. [Các API Endpoint](#các-api-endpoint)
5. [Models AI](#models-ai)
6. [Cấu Trúc Database](#cấu-trúc-database)

---

## 🏗️ Kiến Trúc Tổng Quan

Hệ thống sử dụng **Clean Architecture** với 4 layer chính:

```
┌─────────────────────────────────────────────┐
│     API Layer (Flask & FastAPI)             │
│  - Controllers / Routes                     │
│  - Request/Response Validation             │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│     Service Layer (Business Logic)          │
│  - RetinalImageService                     │
│  - AiAnalysisService                       │
│  - SubscriptionService                     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│   Repository/Infrastructure Layer           │
│  - RetinalImageRepository                  │
│  - AiAnalysisRepository                    │
│  - Database (MSSQL)                        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│      Domain Layer (Entities & Rules)        │
│  - RetinalImage                            │
│  - AiAnalysis                              │
│  - Validators                              │
└─────────────────────────────────────────────┘
```

---

## 🖼️ Luồng Upload Ảnh

### 1️⃣ **Frontend Upload**

**File:** `frontend/js/pages/upload-image.js`

```js
// Bước 1: User chọn ảnh
selectedFile = input.files[0];

// Bước 2: Upload ảnh lên server (hoặc Cloudinary trực tiếp)
// Trả về URL của ảnh đã upload
imageUrl = response.data.secure_url; // hoặc image_url

// Bước 3: Save metadata vào DB
payload = {
  patient_id: patientId,
  clinic_id: user.clinic_id,
  uploaded_by: accountId,
  image_type: 'fundus',    // fundus, oct, angiography
  eye_side: 'left',         // left, right, both
  image_url: imageUrl       // URL to the uploaded image
};
AuraAPI.uploadImage(payload);

// Bước 4: Chuyển hướng tới trang danh sách ảnh
window.location.href = 'my-images.html';
```

---

### 2️⃣ **Backend Upload - API Endpoint**

**File:** `backend/src/api/controllers/retinal_image_controller.py`

**Route:** `POST /api/retinal-images`

```python
@retinal_image_bp.route('', methods=['POST'])
@require_roles(['Patient', 'Doctor', 'Admin', 'ClinicManager'])
def upload_image():
    """
    Upload a new retinal image
    
    Request Body (JSON):
    {
        "patient_id": 1,
        "clinic_id": 1,
        "uploaded_by": 1,          // Account ID
        "image_type": "fundus",    // fundus, oct, fluorescein, angiography
        "eye_side": "left",        // left, right, both
        "image_url": "https://example.com/image.jpg",
        "status": "uploaded"       // Optional, default: 'uploaded'
    }
    """
    
    # 1. Validate request
    schema = RetinalImageCreateRequestSchema()
    data = schema.load(request.get_json())
    
    # 2. Check subscription (nếu hết lượt sẽ trả lỗi 402)
    try:
        subscription = subscription_service.check_analysis_quota(user_id)
        if not subscription or subscription.remaining_analyses <= 0:
            return error_response('Hết lượt phân tích', 402)
    except BusinessRuleException:
        return error_response('Hết lượt phân tích', 402)
    
    # 3. Call Service Layer để lưu ảnh
    image = image_service.upload_image(
        patient_id=data['patient_id'],
        clinic_id=data['clinic_id'],
        uploaded_by=data['uploaded_by'],
        image_type=data['image_type'],
        eye_side=data['eye_side'],
        image_url=data['image_url'],
        status='uploaded'
    )
    
    # 4. Return response
    response_schema = RetinalImageResponseSchema()
    return success_response(
        response_schema.dump(image),
        'Image uploaded successfully',
        201
    )
```

---

### 3️⃣ **Service Layer - Business Logic**

**File:** `backend/src/services/retinal_image_service.py`

```python
class RetinalImageService:
    def __init__(self, repository: IRetinalImageRepository):
        self.repository = repository
    
    def upload_image(self, patient_id: int, clinic_id: int, uploaded_by: int,
                    image_type: str, eye_side: str, image_url: str, 
                    status: str = 'uploaded') -> RetinalImage:
        """
        Upload retinal image với validation
        
        Bước xử lý:
        1. Validate image_type (fundus, oct, angiography, fluorescein)
        2. Validate eye_side (left, right, both)
        3. Validate image_url (không được trống)
        4. Validate status (uploaded, processing, analyzed, error)
        5. Lưu vào database
        """
        
        # 1. Validate fields
        RetinalImageValidator.validate_image_type(image_type)
        RetinalImageValidator.validate_eye_side(eye_side)
        RetinalImageValidator.validate_image_url(image_url)
        
        valid_statuses = ['uploaded', 'processing', 'analyzed', 'error']
        if status not in valid_statuses:
            raise ValidationException(f"Invalid status: {status}")
        
        # 2. Call Repository to insert into DB
        image = self.repository.add(
            patient_id=patient_id,
            clinic_id=clinic_id,
            uploaded_by=uploaded_by,
            image_type=image_type,
            eye_side=eye_side,
            image_url=image_url,
            upload_time=datetime.now(),
            status=status
        )
        
        if not image:
            raise ValueError("Failed to upload image")
        
        return image
```

---

### 4️⃣ **Repository Layer - Database**

**File:** `backend/src/infrastructure/repositories/retinal_image_repository.py`

```python
class RetinalImageRepository(IRetinalImageRepository):
    def add(self, patient_id: int, clinic_id: int, uploaded_by: int, 
            image_type: str, eye_side: str, image_url: str, 
            upload_time: datetime, status: str) -> RetinalImage:
        """
        Lưu ảnh vào database (bảng retinal_images)
        """
        try:
            # 1. Create model instance
            image_model = RetinalImageModel(
                patient_id=patient_id,
                clinic_id=clinic_id,
                uploaded_by=uploaded_by,
                image_type=image_type,
                eye_side=eye_side,
                image_url=image_url,
                upload_time=upload_time,
                status=status
            )
            
            # 2. Insert into database
            self.session.add(image_model)
            self.session.commit()
            self.session.refresh(image_model)
            
            # 3. Convert to domain model and return
            return self._to_domain(image_model)
            
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating retinal image: {str(e)}')
```

---

### 5️⃣ **Database Schema**

**Table:** `retinal_images`

```sql
CREATE TABLE retinal_images (
    image_id        BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id      BIGINT NOT NULL FOREIGN KEY,
    clinic_id       INT NOT NULL FOREIGN KEY,
    uploaded_by     BIGINT NOT NULL FOREIGN KEY (accounts.account_id),
    image_type      VARCHAR(20) NOT NULL,    -- fundus, oct, angiography, fluorescein
    eye_side        VARCHAR(20) NOT NULL,    -- left, right, both
    image_url       TEXT NOT NULL,           -- URL to the image (on Cloudinary, etc.)
    upload_time     DATETIME NOT NULL,
    status          VARCHAR(20) NOT NULL,    -- uploaded, processing, analyzed, error
    
    -- Foreign keys
    FOREIGN KEY (patient_id) REFERENCES patient_profiles(patient_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id),
    FOREIGN KEY (uploaded_by) REFERENCES accounts(account_id)
);
```

---

## 🤖 Luồng Chạy AI Models

### **Cloudinary + Kaggle AI Endpoint Flow**

**File:** `backend/src/app.py` (FastAPI)

#### **Endpoint:** `POST /retinal/analyze`

```python
@fastapi_app.post("/retinal/analyze")
async def analyze_retina_cloudinary(file: UploadFile = File(...)):
    """
    Luồng: Upload → Cloudinary → Kaggle AI Endpoint → Result
    
    NOTE: Tất cả AI models chạy trên Kaggle endpoint (remote)
    Không có local models (folder models/ đã bị xóa)
    """
    
    # 1. Upload ảnh lên Cloudinary
    upload_result = cloudinary.uploader.upload(
        file.file,
        folder="retinal_images",
        public_id=str(uuid.uuid4())
    )
    image_url = upload_result.get("secure_url")
    # Result: https://res.cloudinary.com/dmidkmbyp/image/upload/...
    
    # 2. Gọi Kaggle AI endpoint với image URL
    response = requests.post(
        KAGGLE_AI_URL,  # https://relationless-nonagglomerative-ariel.ngrok-free.dev
        json={"image_url": image_url},
        timeout=120
    )
    
    if response.status_code != 200:
        return {"error": "AI analysis failed", "details": response.text}
    
    ai_result = response.json()
    
    # 3. Trả kết quả về client (kết quả đã xử lý từ Kaggle)
    return {
        "image_url": image_url,
        "analysis": ai_result  # Kết quả từ Kaggle models
    }
```

**Config:**
```python
# Cloudinary credentials
cloudinary.config(
    cloud_name="dmidkmbyp",
    api_key="256857942333283",
    api_secret="dEV8dxWyWpCClSgv9F8ikse1abQ"
)

# Kaggle AI Core endpoint (xử lý tất cả models)
KAGGLE_AI_URL = "https://relationless-nonagglomerative-ariel.ngrok-free.dev"
```

---

### **AI Models Chạy Trên Kaggle**

Tất cả models AI được chạy trên **Kaggle endpoint remote** (ngrok tunnel):

#### **Models Include:**
- **Vessel Segmentation (U-Net):** Phân đoạn mạch máu từ ảnh võng mạc
- **DR Classification (EfficientNetB1):** Phân loại giai đoạn Diabetic Retinopathy
- **Feature Extraction:** Tính toán các chỉ số như vessel ratio, tortuosity, lesion count

#### **Kaggle Response Format:**
Kaggle endpoint sẽ trả về kết quả có dạng:
```json
{
  "vessel_mask_url": "https://...",
  "vessel_density": 0.35,
  "tortuosity": 0.42,
  "lesion_count": 2,
  "risk_level": "Medium",
  "dr_stage": 2,
  "confidence": 0.89,
  "disease_type": "Mild/Moderate Diabetic Retinopathy"
}
```

---

### **Backend AI Analysis Flow**

**File:** `backend/src/services/ai_analysis_service.py`

```python
class AiAnalysisService:
    def create_analysis(self, image_id: int, ai_model_version_id: int, 
                       status: str = 'pending') -> Optional[AiAnalysis]:
        """
        Tạo AI analysis request
        
        Trạng thái: pending → processing → completed/failed
        """
        return self.repository.add(
            image_id=image_id,
            ai_model_version_id=ai_model_version_id,
            analysis_time=datetime.now(),
            status=status,
            processing_time=None
        )
    
    def get_analysis_by_image(self, image_id: int) -> Optional[AiAnalysis]:
        """Lấy kết quả phân tích theo ảnh (1:1)"""
        return self.repository.get_by_image_id(image_id)
```

**Table:** `ai_analyses`

```sql
CREATE TABLE ai_analyses (
    analysis_id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    image_id              BIGINT NOT NULL UNIQUE,      -- 1:1 with retinal_images
    ai_model_version_id   INT NOT NULL,                -- AI model version used
    analysis_time         DATETIME NOT NULL,
    status                VARCHAR(20) NOT NULL,        -- pending, processing, completed, failed
    processing_time       INT,                         -- Milliseconds
    
    FOREIGN KEY (image_id) REFERENCES retinal_images(image_id),
    FOREIGN KEY (ai_model_version_id) REFERENCES ai_model_versions(model_version_id)
);
```

---

## 🔌 Các API Endpoint

### **Retinal Image Upload**

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/retinal-images` | Upload 1 ảnh | Có |
| POST | `/api/retinal-images/bulk` | Upload nhiều ảnh | Có |
| GET | `/api/retinal-images/<id>` | Lấy thông tin ảnh | Có |
| GET | `/api/retinal-images/patient/<patient_id>` | Lấy ảnh của bệnh nhân | Có |
| GET | `/api/retinal-images/pending-analysis` | Lấy ảnh chưa phân tích | Có |
| PUT | `/api/retinal-images/<id>` | Update ảnh | Có |
| PUT | `/api/retinal-images/<id>/analyzed` | Mark as analyzed | Không |
| DELETE | `/api/retinal-images/<id>` | Xóa ảnh | Có |

### **AI Analysis**

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/ai-analysis` | Tạo analysis request | Có |
| GET | `/api/ai-analysis/<id>` | Lấy kết quả phân tích | Có |
| GET | `/api/ai-analysis/image/<image_id>` | Lấy analysis theo ảnh | Có |
| GET | `/api/ai-analysis/patient/<patient_id>` | Lịch sử phân tích bệnh nhân | Có |

### **FastAPI Demo**

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | API info | Không |
| POST | `/retinal/analyze` | Cloudinary + Kaggle AI (recommended) | Không |
| GET | `/docs` | Swagger UI | Không |

---

## 📊 Trạng Thái Ảnh (Status)

```
┌─────────────┐
│  uploaded   │  ← Vừa upload, chưa phân tích
└──────┬──────┘
       │ (Doctor triggers analysis)
       ▼
┌──────────────┐
│  processing  │  ← Đang chạy AI models
└──────┬───────┘
       │ (AI analysis completes)
       ▼
┌──────────────┐
│   analyzed   │  ← Hoàn thành phân tích, có kết quả
└──────────────┘

       ↓ (Nếu có lỗi)
       ▼
┌──────────────┐
│    error     │  ← Lỗi trong quá trình xử lý
└──────────────┘
```

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER UPLOADS IMAGE                          │
│                   (Frontend: upload-image.js)                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  POST /api/retinal-images                                       │
│  {                                                              │
│    "patient_id": 1,                                            │
│    "clinic_id": 1,                                             │
│    "uploaded_by": 1,                                           │
│    "image_type": "fundus",                                     │
│    "eye_side": "left",                                         │
│    "image_url": "https://..." (pre-uploaded to Cloudinary)     │
│  }                                                              │
│                                                                 │
│  Backend: retinal_image_controller.py → upload_image()        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│           Service Layer Validation & Save                       │
│           RetinalImageService.upload_image()                    │
│                                                                 │
│  1. Validate image_type, eye_side, image_url                  │
│  2. Call repository.add()                                      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│        Database Insert: retinal_images table                    │
│                                                                 │
│  INSERT INTO retinal_images                                    │
│  (patient_id, clinic_id, uploaded_by,                          │
│   image_type, eye_side, image_url, upload_time, status)        │
│  VALUES (1, 1, 1, 'fundus', 'left', 'https://...', NOW(),     │
│          'uploaded')                                           │
│                                                                 │
│  status: 'uploaded' ← Ready for AI analysis                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│               Response to Frontend                              │
│                                                                 │
│  {                                                              │
│    "image_id": 1,                                              │
│    "status": "uploaded",                                       │
│    "image_url": "https://..."                                  │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │   Doctor Views Image            │
        │   Triggers: POST /api/ai-analysis│
        └────────────────┬────────────────┘
                         │
                    ┌────▼──────────┐
                    │  CLOUDINARY    │
                    │   + KAGGLE     │
                    │   AI ENDPOINT  │
                    └────┬───────────┘
                         │
                    ┌────▼────────────┐
                    │ Upload to Cloud │
                    │ Call Kaggle AI  │
                    │ Endpoint        │
                    │                 │
                    │ ↓ Kaggle Models:│
                    │ - U-Net         │
                    │   (Vessel)      │
                    │ - EfficientNetB1│
                    │   (DR Class)    │
                    │ - Features      │
                    │                 │
                    │ Result:         │
                    │ - vessel_density│
                    │ - dr_stage      │
                    │ - risk_level    │
                    │ - confidence    │
                    └────┬────────────┘
             │
        ┌────▼──────────────────────────────┐
        │  Save to ai_analyses table         │
        │  Update retinal_images status      │
        │  → status: 'analyzed'              │
        │  → ai_result_id                    │
        └────┬───────────────────────────────┘
             │
        ┌────▼──────────────────────────────┐
        │   Generate AI Result Report        │
        │   Store in ai_results table        │
        │   Create Notification              │
        │   Send to Doctor/Patient           │
        └────────────────────────────────────┘
```

---

## 📈 Subscription & Quota System

**File:** `backend/src/services/subscription_service.py`

```python
# Before creating analysis, check quota:
subscription = subscription_service.check_analysis_quota(user_id)

if not subscription or subscription.remaining_analyses <= 0:
    return error_response('Hết lượt phân tích. Vui lòng mua thêm gói.', 402)
```

**Table:** `subscriptions`

```sql
CREATE TABLE subscriptions (
    subscription_id   INT PRIMARY KEY,
    account_id        BIGINT NOT NULL UNIQUE,
    package_id        INT NOT NULL,
    total_analyses    INT,       -- Tổng lượt phân tích trong gói
    remaining_analyses INT,      -- Lượt phân tích còn lại
    start_date        DATE,
    end_date          DATE,
    status            VARCHAR(20),  -- active, inactive, expired
    
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (package_id) REFERENCES packages(package_id)
);
```

---

## 🔒 Security & Permissions

| Endpoint | Role Required | Notes |
|----------|---------------|-------|
| Upload Image | Patient, Doctor, ClinicManager, Admin | Kiểm tra JWT |
| Create Analysis | Doctor, Admin | Kiểm tra subscription quota |
| View Results | Doctor, Admin, Patient (own) | Row-level security |

---

## 📝 Summary

1. **Frontend** → Upload ảnh (có sẵn URL từ Cloudinary)
2. **Backend** → Lưu metadata vào DB (retinal_images table)
3. **Image Status** → 'uploaded' (chưa phân tích)
4. **Doctor** → Trigger analysis request
5. **AI Models** → Xử lý ảnh (Vessel Segmentation + DR Classification)
6. **Results** → Lưu vào ai_analyses & ai_results tables
7. **Notification** → Gửi kết quả tới Doctor/Patient

---

**Tác giả:** AURA Development Team  
**Cập nhật:** 2026-02-04  
**Version:** 1.0.0
