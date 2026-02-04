/**
 * AURA Frontend - API functions (skeleton)
 * Gọi API backend, sẽ được implement đầy đủ ở Phase 2+
 */

(function () {
  'use strict';

  const API_BASE = window.AURA_CONFIG ? window.AURA_CONFIG.API_BASE_URL : 'http://localhost:9999';

  function getHeaders(includeAuth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (includeAuth) {
      const key = (window.AURA_CONFIG && window.AURA_CONFIG.STORAGE_KEYS && window.AURA_CONFIG.STORAGE_KEYS.TOKEN) || 'aura_access_token';
      const token = localStorage.getItem(key);
      if (token) headers['Authorization'] = 'Bearer ' + token;
    }
    return headers;
  }

  function parseErrorMessage(res, data) {
    if (data && data.message) return data.message;
    if (data && data.error) return data.error;
    if (res.status === 422 && data && data.errors) {
      const err = data.errors;
      const parts = typeof err === 'object' ? Object.values(err).flat() : [err];
      return parts.filter(Boolean).join('. ') || 'Dữ liệu không hợp lệ.';
    }
    if (res.status === 401) {
      if (data && data.message && (data.message.indexOf('token') !== -1 || data.message.indexOf('Authentication') !== -1)) {
        return data.message + ' Vui lòng đăng nhập lại.';
      }
      return 'Email hoặc mật khẩu không đúng.';
    }
    if (res.status === 409) return 'Email này đã được đăng ký.';
    if (res.status === 501) return data.message || 'Chức năng đang được cập nhật.';
    if (res.status >= 500) return data.message || 'Lỗi máy chủ. Vui lòng thử lại sau.';
    return data.message || 'Yêu cầu thất bại. Vui lòng thử lại.';
  }

  async function request(method, path, body = null, useAuth = true) {
    const opts = { method, headers: getHeaders(useAuth) };
    if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      opts.body = JSON.stringify(body);
    }
    let res;
    try {
      res = await fetch(API_BASE + path, opts);
    } catch (e) {
      throw new Error('Không thể kết nối máy chủ. Kiểm tra backend đã chạy tại ' + API_BASE + ' chưa.');
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(parseErrorMessage(res, data));
    return data;
  }

  /** Upload file (multipart/form-data) to /api/uploads */
  async function uploadFile(file, category) {
    if (!file) throw new Error('Thiếu file upload.');
    const form = new FormData();
    form.append('file', file);
    if (category) form.append('category', category);

    const headers = {};
    // For clinic logo upload, no auth required
    // For other categories, include auth token if available
    if (category !== 'clinic') {
      const key = (window.AURA_CONFIG && window.AURA_CONFIG.STORAGE_KEYS && window.AURA_CONFIG.STORAGE_KEYS.TOKEN) || 'aura_access_token';
      const token = localStorage.getItem(key);
      if (token) headers['Authorization'] = 'Bearer ' + token;
    }

    let res;
    try {
      res = await fetch(API_BASE + '/api/uploads', { method: 'POST', headers, body: form });
    } catch (e) {
      throw new Error('Không thể kết nối máy chủ. Kiểm tra backend đã chạy tại ' + API_BASE + ' chưa.');
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(parseErrorMessage(res, data));
    return data.data; // { url, full_url, ... }
  }

  /** Login - POST /api/auth/login (không gửi token) */
  async function login(credentials) {
    return request('POST', '/api/auth/login', credentials, false);
  }

  /** Register - POST /api/auth/register (không gửi token) */
  async function register(payload) {
    return request('POST', '/api/auth/register', payload, false);
  }

  /** Forgot password - placeholder (backend chưa có endpoint) */
  async function forgotPassword(email) {
    return request('POST', '/api/auth/forgot-password', { email }, false);
  }

  /** Reset password - placeholder (backend chưa có endpoint) */
  async function resetPassword(token, newPassword) {
    return request('POST', '/api/auth/reset-password', { token, new_password: newPassword }, false);
  }

  /** Patient: lấy profile bệnh nhân theo account_id */
  async function getPatientByAccount(accountId) {
    const res = await request('GET', '/api/patients/account/' + accountId);
    return res.data;
  }

  /** Patient: danh sách ảnh võng mạc theo patient_id */
  async function getImagesByPatient(patientId, eyeSide) {
    let path = '/api/retinal-images/patient/' + patientId;
    if (eyeSide) path += '?eye_side=' + encodeURIComponent(eyeSide);
    const res = await request('GET', path);
    return res.data;
  }

  /** Patient: thống kê số ảnh theo patient_id */
  async function getImageStatsByPatient(patientId) {
    const res = await request('GET', '/api/retinal-images/stats?patient_id=' + patientId);
    return res.data;
  }

  /** Patient: upload ảnh (JSON: patient_id, clinic_id, uploaded_by, image_type, eye_side, image_url) */
  async function uploadImage(payload) {
    const res = await request('POST', '/api/retinal-images', payload);
    return res.data;
  }

  /** Doctor/Admin/ClinicManager: upload nhiều ảnh hàng loạt (FR-24) - POST /api/retinal-images/bulk */
  async function uploadBulkImages(payload) {
    const res = await request('POST', '/api/retinal-images/bulk', payload);
    return res.data;
  }

  /** Patient: danh sách báo cáo theo patient_id */
  async function getReportsByPatient(patientId, limit) {
    let path = '/api/medical-reports/patient/' + patientId;
    if (limit) path += '?limit=' + limit;
    const res = await request('GET', path);
    return res.data;
  }

  /** Patient: tạo hồ sơ bệnh nhân (POST /api/patients) */
  async function createPatient(payload) {
    const res = await request('POST', '/api/patients', payload);
    return res.data;
  }

  /** Patient: cập nhật profile (PUT /api/patients/:id) */
  async function updatePatient(patientId, payload) {
    const res = await request('PUT', '/api/patients/' + patientId, payload);
    return res.data;
  }

  /** Admin/Doctor: danh sách tất cả bệnh nhân (GET /api/patients) */
  async function getAllPatients() {
    const res = await request('GET', '/api/patients');
    return res.data;
  }

  /** Patient: chi tiết bệnh nhân theo id (GET /api/patients/:id) - Doctor/Admin */
  async function getPatient(patientId) {
    const res = await request('GET', '/api/patients/' + patientId);
    return res.data;
  }

  /** Admin/Doctor: danh sách tất cả bác sĩ (GET /api/doctors) */
  async function getAllDoctors() {
    const res = await request('GET', '/api/doctors');
    return res.data;
  }

  /** Doctor: lấy bác sĩ theo account_id (GET /api/doctors/account/:id) */
  async function getDoctorByAccount(accountId) {
    const res = await request('GET', '/api/doctors/account/' + accountId);
    return res.data;
  }

  /** Doctor: thống kê hiệu suất (GET /api/doctors/:id/performance) */
  async function getDoctorPerformance(doctorId) {
    const res = await request('GET', '/api/doctors/' + doctorId + '/performance');
    return res.data;
  }

  /** Doctor: danh sách bệnh nhân của bác sĩ - patient upload ảnh -> AI phân tích -> bác sĩ review (GET /api/doctors/:id/patients) */
  async function getDoctorPatients(doctorId) {
    const res = await request('GET', '/api/doctors/' + doctorId + '/patients');
    return res.data;
  }

  /** Doctor: tạo hồ sơ bác sĩ (POST /api/doctors) */
  async function createDoctor(payload) {
    const res = await request('POST', '/api/doctors', payload);
    return res.data;
  }

  /** Doctor: cập nhật hồ sơ (PUT /api/doctors/:id) */
  async function updateDoctor(doctorId, payload) {
    const res = await request('PUT', '/api/doctors/' + doctorId, payload);
    return res.data;
  }

  /** Doctor: tìm kiếm bệnh nhân (GET /api/patients/search?name=&clinic_id=&risk_level=) */
  /** FR-18: Tìm kiếm/lọc bệnh nhân theo mã (patient_id), tên (name), mức rủi ro (risk_level) */
  async function searchPatients(params) {
    const q = new URLSearchParams();
    if (params && params.patient_id != null && params.patient_id !== '') q.set('patient_id', params.patient_id);
    if (params && params.name) q.set('name', params.name);
    if (params && params.clinic_id != null) q.set('clinic_id', params.clinic_id);
    if (params && params.risk_level) q.set('risk_level', params.risk_level);
    const query = q.toString();
    const res = await request('GET', '/api/patients/search' + (query ? '?' + query : ''));
    return res.data;
  }

  /** Doctor: danh sách phân tích chờ duyệt (GET /api/doctor-reviews/pending) */
  async function getPendingReviews() {
    const res = await request('GET', '/api/doctor-reviews/pending');
    return res.data;
  }

  /** Doctor: tạo review cho phân tích (POST /api/doctor-reviews) */
  async function createDoctorReview(payload) {
    const res = await request('POST', '/api/doctor-reviews', payload);
    return res.data;
  }

  /** Doctor: review theo analysis_id (GET /api/doctor-reviews/analysis/:id) */
  async function getReviewByAnalysis(analysisId) {
    const res = await request('GET', '/api/doctor-reviews/analysis/' + analysisId);
    return res.data;
  }

  /** Doctor: danh sách review của bác sĩ (GET /api/doctor-reviews/doctor/:id) */
  async function getReviewsByDoctor(doctorId) {
    const res = await request('GET', '/api/doctor-reviews/doctor/' + doctorId);
    return res.data;
  }

  /** Doctor: duyệt review (PUT /api/doctor-reviews/:id/approve). Body (optional): { comment, ai_accuracy_feedback } - FR-19 */
  async function approveReview(reviewId, body) {
    const res = await request('PUT', '/api/doctor-reviews/' + reviewId + '/approve', body || null);
    return res.data;
  }

  /** Doctor: từ chối review (PUT /api/doctor-reviews/:id/reject). comment required; ai_accuracy_feedback optional (FR-19) */
  async function rejectReview(reviewId, comment, aiAccuracyFeedback) {
    const payload = { comment: comment || '' };
    if (aiAccuracyFeedback) payload.ai_accuracy_feedback = aiAccuracyFeedback;
    const res = await request('PUT', '/api/doctor-reviews/' + reviewId + '/reject', payload);
    return res.data;
  }

  /** Doctor/Admin: tổng hợp phản hồi AI (FR-19) - GET /api/doctor-reviews/feedback/aggregation?doctor_id= */
  async function getFeedbackAggregation(doctorId) {
    const q = doctorId != null ? '?doctor_id=' + encodeURIComponent(doctorId) : '';
    const res = await request('GET', '/api/doctor-reviews/feedback/aggregation' + q);
    return res.data;
  }

  /** Doctor: danh sách báo cáo của bác sĩ (GET /api/medical-reports/doctor/:id) */
  async function getReportsByDoctor(doctorId) {
    const res = await request('GET', '/api/medical-reports/doctor/' + doctorId);
    return res.data;
  }

  /** Doctor: tạo báo cáo y tế (POST /api/medical-reports) - FR-16: medical_notes, diagnosis, treatment_recommendations */
  async function createMedicalReport(payload) {
    const res = await request('POST', '/api/medical-reports', payload);
    return res.data;
  }

  /** Doctor: lấy báo cáo theo ID (GET /api/medical-reports/:id) */
  async function getMedicalReport(reportId) {
    const res = await request('GET', '/api/medical-reports/' + reportId);
    return res.data;
  }

  /** Doctor: cập nhật báo cáo (PUT /api/medical-reports/:id) - FR-16: medical_notes, diagnosis, treatment_recommendations */
  async function updateMedicalReport(reportId, payload) {
    const res = await request('PUT', '/api/medical-reports/' + reportId, payload);
    return res.data;
  }

  /** Patient/Doctor: tải PDF báo cáo từ API (GET /api/medical-reports/:id/export?format=pdf). Gửi kèm token, trả blob và trigger download. */
  async function exportMedicalReportPdf(reportId) {
    const API_BASE = window.AURA_CONFIG ? window.AURA_CONFIG.API_BASE_URL : 'http://localhost:9999';
    const path = '/api/medical-reports/' + reportId + '/export?format=pdf';
    const headers = getHeaders(true);
    delete headers['Content-Type']; // binary response
    let res;
    try {
      res = await fetch(API_BASE + path, { method: 'GET', headers });
    } catch (e) {
      throw new Error('Không thể kết nối máy chủ. Kiểm tra backend đã chạy chưa.');
    }
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(parseErrorMessage(res, data));
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'medical_report_' + reportId + '.pdf';
    a.click();
    URL.revokeObjectURL(url);
  }

  /** Doctor: danh sách hội thoại (GET /api/conversations/doctor/:id). Trả full response { message, data: { doctor_id, count, conversations } } */
  async function getConversationsByDoctor(doctorId, activeOnly) {
    let path = '/api/conversations/doctor/' + doctorId;
    if (activeOnly) path += '?active_only=true';
    const res = await request('GET', path);
    return res && res.data != null ? res : { data: res };
  }

  /** Patient: danh sách hội thoại (GET /api/conversations/patient/:id) - FR-10 */
  async function getConversationsByPatient(patientId, activeOnly) {
    let path = '/api/conversations/patient/' + patientId;
    if (activeOnly) path += '?active_only=true';
    const res = await request('GET', path);
    return res.data;
  }

  /** Patient: bác sĩ đã review kết quả của patient (GET /api/doctor-reviews/patient/:id/doctors) - FR-10 */
  async function getDoctorsWhoReviewedPatient(patientId) {
    const res = await request('GET', '/api/doctor-reviews/patient/' + patientId + '/doctors');
    return res.data;
  }

  /** Tạo hoặc lấy hội thoại patient-doctor (POST /api/conversations) - FR-10 */
  async function createConversation(patientId, doctorId) {
    const res = await request('POST', '/api/conversations', { patient_id: patientId, doctor_id: doctorId });
    return res.data;
  }

  /** AI Analysis: chi tiết phân tích (GET /api/ai-analysis/:id) */
  async function getAnalysis(analysisId) {
    const res = await request('GET', '/api/ai-analysis/' + analysisId);
    return res.data;
  }

  /** AI Analysis: phân tích theo bệnh nhân (GET /api/ai-analysis/patient/:id) */
  async function getPatientAnalyses(patientId, limit, offset) {
    let path = '/api/ai-analysis/patient/' + patientId;
    const q = [];
    if (limit != null) q.push('limit=' + limit);
    if (offset != null) q.push('offset=' + offset);
    if (q.length) path += '?' + q.join('&');
    const res = await request('GET', path);
    return res.data;
  }

  /** AI Analysis: trend theo bệnh nhân (GET /api/ai-analysis/patient/:id/trend?days=) - FR-17 */
  async function getPatientTrend(patientId, days) {
    let path = '/api/ai-analysis/patient/' + patientId + '/trend';
    if (days != null) path += '?days=' + days;
    const res = await request('GET', path);
    return res.data;
  }

  /** AI Results: danh sách tất cả (GET /api/ai-results) - entity [dbo].[ai_results] - Doctor/Admin */
  async function getAllResults() {
    const res = await request('GET', '/api/ai-results');
    return res.data;
  }

  /** AI Results: kết quả theo analysis (GET /api/ai-results/analysis/:id) - disease_type, risk_level, confidence_score */
  async function getResultsByAnalysis(analysisId) {
    const res = await request('GET', '/api/ai-results/analysis/' + analysisId);
    return res.data;
  }

  /** AI Annotations: danh sách tất cả (GET /api/ai-annotations) - entity [dbo].[ai_annotations] - Doctor/Admin */
  async function getAllAnnotations() {
    const res = await request('GET', '/api/ai-annotations');
    return res.data;
  }

  /** AI Annotations: chú thích theo analysis (GET /api/ai-annotations/analysis/:id) - FR-14 Doctor xem chú thích */
  async function getAnnotationByAnalysis(analysisId) {
    const res = await request('GET', '/api/ai-annotations/analysis/' + analysisId);
    return res.data;
  }

  /** AI Analysis: danh sách phân tích đã hoàn thành (GET /api/ai-analysis/completed) - Doctor/Admin */
  async function getCompletedAnalyses() {
    const res = await request('GET', '/api/ai-analysis/completed');
    return res.data;
  }

  /** Retinal image: chi tiết ảnh theo id (GET /api/retinal-images/:id) - patient_id, image_url */
  async function getRetinalImage(imageId) {
    const res = await request('GET', '/api/retinal-images/' + imageId);
    return res.data;
  }

  /** Messages: tin nhắn theo conversation (GET /api/messages/conversation/:id) */
  async function getMessagesByConversation(conversationId) {
    const res = await request('GET', '/api/messages/conversation/' + conversationId);
    return res.data;
  }

  /** Messages: gửi tin nhắn (POST /api/messages) */
  async function sendMessage(payload) {
    const res = await request('POST', '/api/messages', payload);
    return res.data;
  }

  /** Clinic: chi tiết phòng khám (GET /api/clinics/:id) */
  async function getClinic(clinicId) {
    const res = await request('GET', '/api/clinics/' + clinicId);
    return res.data;
  }

  /** Clinic: cập nhật phòng khám (PUT /api/clinics/:id) */
  async function updateClinic(clinicId, payload) {
    const res = await request('PUT', '/api/clinics/' + clinicId, payload);
    return res.data;
  }

  /** Clinic: thành viên (GET /api/clinics/:id/members) */
  async function getClinicMembers(clinicId) {
    const res = await request('GET', '/api/clinics/' + clinicId + '/members');
    return res.data;
  }

  /** Clinic: bệnh nhân thuộc phòng khám (GET /api/patients/assigned/clinic/:id) */
  async function getAssignedPatients(clinicId) {
    const res = await request('GET', '/api/patients/assigned/clinic/' + clinicId);
    return res.data;
  }

  /** Clinic: ảnh võng mạc tại phòng khám (GET /api/retinal-images/clinic/:id) */
  async function getImagesByClinic(clinicId) {
    const res = await request('GET', '/api/retinal-images/clinic/' + clinicId);
    return res.data;
  }

  /** Clinic: tổng hợp rủi ro (GET /api/clinics/:id/risk-aggregation) */
  async function getClinicRiskAggregation(clinicId) {
    const res = await request('GET', '/api/clinics/' + clinicId + '/risk-aggregation');
    return res.data;
  }

  /** Clinic: sử dụng dịch vụ (GET /api/clinics/:id/usage) */
  async function getClinicUsage(clinicId) {
    const res = await request('GET', '/api/clinics/' + clinicId + '/usage');
    return res.data;
  }

  /** Clinic: cảnh báo nguy cơ cao (GET /api/clinics/:id/high-risk-alerts) */
  async function getHighRiskAlerts(clinicId, riskLevel) {
    let path = '/api/clinics/' + clinicId + '/high-risk-alerts';
    if (riskLevel) path += '?risk_level=' + encodeURIComponent(riskLevel);
    const res = await request('GET', path);
    return res.data;
  }

  /** Clinic: xu hướng bất thường (GET /api/clinics/:id/abnormal-trends) */
  async function getClinicAbnormalTrends(clinicId, days) {
    let path = '/api/clinics/' + clinicId + '/abnormal-trends';
    if (days != null) path += '?days=' + days;
    const res = await request('GET', path);
    return res.data;
  }

  /** Clinic: tóm tắt báo cáo (GET /api/clinics/:id/reports-summary) */
  async function getClinicReportsSummary(clinicId, startDate, endDate) {
    let path = '/api/clinics/' + clinicId + '/reports-summary';
    const q = [];
    if (startDate) q.push('start_date=' + encodeURIComponent(startDate));
    if (endDate) q.push('end_date=' + encodeURIComponent(endDate));
    if (q.length) path += '?' + q.join('&');
    const res = await request('GET', path);
    return res.data;
  }

  /** Clinic: báo cáo tầm soát (GET /api/clinics/:id/screening-report) */
  async function getClinicScreeningReport(clinicId, params) {
    let path = '/api/clinics/' + clinicId + '/screening-report';
    if (params) {
      const q = new URLSearchParams();
      if (params.campaign_name) q.set('campaign_name', params.campaign_name);
      if (params.start_date) q.set('start_date', params.start_date);
      if (params.end_date) q.set('end_date', params.end_date);
      const s = q.toString();
      if (s) path += '?' + s;
    }
    const res = await request('GET', path);
    return res.data;
  }

  /** Clinic: xuất thống kê (GET /api/clinics/:id/export-statistics) - FR-30 */
  async function exportClinicStatistics(clinicId, format, options) {
    const params = new URLSearchParams();
    if (format) params.set('format', format);
    if (options && options.start_date) params.set('start_date', options.start_date);
    if (options && options.end_date) params.set('end_date', options.end_date);
    const qs = params.toString();
    const path = '/api/clinics/' + clinicId + '/export-statistics' + (qs ? '?' + qs : '');
    const res = await request('GET', path);
    return res.data;
  }

  /** Subscriptions: danh sách theo account (GET /api/subscriptions/account/:id) */
  async function getSubscriptionsByAccount(accountId) {
    const res = await request('GET', '/api/subscriptions/account/' + accountId);
    return res.data;
  }

  /** Subscriptions: gói đang active (GET /api/subscriptions/account/:id/active) */
  async function getActiveSubscription(accountId) {
    const res = await request('GET', '/api/subscriptions/account/' + accountId + '/active');
    return res.data;
  }

  /** Subscriptions: số lượt còn lại (GET /api/subscriptions/account/:id/credits) - FR-12 */
  async function getAccountCredits(accountId) {
    const res = await request('GET', '/api/subscriptions/account/' + accountId + '/credits');
    return res.data;
  }

  /** Subscriptions: mua gói demo PTT chuyển khoản (POST /api/subscriptions/purchase-demo) - FR-11 */
  async function purchasePackageDemo(accountId, packageId) {
    const res = await request('POST', '/api/subscriptions/purchase-demo', { account_id: accountId, package_id: packageId });
    return res.data;
  }

  /** Service packages: danh sách gói cho patient (ids 1-5) - FR-11 */
  async function getServicePackagesForPatient() {
    // FR-34: prefer type+active filter; fallback to legacy ids for older DBs
    try {
      const res = await request('GET', '/api/service-packages?type=patient&active=1');
      if (res && res.data && Array.isArray(res.data.packages) && res.data.packages.length) return res.data;
    } catch (e) { /* fallback below */ }
    const legacy = await request('GET', '/api/service-packages?ids=1,2,3,4,5');
    return legacy.data;
  }

  /** Service packages: danh sách gói cấp phòng khám (ids 6,7,8) - FR-28 */
  async function getServicePackagesForClinic() {
    // FR-34: prefer type+active filter; fallback to legacy ids for older DBs
    try {
      const res = await request('GET', '/api/service-packages?type=clinic&active=1');
      if (res && res.data && Array.isArray(res.data.packages) && res.data.packages.length) return res.data;
    } catch (e) { /* fallback below */ }
    const legacy = await request('GET', '/api/service-packages?ids=6,7,8');
    return legacy.data;
  }

  // ---------- Admin: Billing (FR-34) ----------
  async function adminListServicePackages(opts) {
    opts = opts || {};
    const q = [];
    if (opts.type) q.push('type=' + encodeURIComponent(opts.type));
    if (opts.active != null) q.push('active=' + (opts.active ? '1' : '0'));
    const path = '/api/service-packages' + (q.length ? ('?' + q.join('&')) : '');
    const res = await request('GET', path);
    return res.data;
  }

  async function adminCreateServicePackage(payload) {
    const res = await request('POST', '/api/service-packages', payload);
    return res.data;
  }

  async function adminUpdateServicePackage(packageId, payload) {
    const res = await request('PUT', '/api/service-packages/' + packageId, payload);
    return res.data;
  }

  async function adminDeleteServicePackage(packageId) {
    const res = await request('DELETE', '/api/service-packages/' + packageId);
    return res.data;
  }

  async function adminListPayments(opts) {
    opts = opts || {};
    if (opts.status) {
      const res = await request('GET', '/api/payments/status/' + encodeURIComponent(opts.status));
      return res.data;
    }
    let path = '/api/payments';
    const q = [];
    if (opts.start_date) q.push('start_date=' + encodeURIComponent(opts.start_date));
    if (opts.end_date) q.push('end_date=' + encodeURIComponent(opts.end_date));
    if (q.length) path += '?' + q.join('&');
    const res = await request('GET', path);
    return res.data;
  }

  async function adminCompletePayment(paymentId) {
    const res = await request('PUT', '/api/payments/' + paymentId + '/complete', {});
    return res.data;
  }

  async function adminFailPayment(paymentId) {
    const res = await request('PUT', '/api/payments/' + paymentId + '/fail', {});
    return res.data;
  }

  async function adminRefundPayment(paymentId) {
    const res = await request('PUT', '/api/payments/' + paymentId + '/refund', {});
    return res.data;
  }

  /** Mua gói cấp phòng khám (demo) - FR-28 */
  async function purchaseClinicPackageDemo(accountId, packageId) {
    const res = await request('POST', '/api/subscriptions/purchase-clinic-demo', { account_id: accountId, package_id: packageId });
    return res.data;
  }

  /** Gia hạn subscription - FR-28 */
  async function renewSubscription(subscriptionId, durationDays, additionalCredits) {
    const res = await request('PUT', '/api/subscriptions/' + subscriptionId + '/renew', {
      duration_days: durationDays,
      additional_credits: additionalCredits != null ? additionalCredits : 0
    });
    return res.data;
  }

  /** Payments: lịch sử thanh toán theo account (GET /api/payments/account/:id/history) - FR-12 */
  async function getPaymentHistory(accountId, limit, offset) {
    let path = '/api/payments/account/' + accountId + '/history';
    const q = [];
    if (limit != null) q.push('limit=' + limit);
    if (offset != null) q.push('offset=' + offset);
    if (q.length) path += '?' + q.join('&');
    const res = await request('GET', path);
    return res.data;
  }

  /** Notifications: danh sách thông báo theo account (GET /api/notifications/account/:id) - FR-9 */
  async function getNotificationsByAccount(accountId, unreadOnly) {
    let path = '/api/notifications/account/' + accountId;
    if (unreadOnly) path += '/unread';
    const res = await request('GET', path);
    return res.data;
  }

  // ---------- Admin: Accounts (CRUD, role, status) ----------
  /** Admin: danh sách tất cả tài khoản (GET /api/accounts) */
  async function getAllAccounts() {
    const res = await request('GET', '/api/accounts');
    return res.data;
  }

  /** Admin: tạo tài khoản (POST /api/accounts) body: { email, password, role_id, clinic_id?, status? } */
  async function createAccount(payload) {
    const res = await request('POST', '/api/accounts', payload);
    return res.data;
  }

  /** Admin: lấy tài khoản theo ID (GET /api/accounts/:id) */
  async function getAccount(accountId) {
    const res = await request('GET', '/api/accounts/' + accountId);
    return res.data;
  }

  /** Admin: tài khoản theo role (GET /api/accounts/role/:role_id) */
  async function getAccountsByRole(roleId) {
    const res = await request('GET', '/api/accounts/role/' + roleId);
    return res.data;
  }

  /** Admin: tài khoản theo status (GET /api/accounts/status/:status) */
  async function getAccountsByStatus(status) {
    const res = await request('GET', '/api/accounts/status/' + encodeURIComponent(status));
    return res.data;
  }

  /** Admin: cập nhật tài khoản (PUT /api/accounts/:id) */
  async function updateAccountById(accountId, payload) {
    const res = await request('PUT', '/api/accounts/' + accountId, payload);
    return res.data;
  }

  /** Admin: cập nhật trạng thái tài khoản (PUT /api/accounts/:id/status) body: { status } */
  async function updateAccountStatus(accountId, status) {
    const res = await request('PUT', '/api/accounts/' + accountId + '/status', { status });
    return res.data;
  }

  /** Admin: đổi mật khẩu tài khoản (PUT /api/accounts/:id/password) body: { new_password } - plain text, backend sẽ hash */
  async function updateAccountPassword(accountId, newPassword) {
    const res = await request('PUT', '/api/accounts/' + accountId + '/password', { new_password: newPassword });
    return res.data;
  }

  /** Admin: xóa tài khoản (DELETE /api/accounts/:id) */
  async function deleteAccount(accountId) {
    const res = await request('DELETE', '/api/accounts/' + accountId);
    return res.data;
  }

  /** Admin: thống kê tài khoản (GET /api/accounts/stats) */
  async function getAccountStats(roleId, status) {
    let path = '/api/accounts/stats';
    const q = [];
    if (roleId != null) q.push('role_id=' + roleId);
    if (status) q.push('status=' + encodeURIComponent(status));
    if (q.length) path += '?' + q.join('&');
    const res = await request('GET', path);
    return res.data;
  }

  // ---------- Admin: Roles ----------
  /** Admin: danh sách roles (GET /api/roles) */
  async function getAllRoles() {
    const res = await request('GET', '/api/roles');
    return res.data;
  }

  /** Admin: tạo role (POST /api/roles) body: { role_name } */
  async function createRole(roleName) {
    const res = await request('POST', '/api/roles', { role_name: roleName });
    return res.data;
  }

  /** Admin: cập nhật role (PUT /api/roles/:id) body: { role_name } */
  async function updateRole(roleId, roleName) {
    const res = await request('PUT', '/api/roles/' + roleId, { role_name: roleName });
    return res.data;
  }

  /** Admin: xóa role (DELETE /api/roles/:id) */
  async function deleteRole(roleId) {
    const res = await request('DELETE', '/api/roles/' + roleId);
    return res.data;
  }

  // ---------- Clinic Registration (FR-22) ----------
  /** Register clinic with manager account (POST /api/clinics) */
  async function registerClinic(payload) {
    const res = await request('POST', '/api/clinics', payload, false);
    return res.data;
  }

  // ---------- Admin: Clinics (verify/reject/approve/suspend) ----------
  /** Admin: danh sách phòng khám có lọc (GET /api/clinics?status=) */
  async function listClinics(status) {
    let path = '/api/clinics';
    if (status) path += '?status=' + encodeURIComponent(status);
    const res = await request('GET', path);
    return res.data;
  }

  /** Admin: phòng khám chờ duyệt (GET /api/clinics/pending) */
  async function getPendingClinics() {
    const res = await request('GET', '/api/clinics/pending');
    return res.data;
  }

  /** Public: danh sách phòng khám đã được duyệt (GET /api/clinics/verified) */
  async function getVerifiedClinics() {
    const res = await request('GET', '/api/clinics/verified', null, false);
    return res.data;
  }

  /** Admin: duyệt phòng khám (PUT /api/clinics/:id/verify) body: { admin_notes? } */
  async function verifyClinic(clinicId, adminNotes) {
    const res = await request('PUT', '/api/clinics/' + clinicId + '/verify', { admin_notes: adminNotes || '' });
    return res.data;
  }

  /** Admin: từ chối phòng khám (PUT /api/clinics/:id/reject) body: { rejection_reason? } */
  async function rejectClinic(clinicId, rejectionReason) {
    const res = await request('PUT', '/api/clinics/' + clinicId + '/reject', { rejection_reason: rejectionReason || '' });
    return res.data;
  }

  /** Admin: phê duyệt / gỡ treo (PUT /api/clinics/:id/approve) body: { admin_notes? } */
  async function approveClinic(clinicId, adminNotes) {
    const res = await request('PUT', '/api/clinics/' + clinicId + '/approve', { admin_notes: adminNotes || '' });
    return res.data;
  }

  /** Admin: treo phòng khám (PUT /api/clinics/:id/suspend) body: { suspension_reason? } */
  async function suspendClinic(clinicId, suspensionReason) {
    const res = await request('PUT', '/api/clinics/' + clinicId + '/suspend', { suspension_reason: suspensionReason || '' });
    return res.data;
  }

  /** Admin: xóa phòng khám (DELETE /api/clinics/:id) */
  async function deleteClinic(clinicId) {
    const res = await request('DELETE', '/api/clinics/' + clinicId);
    return res.data;
  }

  /** Admin: thống kê phòng khám (GET /api/clinics/stats?verification_status=) */
  async function getClinicStats(verificationStatus) {
    let path = '/api/clinics/stats';
    if (verificationStatus) path += '?verification_status=' + encodeURIComponent(verificationStatus);
    const res = await request('GET', path);
    return res.data;
  }

  // ---------- Admin: AI Model Versions ----------
  /** Admin: danh sách phiên bản AI (GET /api/ai-model-versions) */
  async function getAllAiModelVersions() {
    const res = await request('GET', '/api/ai-model-versions');
    return res.data;
  }

  /** Admin: phiên bản đang active (GET /api/ai-model-versions/active) */
  async function getActiveAiModels() {
    const res = await request('GET', '/api/ai-model-versions/active');
    return res.data;
  }

  /** Admin: kích hoạt phiên bản (PUT /api/ai-model-versions/:id/activate) */
  async function activateAiModel(modelVersionId) {
    const res = await request('PUT', '/api/ai-model-versions/' + modelVersionId + '/activate', null);
    return res.data;
  }

  /** Admin: tắt phiên bản (PUT /api/ai-model-versions/:id/deactivate) */
  async function deactivateAiModel(modelVersionId) {
    const res = await request('PUT', '/api/ai-model-versions/' + modelVersionId + '/deactivate', null);
    return res.data;
  }

  /** Admin: tạo phiên bản (POST /api/ai-model-versions) */
  async function createAiModelVersion(payload) {
    const res = await request('POST', '/api/ai-model-versions', payload);
    return res.data;
  }

  /** Admin: cập nhật threshold (PUT /api/ai-model-versions/:id/threshold) body: { threshold_config } */
  async function updateAiModelThreshold(modelVersionId, thresholdConfig) {
    const res = await request('PUT', '/api/ai-model-versions/' + modelVersionId + '/threshold', { threshold_config: thresholdConfig });
    return res.data;
  }

  /** Admin: xóa phiên bản (DELETE /api/ai-model-versions/:id) */
  async function deleteAiModelVersion(modelVersionId) {
    const res = await request('DELETE', '/api/ai-model-versions/' + modelVersionId);
    return res.data;
  }

  /** Admin: thống kê AI models (GET /api/ai-model-versions/stats) */
  async function getAiModelStats() {
    const res = await request('GET', '/api/ai-model-versions/stats');
    return res.data;
  }

  // ---------- Admin: Dashboard & Analytics ----------
  /** Admin: dashboard tổng quan (GET /api/admin/dashboard) */
  async function getAdminDashboard() {
    const res = await request('GET', '/api/admin/dashboard');
    return res.data;
  }

  /** Admin: analytics ảnh (GET /api/admin/analytics/images?days=) */
  async function getAdminImageAnalytics(days) {
    let path = '/api/admin/analytics/images';
    if (days != null && days !== '') path += '?days=' + (days === 'all' ? '0' : days);
    const res = await request('GET', path);
    return res.data;
  }

  /** Admin: analytics phân bố rủi ro (GET /api/admin/analytics/risk-distribution) */
  async function getAdminRiskDistribution(days) {
    let path = '/api/admin/analytics/risk-distribution';
    if (days != null && days !== '') path += '?days=' + (days === 'all' ? '0' : days);
    const res = await request('GET', path);
    return res.data;
  }

  /** Admin: analytics doanh thu (GET /api/admin/analytics/revenue?days=) */
  async function getAdminRevenueAnalytics(days) {
    let path = '/api/admin/analytics/revenue';
    if (days != null && days !== '') path += '?days=' + (days === 'all' ? '0' : days);
    const res = await request('GET', path);
    return res.data;
  }

  /** Admin: analytics tỷ lệ lỗi (GET /api/admin/analytics/error-rates) */
  async function getAdminErrorRateAnalytics(days) {
    let path = '/api/admin/analytics/error-rates';
    if (days != null && days !== '') path += '?days=' + (days === 'all' ? '0' : days);
    const res = await request('GET', path);
    return res.data;
  }

  /** Admin: cấu hình AI (GET /api/admin/ai-config) */
  async function getAdminAiConfig() {
    const res = await request('GET', '/api/admin/ai-config');
    return res.data;
  }

  /** Admin: cập nhật cấu hình AI (PUT /api/admin/ai-config) */
  async function updateAdminAiConfig(payload) {
    const res = await request('PUT', '/api/admin/ai-config', payload);
    return res.data;
  }

  /** Admin: cài đặt bảo mật (GET /api/admin/privacy-settings) */
  async function getAdminPrivacySettings() {
    const res = await request('GET', '/api/admin/privacy-settings');
    return res.data;
  }

  /** Admin: cập nhật cài đặt bảo mật (PUT /api/admin/privacy-settings) */
  async function updateAdminPrivacySettings(payload) {
    const res = await request('PUT', '/api/admin/privacy-settings', payload);
    return res.data;
  }

  /** Admin: chính sách thông báo (GET /api/admin/communication-policies) */
  async function getAdminCommunicationPolicies() {
    const res = await request('GET', '/api/admin/communication-policies');
    return res.data;
  }

  /** Admin: cập nhật chính sách thông báo (PUT /api/admin/communication-policies/:type) */
  async function updateAdminCommunicationPolicy(notificationType, payload) {
    const res = await request('PUT', '/api/admin/communication-policies/' + encodeURIComponent(notificationType), payload);
    return res.data;
  }

  // ---------- Admin: Notification Templates (FR-39) ----------
  /** Admin: danh sách mẫu thông báo (GET /api/admin/notification-templates) */
  async function adminListNotificationTemplates(includeInactive) {
    let path = '/api/admin/notification-templates';
    if (includeInactive) path += '?include_inactive=true';
    const res = await request('GET', path);
    return res.data;
  }

  /** Admin: kích hoạt mẫu (PUT /api/admin/notification-templates/:id/activate) */
  async function adminActivateNotificationTemplate(templateId) {
    const res = await request('PUT', '/api/admin/notification-templates/' + templateId + '/activate', {});
    return res.data;
  }

  /** Admin: tắt mẫu (PUT /api/admin/notification-templates/:id/deactivate) */
  async function adminDeactivateNotificationTemplate(templateId) {
    const res = await request('PUT', '/api/admin/notification-templates/' + templateId + '/deactivate', {});
    return res.data;
  }

  window.AuraAPI = {
    get: (path) => request('GET', path),
    post: (path, body) => request('POST', path, body),
    put: (path, body) => request('PUT', path, body),
    patch: (path, body) => request('PATCH', path, body),
    delete: (path) => request('DELETE', path),
    login,
    register,
    forgotPassword,
    resetPassword,
    uploadFile,
    getPatientByAccount,
    getImagesByPatient,
    getImageStatsByPatient,
    uploadImage,
    uploadBulkImages,
    getReportsByPatient,
    createPatient,
    updatePatient,
    getPatient,
    getAllPatients,
    getAllDoctors,
    getDoctorByAccount,
    getDoctorPerformance,
    getDoctorPatients,
    createDoctor,
    updateDoctor,
    searchPatients,
    getPendingReviews,
    createDoctorReview,
    getReviewByAnalysis,
    getReviewsByDoctor,
    approveReview,
    rejectReview,
    getFeedbackAggregation,
    getReportsByDoctor,
    createMedicalReport,
    getMedicalReport,
    updateMedicalReport,
    exportMedicalReportPdf,
    getConversationsByDoctor,
    getConversationsByPatient,
    getDoctorsWhoReviewedPatient,
    createConversation,
    getAnalysis,
    getPatientAnalyses,
    getPatientTrend,
    getAllResults,
    getAllAnnotations,
    getResultsByAnalysis,
    getAnnotationByAnalysis,
    getCompletedAnalyses,
    getRetinalImage,
    getMessagesByConversation,
    sendMessage,
    getClinic,
    updateClinic,
    getClinicMembers,
    getAssignedPatients,
    getImagesByClinic,
    getClinicRiskAggregation,
    getClinicUsage,
    getHighRiskAlerts,
    getClinicAbnormalTrends,
    getClinicReportsSummary,
    getClinicScreeningReport,
    exportClinicStatistics,
    getSubscriptionsByAccount,
    getActiveSubscription,
    getAccountCredits,
    purchasePackageDemo,
    getServicePackagesForPatient,
    getServicePackagesForClinic,
    adminListServicePackages,
    adminCreateServicePackage,
    adminUpdateServicePackage,
    adminDeleteServicePackage,
    adminListPayments,
    adminCompletePayment,
    adminFailPayment,
    adminRefundPayment,
    purchaseClinicPackageDemo,
    renewSubscription,
    getPaymentHistory,
    getNotificationsByAccount,
    getAllAccounts,
    createAccount,
    getAccount,
    getAccountsByRole,
    getAccountsByStatus,
    updateAccountById,
    updateAccountStatus,
    updateAccountPassword,
    deleteAccount,
    getAccountStats,
    getAllRoles,
    createRole,
    updateRole,
    deleteRole,
    registerClinic,
    listClinics,
    getPendingClinics,
    getVerifiedClinics,
    verifyClinic,
    rejectClinic,
    approveClinic,
    suspendClinic,
    deleteClinic,
    getClinicStats,
    getAllAiModelVersions,
    getActiveAiModels,
    activateAiModel,
    deactivateAiModel,
    createAiModelVersion,
    updateAiModelThreshold,
    deleteAiModelVersion,
    getAiModelStats,
    getAdminDashboard,
    getAdminImageAnalytics,
    getAdminRiskDistribution,
    getAdminRevenueAnalytics,
    getAdminErrorRateAnalytics,
    getAdminAiConfig,
    updateAdminAiConfig,
    getAdminPrivacySettings,
    updateAdminPrivacySettings,
    getAdminCommunicationPolicies,
    updateAdminCommunicationPolicy,
    adminListNotificationTemplates,
    adminActivateNotificationTemplate,
    adminDeactivateNotificationTemplate,
  };
})();
