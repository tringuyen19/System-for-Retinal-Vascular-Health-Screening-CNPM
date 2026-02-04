# 📋 PHÂN TÍCH VÀ HƯỚNG TRIỂN KHAI ADMIN FEATURES (FR-31 đến FR-39)

---

## 🎯 TỔNG QUAN YÊUM CẦU (9 Features)

| FR | Tên chức năng | Loại | Phức tạp |
|----|---------------|------|---------|
| **FR-31** | Quản lý tài khoản, bác sĩ, phòng khám | CRUD + Filter | ⭐⭐ |
| **FR-32** | Định nghĩa vai trò & phân quyền | Configuration | ⭐⭐⭐ |
| **FR-33** | Cấu hình AI (ngưỡng, chính sách huấn luyện) | Settings | ⭐⭐ |
| **FR-34** | Quản lý gói dịch vụ & giá cả | CRUD + Pricing | ⭐⭐⭐ |
| **FR-35** | Dashboard tổng thể (sử dụng, doanh thu, hiệu suất) | Analytics | ⭐⭐⭐ |
| **FR-36** | Theo dõi phân tích hệ thống (ảnh, rủi ro, lỗi) | Analytics | ⭐⭐⭐ |
| **FR-37** | Quản lý tuân thủ, audit log, quyền riêng tư | Compliance | ⭐⭐⭐ |
| **FR-38** | Phê duyệt/tạm ngưng đăng ký phòng khám | Workflow | ⭐⭐ |
| **FR-39** | Quản lý mẫu thông báo & chính sách truyền thông | Configuration | ⭐⭐ |

---

## 🏗️ KIẾN TRÚC HIỆN TẠI (Status Check)

### ✅ Đã có sẵn:
```
Backend:
✅ AdminService (633 lines) - Cơ sở logic đã có
✅ AdminController (614 lines) - Routes đã setup
✅ AccountService, ClinicService, DoctorProfileService - Có sẵn
✅ RoleService - Cơ bản CRUD
✅ ServicePackageService, PaymentService - Có
✅ AuditLogService - Ghi log
✅ Repositories - 20+ repo đã có

Frontend:
✅ admin/dashboard.html - Layout sẵn
✅ admin/accounts.html - HTML cơ bản
✅ admin/clinics.html - Có
✅ admin/ai-models.html - Có
✅ admin/statistics.html - Có
✅ admin/settings.html - Có
✅ js/api.js - API functions (909 lines)
```

### ❓ Cần bổ sung:
- Permission model & enforcement
- AI configuration API
- Advanced analytics aggregation
- Clinic approval workflow
- Privacy policy management
- Communication policy CRUD
- Audit log detailed view

---

## 📊 PHÂN TÍCH CHI TIẾT TỪNG FEATURE

### ✅ NHÓM 1: FR-31, FR-32, FR-33 (3 chức năng)
#### **FR-31: Quản lý tài khoản, bác sĩ, phòng khám**

**Status hiện tại:** 70% (HTML có, API cơ bản có)

**Backend cần làm:**
```
✅ AccountService.list_accounts() - Lọc, phân trang
✅ ClinicService.list_clinics() - Lọc, phân trang
✅ DoctorProfileService.list_doctors() - Lọc, phân trang
✅ Bulk operations (suspend, reactivate multiple users)
```

**Frontend cần làm:**
```
✅ admin/accounts.html - Hoàn thiện table, modal CRUD
✅ admin/clinics.html - Danh sách clinic + edit modal
✅ Thêm search box, filter by role/status
✅ Pagination controls
✅ Inline edit cho các trường đơn giản
```

**Implementation flow:**
1. Backend: GET `/api/admin/accounts?role=Doctor&status=active&page=1&limit=20`
2. Backend: PUT `/api/admin/accounts/{id}` - Update account
3. Backend: DELETE `/api/admin/accounts/{id}` - Soft delete
4. Frontend: Load danh sách → show table → modal edit → call API

---

#### **FR-32: Định nghĩa vai trò & phân quyền**

**Status hiện tại:** 40% (RoleService cơ bản, chưa có permissions)

