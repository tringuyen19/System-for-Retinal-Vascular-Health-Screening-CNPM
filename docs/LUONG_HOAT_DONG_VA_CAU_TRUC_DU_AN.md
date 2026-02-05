# Tài liệu Luồng Hoạt Động và Cấu Trúc Dự Án AURA

**AURA - AI-Powered Retinal Disease Detection System**  
Hệ thống sàng lọc sức khỏe mạch máu võng mạc, phân tích ảnh đáy mắt bằng AI.

Tài liệu này mô tả **luồng hoạt động** khi chạy hệ thống (request đi qua các tầng nào), **cấu trúc file/thư mục** chi tiết, và gợi ý **câu hỏi vấn đáp** để thầy/cô và sinh viên có thể trao đổi.

---

## Mục lục

1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [Luồng hoạt động khi chạy (request đi qua các tầng)](#2-luồng-hoạt-động-khi-chạy-request-đi-qua-các-tầng)
3. [Cấu trúc thư mục và file chi tiết](#3-cấu-trúc-thư-mục-và-file-chi-tiết)
4. [Ví dụ luồng cụ thể](#4-ví-dụ-luồng-cụ-thể)
5. [Gợi ý câu hỏi vấn đáp](#5-gợi-ý-câu-hỏi-vấn-đáp)

---

## 1. Tổng quan kiến trúc

Hệ thống dùng **kiến trúc phân tầng (Layered Architecture)** kết hợp **Clean Architecture** ở backend:

- **Frontend**: Giao diện web tĩnh (HTML, CSS, JavaScript), gọi API REST qua `fetch`.
- **Backend**: Flask (Python), tổ chức theo các tầng:
  - **API / Presentation**: Routes, Controllers, Schemas, Middleware (CORS, JWT, RBAC).
  - **Application / Business**: Services (nghiệp vụ).
  - **Domain**: Domain models, interfaces (repository interfaces).
  - **Infrastructure**: Repositories, DB models (SQLAlchemy), kết nối cơ sở dữ liệu.

Khi **một request** từ trình duyệt tới backend, nó lần lượt đi qua: **CORS → Route → Middleware (JWT/RBAC) → Controller → Schema (validation) → Service → Repository → Database**, rồi response đi ngược lại.

---

## 2. Luồng hoạt động khi chạy (request đi qua các tầng)

### 2.1. Khởi động ứng dụng (khi chạy `python app.py`)

Thứ tự khởi tạo trong `app.py`:

| Bước | Thành phần | File / Hàm | Mô tả ngắn |
|------|------------|------------|------------|
| 1 | Flask app | `app.py` → `create_app()` | Tạo ứng dụng Flask, load `Config` từ `config.py`. |
| 2 | CORS | `cors.py` → `init_cors(app)` | Cho phép frontend (origin khác, ví dụ `localhost:8080`) gọi API, cho phép header `Authorization`. |
| 3 | JWT | `JWTManager(app)` | Cấu hình JWT (secret, thời hạn token) cho đăng nhập/xác thực. |
| 4 | Swagger | `Swagger(app, ...)` | Cấu hình tài liệu API tại `/docs`. |
| 5 | Database | `init_db(app)` | Import models, kết nối DB (MSSQL), tạo bảng (`create_all`), chạy migrations (nếu có). |
| 6 | Routes | `register_routes(app)` | Đăng ký tất cả Blueprint (auth, roles, accounts, patients, doctors, clinics, retinal-images, ai-analysis, ...). |
| 7 | Chạy server | `app.run(host='0.0.0.0', port=9999)` | Lắng nghe cổng 9999. |

**Kết luận khi chạy:** Request từ bên ngoài chỉ tới được **sau** khi CORS, JWT, DB và Routes đã được khởi tạo.

---

### 2.2. Luồng một HTTP request (ví dụ: đăng nhập, hoặc lấy danh sách bệnh nhân)

Một request từ **Frontend** (trình duyệt) tới **Backend** (Flask) đi qua các tầng theo thứ tự sau:

```
[Trình duyệt] 
    → (1) Gửi HTTP request (GET/POST/PUT/DELETE) tới http://localhost:9999/api/...
    
[Backend - Flask]
    → (2) CORS: kiểm tra origin, headers (cho phép Content-Type, Authorization)
    → (3) Routing: Flask khớp URL với Blueprint + route (vd: /api/auth/login → auth_controller.register hoặc login)
    → (4) Middleware (nếu route yêu cầu):
           - JWT: verify token trong header Authorization (trừ route login/register)
           - RBAC: kiểm tra role (Patient, Doctor, ClinicManager, Admin) nếu dùng @require_role / @require_roles
    → (5) Controller (trong api/controllers/):
           - Đọc body/query (request.get_json(), request.args)
           - Validate dữ liệu bằng Schema (Marshmallow) → load() hoặc validate()
           - Gọi Service tương ứng (vd: AccountService, AiAnalysisService)
           - Bắt exception (ValidationError, NotFoundException, ...) → trả error_response / validation_error_response
           - Serialize kết quả bằng Response Schema → success_response(data)
    → (6) Service (trong services/):
           - Nghiệp vụ: kiểm tra điều kiện, tạo/cập nhật/xóa theo logic nghiệp vụ
           - Gọi Repository để đọc/ghi dữ liệu
           - Trả về domain object hoặc dữ liệu cho controller
    → (7) Repository (trong infrastructure/repositories/):
           - Chuyển domain object ↔ DB model (SQLAlchemy)
           - Thực hiện session.add(), session.query(), commit(), rollback()
    → (8) Database (MSSQL):
           - Thực thi SQL (INSERT, SELECT, UPDATE, DELETE) qua SQLAlchemy engine
    
    → (9) Response: Controller trả jsonify({ "message": "...", "data": ... }) với status code (200, 201, 400, 401, 404, 422, 500)
    
[Trình duyệt]
    → (10) Frontend nhận response, cập nhật UI (vd: lưu token, chuyển trang, hiển thị danh sách)
```

**Tóm tắt các tầng request đi qua:**

1. **CORS** (infrastructure – mạng/security)  
2. **Routing** (Flask – API layer)  
3. **Middleware (JWT + RBAC)** (API layer)  
4. **Controller** (API layer)  
5. **Schema validation** (API layer – Marshmallow)  
6. **Service** (Application/Business layer)  
7. **Repository** (Infrastructure layer)  
8. **Database** (Infrastructure – MSSQL)  

Response đi ngược: **Database → Repository → Service → Controller → JSON response → Frontend**.

---

### 2.3. Sơ đồ luồng (theo tầng)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND (Trình duyệt)                                                  │
│  - HTML trang (login.html, patient/dashboard.html, ...)                 │
│  - JS: config.js (API_BASE_URL), api.js (fetch), auth.js (token),       │
│        pages/login.js, pages/patient-dashboard.js, ...                   │
│  - Gửi: GET/POST/PUT/DELETE + headers (Authorization: Bearer <token>)  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  BACKEND - API / PRESENTATION LAYER                                      │
│  - CORS (cors.py)                                                        │
│  - Routes (api/routes.py → Blueprints)                                   │
│  - Middleware: JWT (Flask-JWT-Extended), RBAC (auth_middleware.py)       │
│  - Controllers (api/controllers/*.py): nhận request, validate, gọi      │
│    Service, trả response                                                  │
│  - Schemas (api/schemas/*.py): Marshmallow validate/serialize            │
│  - responses.py: success_response, error_response, not_found_response    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  APPLICATION / BUSINESS LAYER (services/)                                │
│  - account_service, ai_analysis_service, patient_profile_service, ...    │
│  - Nghiệp vụ: tạo user, tạo phân tích AI, kiểm tra quyền, ...           │
│  - Gọi Repository, không gọi trực tiếp DB model                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DOMAIN LAYER (domain/)                                                  │
│  - domain/models/*.py: AiAnalysis, Account, PatientProfile, ... (pure   │
│    Python, không phụ thuộc DB)                                            │
│  - domain/models/i*_repository.py: interface (abstract) cho Repository │
│  - domain/exceptions.py: NotFoundException, ValidationException, ...     │
│  - domain/constants.py                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE LAYER                                                    │
│  - Repositories (infrastructure/repositories/*.py):                      │
│    implement interface, dùng Session, map Domain ↔ Model                │
│  - Models (infrastructure/models/*.py): SQLAlchemy (Base, Column, FK)   │
│  - databases/base.py, mssql.py: engine, session, init_db, create_all    │
│  - Database: MSSQL (RetinalHealthDB)                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Cấu trúc thư mục và file chi tiết

### 3.1. Thư mục gốc dự án

| Thư mục/File | Mô tả |
|--------------|--------|
| `backend/` | Mã nguồn backend Flask (API, nghiệp vụ, DB). |
| `frontend/` | Giao diện web (HTML, CSS, JS). |
| `docs/` | Tài liệu (README, kiến trúc, **luồng hoạt động**). |
| `.gitignore` | Các file/thư mục không đưa lên Git. |
| `default.db` | File SQLite (nếu dùng SQLite thay MSSQL, thường không commit). |

---

### 3.2. Backend (`backend/`)

#### 3.2.1. Cấu trúc tổng quan

```
backend/
├── requirements.txt          # Thư viện Python (Flask, SQLAlchemy, PyMSSQL, JWT, Marshmallow, ...)
└── src/
    ├── app.py                # Entry point: create_app(), chạy server port 9999
    ├── config.py             # Config: SECRET_KEY, JWT, DATABASE_URI, CORS, Swagger
    ├── cors.py               # init_cors(app): CORS cho frontend
    ├── create_app.py         # Factory tạo app (nếu tách riêng)
    ├── dependency_container.py  # Dependency injection (nếu dùng)
    ├── error_handler.py      # Xử lý lỗi toàn cục
    ├── app_logging.py        # Cấu hình logging
    ├── api/                  # Tầng API / Presentation
    ├── domain/               # Tầng Domain
    ├── services/             # Tầng Application / Business
    └── infrastructure/       # Tầng Infrastructure
```

#### 3.2.2. `backend/src/api/` – API / Presentation

| Thành phần | Đường dẫn / File | Vai trò |
|------------|-------------------|--------|
| **Routes** | `api/routes.py` | Đăng ký tất cả Blueprint: auth, role, account, patient, doctor, clinic, retinal_image, ai_analysis, ai_annotation, ai_model_version, ai_result, medical_report, doctor_review, notification, conversation, message, service_package, subscription, payment, admin, audit_log, notification_template, upload. |
| **Controllers** | `api/controllers/*.py` | Mỗi file = một Blueprint (vd: `auth_controller.py` → `auth_bp`, `ai_analysis_controller.py` → `ai_analysis_bp`). Định nghĩa route (GET/POST/PUT/DELETE), gọi Schema load/validate, gọi Service, trả success/error. |
| **Middleware** | `api/middleware/auth_middleware.py` | `@jwt_required`, `@require_role('Admin')`, `@require_roles(['Doctor','Admin'])`, `get_current_user()`, `get_current_user_role_id()`. Kiểm tra JWT và quyền trước khi vào controller. |
| **Schemas** | `api/schemas/*.py` | Marshmallow: Request (Create/Update), Response. Validate input, serialize output. |
| **Responses** | `api/responses.py` | `success_response(data, message, status_code)`, `error_response(message, status_code)`, `not_found_response(message)`, `validation_error_response(errors)`. |
| **Requests** | `api/requests.py` | Các helper đọc request (nếu có). |
| **Swagger** | `api/swagger.py` / `config.SwaggerConfig` | Cấu hình Swagger/Flasgger cho `/docs`. |

**Ví dụ controller:** `api/controllers/ai_analysis_controller.py`  
- Route `POST /api/ai-analysis` → `@require_roles(['Doctor','Admin'])` → `AiAnalysisCreateRequestSchema().load(request.get_json())` → `analysis_service.create_analysis(...)` → `AiAnalysisResponseSchema().dump(analysis)` → `success_response(...)`.

#### 3.2.3. `backend/src/domain/` – Domain

| Thành phần | Đường dẫn | Vai trò |
|------------|-----------|--------|
| **Domain models** | `domain/models/*.py` (trừ `i*.py`) | Class thuần Python: `AiAnalysis`, `Account`, `PatientProfile`, `Clinic`, ... Không import SQLAlchemy. Chứa thuộc tính nghiệp vụ. |
| **Repository interfaces** | `domain/models/i*_repository.py` | Interface (abstract) cho Repository: vd `IAiAnalysisRepository` với `add()`, `get_by_id()`, ... Service phụ thuộc interface, không phụ thuộc implementation. |
| **Exceptions** | `domain/exceptions.py` | `NotFoundException`, `ValidationException`, `ConflictException`, ... Được raise từ Service, bắt ở Controller. |
| **Constants** | `domain/constants.py` | Hằng số dùng chung. |
| **Validators** | `domain/validators.py` | Hàm validate nghiệp vụ (nếu có). |

#### 3.2.4. `backend/src/services/` – Application / Business

| File (ví dụ) | Vai trò |
|--------------|--------|
| `account_service.py` | Đăng ký, đăng nhập, cập nhật tài khoản; gọi AccountRepository, RoleRepository. |
| `ai_analysis_service.py` | Tạo/cập nhật/xóa phân tích AI, tạo mock result; gọi AiAnalysisRepository, có thể gọi AiResultService. |
| `patient_profile_service.py` | CRUD hồ sơ bệnh nhân, liên kết account. |
| `retinal_image_service.py` | Upload, lấy ảnh theo patient, thống kê. |
| `medical_report_service.py` | Tạo/sửa báo cáo y tế. |
| Các service khác | Tương ứng từng nghiệp vụ (clinic, doctor, notification, subscription, payment, ...). |

Service **không** import Controller hay Flask request; nhận dữ liệu từ Controller và trả domain object hoặc dict/list.

#### 3.2.5. `backend/src/infrastructure/` – Infrastructure

| Thành phần | Đường dẫn | Vai trò |
|------------|-----------|--------|
| **Database** | `infrastructure/databases/base.py` | SQLAlchemy `Base` (declarative_base). |
| | `infrastructure/databases/mssql.py` | `create_engine(DATABASE_URI)`, `sessionmaker`, `scoped_session`, `init_mssql(app)`: create_all, migrations (FR-16, FR-19, FR-22, FR-34). |
| | `infrastructure/databases/__init__.py` | Import Base và tất cả models để đăng ký với Base; gọi `init_mssql(app)` trong `init_db(app)`. |
| **Models** | `infrastructure/models/*.py` | SQLAlchemy model: `RoleModel`, `AccountModel`, `ClinicModel`, `PatientProfileModel`, `DoctorProfileModel`, `RetinalImageModel`, `AiAnalysisModel`, `AiResultModel`, `MedicalReportModel`, ... Ánh xạ bảng trong MSSQL. |
| **Repositories** | `infrastructure/repositories/*.py` | Class implement interface domain (vd `AiAnalysisRepository(IAiAnalysisRepository)`). Dùng `session.query(Model)`, `session.add()`, `commit()`, `_to_domain(model)`. |
| **Infrastructure services** | `infrastructure/services/` | Dịch vụ bên thứ ba (email, storage, ...) nếu có. |

---

### 3.3. Frontend (`frontend/`)

| Thư mục/File | Vai trò |
|--------------|--------|
| `index.html` | Trang chủ. |
| `login.html`, `register.html` | Đăng nhập, đăng ký. |
| `forgot-password.html`, `reset-password.html` | Quên mật khẩu, đặt lại mật khẩu. |
| `clinic-register.html` | Đăng ký phòng khám. |
| `css/style.css` | Style chung. |
| `js/config.js` | `AURA_CONFIG`: `API_BASE_URL` (localhost:9999), `STORAGE_KEYS`, `ROLES`. |
| `js/api.js` | Gọi API: `getHeaders()` (Authorization Bearer), `request()`, `login()`, `register()`, `getPatientByAccount()`, `getImagesByPatient()`, `uploadFile()`, ... (object `window.AuraAPI`). |
| `js/auth.js` | `setAuthFromResponse()`, lưu token/user/role vào localStorage; kiểm tra đăng nhập; redirect theo role. |
| `js/utils.js` | Hàm tiện ích (showToast, format ngày, ...). |
| `js/components/*.js` | alert, header, modal, sidebar, spinner, table. |
| `js/pages/*.js` | Logic từng trang: login.js, register.js, patient-dashboard.js, upload-image.js, doctor-patients.js, admin-accounts.js, ... |
| `components/*.html` | header, footer, sidebar (include vào các trang). |
| `admin/*.html` | Trang quản trị: dashboard, accounts, clinics, ai-models, billing, settings, statistics. |
| `clinic/*.html` | Trang phòng khám: dashboard, patients, reports, images, settings, ... |
| `doctor/*.html` | Trang bác sĩ: dashboard, patients, analysis-results, create-report, ... |
| `patient/*.html` | Trang bệnh nhân: dashboard, upload-image, my-images, analysis-results, profile, ... |

**Luồng frontend điển hình:**  
Trang (vd `login.html`) load `config.js`, `api.js`, `auth.js`, `pages/login.js`. User nhập form → `login.js` gọi `AuraAPI.login({ email, password })` → `api.js` gửi `POST http://localhost:9999/api/auth/login` → nhận response → `AuraAuth.setAuthFromResponse(res)` lưu token, redirect theo role (patient/doctor/admin/clinic).

---

## 4. Ví dụ luồng cụ thể

### 4.1. Luồng đăng nhập (Login)

1. **Frontend:** User nhập email/mật khẩu trên `login.html` → `login.js` gọi `AuraAPI.login({ email, password })`.
2. **api.js:** `request('POST', '/api/auth/login', credentials, false)` → không gửi token; `fetch(API_BASE + '/api/auth/login', { method: 'POST', body: JSON.stringify(credentials), headers: { 'Content-Type': 'application/json' } })`.
3. **Backend:**  
   - CORS cho phép request.  
   - Route: `POST /api/auth/login` → `auth_controller.py` (hàm `login()`).  
   - Không qua `@jwt_required` (vì chưa có token).  
   - Controller: `RegisterRequestSchema` hoặc schema login → load body → gọi `account_service` (kiểm tra email/password, lấy role, clinic nếu có).  
   - Service: dùng `AccountRepository`, `RoleRepository` để lấy account và role.  
   - Controller: tạo JWT bằng `create_access_token(identity=account_id, additional_claims={ 'role_id': ... })`, trả `success_response({ access_token, user, role_id, ... })`.
4. **Frontend:** Nhận JSON → `AuraAuth.setAuthFromResponse(res)` lưu token và user vào localStorage → redirect theo role (patient → patient/dashboard.html, doctor → doctor/dashboard.html, ...).

### 4.2. Luồng tạo AI Analysis (có JWT + RBAC)

1. **Frontend:** Trang doctor gửi `POST /api/ai-analysis` với body `{ image_id, ai_model_version_id }` và header `Authorization: Bearer <token>`.
2. **Backend:**  
   - CORS cho phép.  
   - Route: `POST /api/ai-analysis` → `ai_analysis_controller.create_analysis()`.  
   - Middleware: `@require_roles(['Doctor','Admin'])` → verify JWT, lấy `role_id` từ token → so sánh với role Doctor/Admin → cho qua hoặc 403.  
   - Controller: `AiAnalysisCreateRequestSchema().load(request.get_json())` → validate; gọi `image_service.get_image_by_id(image_id)`; gọi `analysis_service.create_analysis(...)`.  
   - Service: validate status, gọi `analysis_repo.add(...)`; có thể gọi thêm `_auto_create_result()` (tạo AI result mock).  
   - Repository: tạo `AiAnalysisModel`, `session.add()`, `commit()`, `_to_domain()` trả `AiAnalysis`.  
   - Controller: `AiAnalysisResponseSchema().dump(analysis)` → `success_response(..., 201)`.  
3. **Frontend:** Nhận 201 và data → cập nhật UI (vd thông báo tạo phân tích thành công).

---

## 5. Gợi ý câu hỏi vấn đáp

Dưới đây là các câu hỏi thường gặp theo từng chủ đề để thầy/cô vấn đáp và sinh viên chuẩn bị.

### Kiến trúc và luồng tổng thể

1. **Khi chạy `python app.py`, hệ thống khởi tạo những gì, theo thứ tự nào?**  
   → CORS → JWT → Swagger → Database (init_db, create_all, migrations) → register_routes (Blueprint) → app.run(9999).

2. **Một request từ trình duyệt tới API (vd POST /api/ai-analysis) đi qua những tầng nào?**  
   → CORS → Routing → Middleware (JWT, RBAC) → Controller → Schema validation → Service → Repository → Database; response đi ngược lại.

3. **Backend được tổ chức theo kiến trúc gì?**  
   → Layered / Clean Architecture: API (Controllers, Schemas, Middleware) → Application (Services) → Domain (models, interfaces, exceptions) → Infrastructure (Repositories, DB models, databases).

4. **Vì sao tách Domain model và Infrastructure model (SQLAlchemy)?**  
   → Domain độc lập với DB, dễ test và thay đổi persistence; Infrastructure model chỉ là ánh xạ bảng, Repository chuyển đổi giữa hai bên.

### API và Controller

5. **Controller làm những việc gì?**  
   → Nhận request (body, query, params), validate bằng Schema (Marshmallow), gọi Service, bắt exception, serialize response bằng Schema và trả JSON (success_response/error_response).

6. **Schema (Marshmallow) dùng để làm gì?**  
   → Validate dữ liệu đầu vào (load/validate) và serialize dữ liệu đầu ra (dump) cho API; đảm bảo format và kiểu dữ liệu thống nhất.

7. **Middleware JWT và RBAC hoạt động thế nào?**  
   → JWT: verify token trong header `Authorization: Bearer <token>`, lấy identity (account_id) và claims (role_id). RBAC: decorator `@require_role('Admin')` hoặc `@require_roles(['Doctor','Admin'])` kiểm tra role_id trong token với role được phép; nếu không đủ quyền trả 403.

8. **CORS trong dự án cấu hình thế nào?**  
   → Trong `cors.py`, dùng Flask-CORS: cho phép mọi origin (`*`), allow_headers `Content-Type`, `Authorization`, expose_headers `Content-Type`, `Content-Disposition` để frontend (cổng khác) gọi API và gửi JWT.

### Service và Domain

9. **Service layer đảm nhiệm gì?**  
   → Nghiệp vụ: kiểm tra điều kiện, quy tắc nghiệp vụ, gọi Repository để đọc/ghi; không xử lý HTTP request/response trực tiếp.

10. **Repository làm gì?**  
    → Implement interface trong domain; nhận/trả domain object; bên trong dùng SQLAlchemy Session và Model (infrastructure); thực hiện add, query, commit, rollback; map Model ↔ Domain (_to_domain, _to_model nếu cần).

11. **Domain model khác gì so với DB model (infrastructure)?**  
    → Domain: class Python thuần, không phụ thuộc SQLAlchemy, dùng trong Service. DB model: class kế thừa Base, Column, ForeignKey, ánh xạ trực tiếp bảng trong DB.

### Frontend

12. **Frontend gọi API như thế nào?**  
    → Dùng `fetch(API_BASE_URL + path, { method, headers: getHeaders(includeAuth), body })` trong `api.js`; token lấy từ localStorage (key trong config), gửi header `Authorization: Bearer <token>` khi cần.

13. **Sau khi đăng nhập thành công, frontend làm gì?**  
    → Nhận response chứa access_token, user, role_id; lưu vào localStorage (AuraAuth.setAuthFromResponse); redirect theo role (patient/doctor/admin/clinic) tới dashboard tương ứng.

14. **API_BASE_URL được cấu hình ở đâu?**  
    → Trong `frontend/js/config.js`, biến `AURA_CONFIG.API_BASE_URL`; khi chạy local thường là `http://localhost:9999`.

### Database

15. **Database đang dùng là gì?**  
    → Cấu hình trong `config.py`: MSSQL (PyMSSQL), DATABASE_URI dạng `mssql+pymssql://user:pass@host:port/RetinalHealthDB`.

16. **Bảng trong DB được tạo như thế nào?**  
    → Trong `init_db(app)` gọi `init_mssql(app)`; `Base.metadata.create_all(bind=engine)` tạo tất cả bảng từ các model đã import trong `infrastructure/databases/__init__.py`; sau đó chạy các hàm migration (FR-16, FR-19, FR-22, FR-34) trong `mssql.py`.

### Tính năng cụ thể (AI, ảnh, báo cáo)

17. **Luồng tạo một “AI Analysis” từ đầu đến cuối?**  
    → Frontend POST /api/ai-analysis (image_id, ai_model_version_id) + JWT → Controller validate → Service create_analysis → Repository add AiAnalysisModel → (tuỳ cấu hình) Service tạo thêm AI result (mock) → Response trả về thông tin analysis.

18. **Ảnh võng mạc được lưu ở đâu?**  
    → Backend: file upload lưu tại `STATIC_UPLOAD_DIR` (config), URL trả về cho frontend; metadata ảnh (đường dẫn, patient_id, eye_side, ...) lưu trong bảng retinal_images qua RetinalImageRepository.

19. **Các role trong hệ thống và quyền truy cập API?**  
    → Patient, Doctor, ClinicManager, Admin; mỗi endpoint có thể bảo vệ bằng `@require_role` hoặc `@require_roles` (vd chỉ Doctor/Admin mới tạo AI analysis).

---

Bạn có thể in hoặc mở file này khi ôn tập hoặc khi thầy/cô vấn đáp để trả lời chính xác luồng hoạt động và cấu trúc file của dự án.
