# AURA - System for Retinal Vascular Health Screening

Hệ thống sàng lọc sức khỏe mạch máu võng mạc, hỗ trợ phân tích ảnh đáy mắt bằng AI.

---

## Cấu trúc dự án

```
System for Retinal Vascular Health Screening/
├── backend/                          # Backend Flask API
│   ├── requirements.txt              # Thư viện Python
│   └── src/
│       ├── app.py                    # Entry point, tạo Flask app
│       ├── config.py                 # Cấu hình (DB, JWT, CORS, Swagger)
│       ├── create_app.py             # Factory tạo ứng dụng
│       ├── cors.py                   # CORS cho frontend
│       ├── dependency_container.py   # Dependency injection
│       ├── error_handler.py          # Xử lý lỗi toàn cục
│       ├── app_logging.py            # Logging
│       ├── api/
│       │   ├── routes.py             # Đăng ký tất cả route
│       │   ├── middleware.py         # Middleware chung
│       │   ├── requests.py / responses.py
│       │   ├── swagger.py            # Cấu hình Swagger
│       │   ├── controllers/          # API controllers (auth, patient, doctor, clinic, ...)
│       │   ├── schemas/              # Marshmallow schemas
│       │   └── middleware/           # Auth middleware
│       ├── domain/                   # Domain models, constants, exceptions
│       ├── services/                 # Business logic (account, clinic, ai_analysis, ...)
│       ├── infrastructure/
│       │   ├── databases/            # Khởi tạo DB, kết nối
│       │   ├── models/               # SQLAlchemy models
│       │   ├── repositories/         # Truy cập dữ liệu
│       │   └── services/             # Dịch vụ bên thứ ba (email, ...)
│       ├── static/uploads/           # File tải lên (ảnh, heatmap)
│       └── migrations                # DB migrations (nếu dùng)
│
├── frontend/                         # Giao diện web (HTML, CSS, JS)
│   ├── index.html                    # Trang chủ
│   ├── login.html, register.html     # Đăng nhập, đăng ký
│   ├── forgot-password.html, reset-password.html
│   ├── clinic-register.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── config.js                 # API_BASE_URL (localhost:9999), roles, storage
│   │   ├── api.js                    # Gọi API backend
│   │   ├── auth.js                   # Xác thực, token
│   │   ├── utils.js
│   │   ├── components/               # alert, header, modal, sidebar, spinner, table
│   │   └── pages/                    # Logic từng trang (login, patient-dashboard, ...)
│   ├── components/                   # header, footer, sidebar (HTML)
│   ├── assets/                       # fonts, images, uploads
│   ├── admin/                        # Trang quản trị (dashboard, accounts, clinics, ...)
│   ├── clinic/                       # Trang phòng khám (dashboard, patients, reports, ...)
│   ├── doctor/                       # Trang bác sĩ (dashboard, patients, reports, ...)
│   └── patient/                      # Trang bệnh nhân (dashboard, upload ảnh, kết quả, ...)
│
├── docs/
│   ├── README.md                     
│   └── 
│
├── .gitignore
└── default.db                       
```


---

## Hướng dẫn chạy dự án

### 1. Clone mã nguồn (nếu chưa có)

```bash
git clone https://github.com/tringuyen19/System-for-Retinal-Vascular-Health-Screening-CNPM.git
cd System-for-Retinal-Vascular-Health-Screening-CNPM
```

### 2. Kiểm tra Python

```bash
python --version
# hoặc
py -m python --version
```

### 3. Chạy Backend (API Flask)

**Bước 3.1:** Vào thư mục backend và tạo môi trường ảo

```bash
cd backend
```

- **Windows (PowerShell/CMD):**
  ```bash
  py -m venv .venv
  ```
- **macOS/Linux:**
  ```bash
  python3 -m venv .venv
  ```

**Bước 3.2:** Kích hoạt môi trường ảo

- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\activate.ps1
  ```
  Nếu bị lỗi execution policy, chạy PowerShell **as Administrator** rồi:
  ```powershell
  Set-ExecutionPolicy RemoteSigned -Force
  ```
- **Windows (CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```

**Bước 3.3:** Cài đặt thư viện

```bash
pip install -r requirements.txt
```

**Bước 3.4:** Tạo file `.env` trong thư mục `backend/src/`

Tạo file `backend/src/.env` với nội dung ví dụ:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=jwt-secret-key-change-in-production

# SQL Server (MSSQL)
DB_USER=sa
DB_PASSWORD=123
DB_HOST=127.0.0.1
DB_PORT=1433
DB_NAME=RetinalHealthDB
DATABASE_URI=mssql+pymssql://sa:123@127.0.0.1:1433/RetinalHealthDB

# Tùy chọn: Google OAuth
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
# GOOGLE_REDIRECT_URI=http://localhost:9999/api/auth/google/callback
# FRONTEND_BASE_URL=http://localhost:8080
```


**Bước 3.5:** Chạy ứng dụng Flask

Từ thư mục **backend** (sau khi activate .venv):

```bash
cd src
python app.py
```

Hoặc từ thư mục gốc dự án:

```bash
cd backend/src
python app.py
```

Backend chạy tại: **http://localhost:9999**

- API docs (Swagger): **http://localhost:9999/docs**

### 4. Chạy Frontend

  ```bash
  cd frontend
  python -m http.server 8080
  ```
- Mở trình duyệt: **http://localhost:8080**

Đảm bảo backend đã chạy tại **http://localhost:9999** trước khi dùng frontend.

---