**Backend cần làm:**
```
❌ Permission model (tạo mới)
   - Fields: id, role_id, resource, action (create/read/update/delete)
   - E.g. (Admin, Account, delete), (Doctor, AIResult, read)

❌ PermissionRepository (tạo mới)

❌ RoleService.assign_permissions(role_id, permissions[])
   - Bulk assign permissions to role

❌ GET /api/admin/roles/{id}/permissions - List permissions

✅ API endpoints: CRUD roles (đã có RoleService)
```

**Frontend cần làm:**
```
✅ New page: admin/roles.html
   - List roles
   - Edit role modal
   - Permission matrix (Resources vs Actions)
   - Checkbox để assign permissions
```

**Implementation flow:**
1. Role (Admin, Doctor, Patient, ClinicManager)
2. Each role has permissions (CRUD operations)
3. Admin assigns permissions via checkbox matrix
4. Middleware checks: `require_permission('Account', 'create')`

---

#### **FR-33: Cấu hình AI (ngưỡng, chính sách huấn luyện lại)**

**Status hiện tại:** 50% (AdminService có policy storage, chưa API)

**Backend cần làm:**
```
✅ AdminService._retraining_policies - Đã có
✅ AdminService._ai_configuration - Cần tạo

❌ GET /api/admin/ai/configuration - Get all AI config
   - Response: {thresholds, retraining_policy, auto_retrain}

❌ PUT /api/admin/ai/configuration - Update AI config
   - Params: confidence_threshold, error_rate_threshold, etc.

❌ POST /api/admin/ai/retrain - Trigger retraining
   - Manual retrain với selected model

❌ GET /api/admin/ai/retrain-schedule - Get retrain schedule
```

**Frontend cần làm:**
```
✅ admin/settings.html - Thêm tab "AI Configuration"
   - Confidence threshold slider
   - Error rate threshold
   - Auto-retrain toggle + schedule selector
   - Min samples for retrain input
   - Save button

✅ Show current settings
✅ Show last retrain date
✅ Show next scheduled retrain
```

**Implementation flow:**
1. Show current AI config
2. Edit thresholds/policies
3. Save → PUT /api/admin/ai/configuration
4. Show confirmation

---

### 🎯 **NHÓM 2: FR-34, FR-35, FR-36 (3 chức năng - Analytics & Billing)**

#### **FR-34: Quản lý gói dịch vụ, giá cả, mô hình thanh toán**

**Status hiện tại:** 50% (ServicePackageService, PaymentService có)

**Backend cần làm:**
```
✅ ServicePackageService.list_packages() - Filter
✅ ServicePackageService.get_by_id()
✅ ServicePackageService.update() - Update giá, mô tả
✅ GET /api/admin/service-packages - List all
✅ PUT /api/admin/service-packages/{id} - Update package
✅ POST /api/admin/service-packages - Create new

❌ Pricing tiers (Basic/Standard/Premium/Enterprise)
❌ Feature limits per package (max images, analyses per month)
```

**Frontend cần làm:**
```
✅ admin/packages.html (NEW)
   - List packages in table or cards
   - Package name, description, price
   - Features list
   - Edit button → modal
   - Delete button

✅ Modal to edit:
   - Name, Description
   - Price
   - Feature limits
   - Status (active/inactive)
```

**Implementation flow:**
1. GET `/api/admin/service-packages` → Load table
2. Click Edit → Show modal with current data
3. Update → PUT `/api/admin/service-packages/{id}`
4. Show success message

---

#### **FR-35: Dashboard tổng thể (sử dụng, doanh thu, hiệu suất AI)**

**Status hiện tại:** 30% (AdminService.get_dashboard_summary() cơ bản)

**Backend cần làm:**
```
✅ GET /api/admin/dashboard - Overall metrics
   Response: {
     users: {total_users, total_doctors, total_patients, total_clinics},
     usage: {total_images, total_analyses, completed_analyses, pending_analyses},
     revenue: {total_revenue, total_payments, pending_payments},
     ai_performance: {avg_confidence, success_rate, error_rate},
     top_metrics: {top_conditions, risk_distribution}
   }

❌ GET /api/admin/dashboard/charts - Chart data
   - User growth (line chart)
   - Revenue over time
   - AI accuracy trend
```

