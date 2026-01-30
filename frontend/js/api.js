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

  /** Patient: chi tiết bệnh nhân theo id (GET /api/patients/:id) - Doctor/Admin */
  async function getPatient(patientId) {
    const res = await request('GET', '/api/patients/' + patientId);
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
  async function searchPatients(params) {
    const q = new URLSearchParams();
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

  /** Doctor: duyệt review (PUT /api/doctor-reviews/:id/approve) */
  async function approveReview(reviewId) {
    const res = await request('PUT', '/api/doctor-reviews/' + reviewId + '/approve', null);
    return res.data;
  }

  /** Doctor: từ chối review (PUT /api/doctor-reviews/:id/reject) body: { comment } */
  async function rejectReview(reviewId, comment) {
    const res = await request('PUT', '/api/doctor-reviews/' + reviewId + '/reject', { comment: comment || '' });
    return res.data;
  }

  /** Doctor: danh sách báo cáo của bác sĩ (GET /api/medical-reports/doctor/:id) */
  async function getReportsByDoctor(doctorId) {
    const res = await request('GET', '/api/medical-reports/doctor/' + doctorId);
    return res.data;
  }

  /** Doctor: tạo báo cáo y tế (POST /api/medical-reports) */
  async function createMedicalReport(payload) {
    const res = await request('POST', '/api/medical-reports', payload);
    return res.data;
  }

  /** Doctor: danh sách hội thoại (GET /api/conversations/doctor/:id) */
  async function getConversationsByDoctor(doctorId, activeOnly) {
    let path = '/api/conversations/doctor/' + doctorId;
    if (activeOnly) path += '?active_only=true';
    const res = await request('GET', path);
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

  /** Clinic: xuất thống kê (GET /api/clinics/:id/export-statistics) */
  async function exportClinicStatistics(clinicId, format) {
    let path = '/api/clinics/' + clinicId + '/export-statistics';
    if (format) path += '?format=' + encodeURIComponent(format);
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
    getPatientByAccount,
    getImagesByPatient,
    getImageStatsByPatient,
    uploadImage,
    getReportsByPatient,
    createPatient,
    updatePatient,
    getPatient,
    getDoctorByAccount,
    getDoctorPerformance,
    createDoctor,
    updateDoctor,
    searchPatients,
    getPendingReviews,
    createDoctorReview,
    getReviewByAnalysis,
    getReviewsByDoctor,
    approveReview,
    rejectReview,
    getReportsByDoctor,
    createMedicalReport,
    getConversationsByDoctor,
    getAnalysis,
    getPatientAnalyses,
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
  };
})();