**Frontend cần làm:**
```
✅ admin/dashboard.html - Enhance với charts
   - KPI cards (sẵn có)
   - Add line charts (Chart.js hoặc simple SVG)
   - User growth last 30 days
   - Revenue last 30 days
   - AI model accuracy trend
   - Top 5 risk conditions
```

**Implementation flow:**
1. Page load → GET `/api/admin/dashboard`
2. Update KPI cards
3. Get chart data → GET `/api/admin/dashboard/charts`
4. Render charts with library (Chart.js)
5. Auto-refresh every 5 minutes

---

#### **FR-36: Theo dõi phân tích hệ thống (ảnh, rủi ko, lỗi)**

**Status hiện tại:** 10% (Chưa có dedicated analytics endpoints)

**Backend cần làm:**
```
❌ GET /api/admin/analytics/images
   - Total images, by status, by date range
   - Image upload rate (per day)
   
❌ GET /api/admin/analytics/analyses
   - Total analyses, completed, failed, pending
   - Success rate, error rate
   
❌ GET /api/admin/analytics/errors
   - List recent errors
   - Error counts by type
   - Affected users/clinics
   
❌ GET /api/admin/analytics/risk-distribution
   - Breakdown by risk level (low/medium/high)
   - Trend over time
```

**Frontend cần làm:**
```
✅ admin/statistics.html - Enhance với real data
   - Tab 1: Image Analytics
     * Total images, uploads per day
     * Images by status (processed, failed, pending)
   
   - Tab 2: Analysis Quality
     * Success rate %, error rate %
     * Confidence distribution (histogram)
     * Risk distribution pie chart
   
   - Tab 3: Error Tracking
     * Recent errors table
     * Error types breakdown
     * Affected users count
   
   - All with date range picker
```

**Implementation flow:**
1. Load tabs on page load
2. First tab active → GET `/api/admin/analytics/images`
3. Tab click → GET corresponding endpoint
4. Render tables/charts
5. Date range picker to filter

---

### 🔐 **NHÓM 3: FR-37, FR-38, FR-39 (3 chức năng - Compliance & Settings)**

#### **FR-37: Quản lý tuân thủ, audit log, quyền riêng tư**

**Status hiện tại:** 40% (AuditLogService có, privacy settings cơ bản)

**Backend cần làm:**
```
✅ GET /api/admin/audit-logs
   - Filter by: user, action, resource, date range
   - Pagination
   
❌ GET /api/admin/privacy-settings
   - Get current privacy policies
   
❌ PUT /api/admin/privacy-settings
   - Update privacy policies:
     * Data retention period (days)
     * Auto-anonymize after X days
     * GDPR compliance mode
     * Require consent for AI training
     * Allow data sharing
```

**Frontend cần làm:**
```
✅ admin/settings.html - Add "Compliance" tab
   
   - Tab 1: Audit Logs
     * Table: User, Action, Resource, Timestamp
     * Filter by user, action, date range
     * Pagination
     * Export audit logs button
   
   - Tab 2: Privacy Settings
     * Data retention days slider (30-3650)
     * Auto-anonymize toggle + days input
     * GDPR compliance toggle
     * Require AI training consent toggle
     * Allow data sharing toggle
     * Save button
   
   - Tab 3: Data Policies
     * Show current retention policy
     * Show anonymization rules
     * Download policy document button
```

**Implementation flow:**
1. Load current settings
2. Display in forms
3. Edit → call PUT endpoint
4. Show success/error message

---

#### **FR-38: Phê duyệt/tạm ngưng đăng ký phòng khám**

**Status hiện tại:** 20% (Clinic model cơ bản, chưa approval workflow)

**Backend cần làm:**
```
❌ Clinic model cần: status field (pending/approved/suspended/rejected)

❌ GET /api/admin/clinics/pending
   - List clinics with status='pending'
   - Include: clinic name, manager name, registration date, documents

❌ PUT /api/admin/clinics/{id}/approve
   - Change status from pending → approved
   - Send notification to clinic manager

❌ PUT /api/admin/clinics/{id}/suspend
   - Change status to suspended
   - Reason field
   - Send notification to clinic manager

❌ GET /api/admin/clinics/{id}/approval-documents
   - Get registration documents for review
```

**Frontend cần làm:**
```
✅ admin/clinics.html - Add Approval section
   - Tab 1: Pending Approvals
     * Filter table for status='pending'
     * Columns: Clinic name, Manager, Registration date, Documents
     * "View Details" button → modal
     * "Approve" button (green)
     * "Reject" button (red) + reason input
   
   - Tab 2: Active Clinics
     * List approved clinics
     * "Suspend" button → modal + reason input
     * "View Details" button
   
   - Modal: Clinic Details
     * Show all clinic info
     * Documents preview
     * Approve/Reject buttons
     * Reason textarea
```

**Implementation flow:**
1. Load pending clinics: GET `/api/admin/clinics/pending`
2. Show in table
3. Click Approve → PUT `/api/admin/clinics/{id}/approve`
4. Click Suspend → PUT `/api/admin/clinics/{id}/suspend` + reason

---

#### **FR-39: Quản lý mẫu thông báo & chính sách truyền thông**

**Status hiện tại:** 30% (NotificationTemplateService có, chưa policy CRUD)

**Backend cần làm:**
```
✅ GET /api/admin/notification-templates
   - List all templates with filters

❌ GET /api/admin/notification-policies
   - Get all communication policies
   - Response: {ai_result_ready, clinic_approved, payment_success, high_risk_alert, ...}

❌ PUT /api/admin/notification-policies/{policy_name}
   - Update policy:
     * enabled: boolean
     * channels: [in_app, email, sms]
     * recipients: [patient, doctor, clinic_manager]
     * frequency_limit: number or null
     * priority: low/normal/high/urgent

❌ POST /api/admin/notification-templates
   - Create custom template

❌ PUT /api/admin/notification-templates/{id}
   - Update template
```

**Frontend cần làm:**
```
✅ admin/settings.html - Add "Communication" tab
   
   - Tab 1: Notification Templates
     * Table: Template name, Type, Channels
     * Edit button → modal with:
       - Subject template
       - Body template
       - Variables ({{patient_name}}, {{risk_level}}, etc.)
       - Preview button
     * Add new template button
   
   - Tab 2: Notification Policies
     * List policies (AI Result Ready, Clinic Approved, etc.)
     * For each policy:
       - Toggle enabled/disabled
       - Multi-select for channels (in_app, email, sms)
       - Multi-select for recipients
       - Frequency limit input
       - Priority selector
     * Save button
```

**Implementation flow:**
1. GET `/api/admin/notification-policies`
2. Display in toggles/selects
3. Edit → PUT `/api/admin/notification-policies/{policy_name}`
4. Get templates → GET `/api/admin/notification-templates`
5. Edit template → PUT `/api/admin/notification-templates/{id}`

---

## 🛣️ HƯỚNG TRIỂN KHAI TỔNG THỂ

### **Phase 1: NHÓM 1 (FR-31, FR-32, FR-33)**
**Thời gian ước tính:** 4-5 hours

**Công việc:**
```
Backend (2-3h):
1. AccountService.list_accounts() với filter & pagination
2. ClinicService.list_clinics() với filter & pagination  
3. AdminService endpoints cho FR-31
4. Permission model + PermissionRepository (new)
5. RoleService.assign_permissions()
6. AdminService.get_ai_configuration() & update
7. Middleware: @require_permission()

Frontend (2h):
1. Enhance accounts.html (table CRUD)
2. Enhance clinics.html (table CRUD)
3. New: admin/roles.html (role management + permission matrix)
4. admin/settings.html "AI Configuration" tab
5. JavaScript: Load, filter, edit, save logic
```

**Testing:**
- ✅ Bật frontend sau 3 chức năng
- Kiểm tra: list, filter, edit, delete accounts
- Kiểm tra: list, filter, edit, delete clinics
- Kiểm tra: role management & permissions

---

### **Phase 2: NHÓM 2 (FR-34, FR-35, FR-36)**
**Thời gian ước tính:** 4-5 hours

**Công việc:**
```
Backend (2-3h):
1. ServicePackageService enhance (list, update)
2. AdminService.get_dashboard_summary() enhance
3. AdminService.get_analytics_images()
4. AdminService.get_analytics_analyses()
5. AdminService.get_analytics_risk_distribution()
6. AdminService.get_analytics_errors()
7. Chart data aggregation

Frontend (2h):
1. admin/packages.html (NEW) - Package CRUD
2. admin/dashboard.html - Enhance with charts
3. admin/statistics.html - Real data + charts
4. Chart.js library integration
5. Date range picker logic
```

**Testing:**
- ✅ Bật frontend sau 3 chức năng
- Kiểm tra: Service package list, edit
- Kiểm tra: Dashboard metrics load correctly
- Kiểm tra: Statistics & analytics display

---

### **Phase 3: NHÓM 3 (FR-37, FR-38, FR-39)**
**Thời gian ước tính:** 3-4 hours

**Công việc:**
```
Backend (1.5-2h):
1. AuditLogService enhance với filters
2. AdminService.get_privacy_settings()
3. AdminService.update_privacy_settings()
4. Clinic model: add status field
5. AdminService.get_pending_clinics()
6. AdminService.approve_clinic()
7. AdminService.suspend_clinic()
8. NotificationPolicyService (new)
9. AdminService.get_notification_policies()

Frontend (1.5-2h):
1. admin/settings.html - "Compliance" tab
2. admin/settings.html - "Communication" tab
3. admin/clinics.html - Approval section
4. Audit log table with filters
5. Privacy settings form
6. Clinic approval workflow
7. Notification policy editor
```

**Testing:**
- ✅ Bật frontend sau 3 chức năng
- Kiểm tra: Audit log display & filter
- Kiểm tra: Privacy settings save
- Kiểm tra: Clinic approval workflow
- Kiểm tra: Notification policies update

---

## 📋 SUMMARY: Implementation Checklist

### **Backend Components Cần Tạo Mới:**
- [ ] Permission Model & Repository
- [ ] PermissionService
- [ ] NotificationPolicyService
- [ ] Enhanced AuditLogService
- [ ] AI Configuration storage (DB or config file)
- [ ] Clinic approval workflow logic

### **Backend Enhancements:**
- [ ] AdminService methods cho tất cả FR-31-39
- [ ] Filter & pagination trên account, clinic, doctor, image lists
- [ ] Analytics aggregation methods
- [ ] Chart data endpoints

### **Frontend Pages Cần Tạo Mới:**
- [ ] admin/roles.html (Role & Permission Management)
- [ ] admin/packages.html (Service Package Management)

### **Frontend Enhancements:**
- [ ] admin/dashboard.html (Add charts & real data)
- [ ] admin/accounts.html (Enhance CRUD)
- [ ] admin/clinics.html (Enhance CRUD + Approval)
- [ ] admin/statistics.html (Real analytics data)
- [ ] admin/settings.html (Add 3 tabs: AI Config, Compliance, Communication)

### **JavaScript/Libraries:**
- [ ] Chart.js library (for dashboard & analytics)
- [ ] Date range picker (for analytics filters)
- [ ] Enhanced form validation

---

## 🎯 TIMELINE

| Phase | FRs | Backend | Frontend | Total | Testing |
|-------|-----|---------|----------|-------|---------|
| Phase 1 | 31-33 | 2-3h | 2h | 4-5h | Frontend check ✅ |
| Phase 2 | 34-36 | 2-3h | 2h | 4-5h | Frontend check ✅ |
| Phase 3 | 37-39 | 1.5-2h | 1.5-2h | 3-4h | Frontend check ✅ |
| **Total** | **9** | **5.5-8h** | **5.5h** | **11-13h** | **Per phase** |

---

## ✨ BENEFITS CỦA HƯỚNGthiết này:

✅ **Modular**: Chia thành 3 phase, mỗi phase 3-5 chức năng
✅ **Progressive**: Từ đơn giản → phức tạp
✅ **Testable**: Bật frontend mỗi phase để test
✅ **Reusable**: Components & patterns có thể tái sử dụng
✅ **Clean**: Theo Clean Architecture (không lộn xộn)
✅ **Maintainable**: Dễ debug, bảo trì, mở rộng

---

**Bạn sẵn sàng bắt đầu Phase 1 (FR-31, FR-32, FR-33) chưa?**
