/**
 * AURA - Doctor Dashboard
 * Stats (patients, reviews, reports), pending reviews list, quick actions
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var doctorId = null;

  var statPatients = document.getElementById('statPatients');
  var statReviews = document.getElementById('statReviews');
  var statReports = document.getElementById('statReports');
  var statPending = document.getElementById('statPending');
  var pendingBadge = document.getElementById('pendingBadge');
  var pendingList = document.getElementById('pendingList');
  var analysisResultsList = document.getElementById('analysisResultsList');
  var dashboardError = document.getElementById('dashboardError');

  function showError(msg) {
    if (!dashboardError) return;
    dashboardError.textContent = msg || '';
    dashboardError.classList.toggle('d-none', !msg);
  }

  function setStat(el, value) {
    if (el) el.textContent = value != null ? value : '-';
  }

  function setPendingCount(count) {
    var n = (count != null && count !== '-') ? (typeof count === 'number' ? count : parseInt(count, 10)) : null;
    var num = (n !== null && !isNaN(n)) ? n : 0;
    if (statPending) statPending.textContent = (count === '-' || count == null) ? '-' : num;
    if (pendingBadge) pendingBadge.textContent = num;
  }

  function renderPending(pendingData) {
    // Giống trang reviews: hỗ trợ response bọc trong data (data.data) và luôn đếm từ mảng
    var payload = (pendingData && pendingData.data !== undefined) ? pendingData.data : (pendingData || {});
    var pendingListItems = (payload.pending_analyses && Array.isArray(payload.pending_analyses)) ? payload.pending_analyses : [];
    var needRevListRaw = (payload.need_revision_reviews && Array.isArray(payload.need_revision_reviews)) ? payload.need_revision_reviews : [];
    // Chỉ "Cần duyệt": chưa approved (pending, rejected, needs_revision). Loại bỏ approved.
    var needRevList = needRevListRaw.filter(function (r) {
      return (r.validation_status || '').toLowerCase() !== 'approved';
    });
    var totalItems = pendingListItems.length + needRevList.length;
    setPendingCount(totalItems);

    if (!pendingList) return;
    if (totalItems === 0) {
      pendingList.innerHTML = '<p class="text-muted mb-0">Không có kết quả AI nào chờ duyệt.</p>';
      return;
    }
    var html = '<ul class="list-group list-group-flush">';
    var combined = [];
    pendingListItems.forEach(function (a) {
      combined.push({ analysis_id: a.analysis_id || a.id, image_id: a.image_id, dateStr: a.completed_at ? new Date(a.completed_at).toLocaleDateString('vi-VN') : '-', label: 'Chưa duyệt' });
    });
    needRevList.forEach(function (r) {
      var d = (r.reviewed_at || r.completed_at) ? new Date(r.reviewed_at || r.completed_at).toLocaleDateString('vi-VN') : '-';
      combined.push({ analysis_id: r.analysis_id || r.id, image_id: r.image_id, dateStr: d, label: r.validation_status === 'rejected' ? 'Từ chối' : r.validation_status === 'needs_revision' ? 'Cần chỉnh sửa' : 'Chờ duyệt' });
    });
    combined.slice(0, 5).forEach(function (item) {
      html += '<li class="list-group-item d-flex justify-content-between align-items-center">' +
        '<span>Phân tích ' + item.analysis_id + ' (Ảnh ' + (item.image_id || '-') + ') - ' + item.dateStr + ' <span class="badge bg-secondary ms-1">' + item.label + '</span></span>' +
        '<a href="reviews.html?analysis_id=' + item.analysis_id + '" class="btn btn-sm btn-outline-primary">Duyệt</a></li>';
    });
    html += '</ul>';
    pendingList.innerHTML = html;
  }

  /** Render danh sách kết quả AI theo result_id của các bệnh nhân thuộc doctor (GET /api/ai-results). */
  function renderAnalysisResults(resultsPayload) {
    if (!analysisResultsList) return;
    var list = (resultsPayload && resultsPayload.results && Array.isArray(resultsPayload.results)) ? resultsPayload.results : [];
    if (!list.length) {
      analysisResultsList.innerHTML = '<p class="text-muted mb-0">Chưa có kết quả phân tích nào của bệnh nhân bạn. Xem chi tiết tại <a href="analysis-results.html">Kết quả & chú thích AI</a>.</p>';
      return;
    }
    var html = '<ul class="list-group list-group-flush">';
    list.slice(0, 5).forEach(function (r) {
      var analysisId = r.analysis_id;
      var patientName = (r.patient_name || '').trim() || 'Bệnh nhân';
      html += '<li class="list-group-item d-flex justify-content-between align-items-center">' +
        '<span><strong>' + patientName + '</strong></span>' +
        '<a href="analysis-results.html?analysis_id=' + (analysisId || '') + '" class="btn btn-sm btn-outline-primary">Xem kết quả & chú thích</a></li>';
    });
    html += '</ul>';
    analysisResultsList.innerHTML = html;
  }

  /** Luôn gọi GET /api/doctor-reviews/pending và cập nhật thẻ "Cần duyệt" + danh sách (độc lập với các API khác). */
  function loadPendingFromApi() {
    window.AuraAPI.getPendingReviews()
      .then(function (data) {
        var payload = (data && data.data !== undefined) ? data.data : (data || {});
        renderPending(payload);
      })
      .catch(function () {
        setPendingCount(0);
        if (pendingList) pendingList.innerHTML = '<p class="text-muted mb-0">Không tải được danh sách cần duyệt.</p>';
      });
  }

  function load() {
    if (!accountId) {
      showError('Không tìm thấy thông tin tài khoản.');
      return;
    }
    showError('');
    if (pendingList) pendingList.innerHTML = 'Đang tải...';
    if (analysisResultsList) analysisResultsList.innerHTML = 'Đang tải...';

    // Luôn gọi GET /api/doctor-reviews/pending ngay để hiển thị số "Cần duyệt" (không phụ thuộc Promise.all)
    loadPendingFromApi();

    window.AuraAPI.getDoctorByAccount(accountId)
      .then(function (doctor) {
        if (!doctor || !doctor.doctor_id) {
          // Chưa có profile, redirect đến trang setup
          window.location.href = 'setup-profile.html';
          return;
        }
        doctorId = doctor.doctor_id;
        return Promise.all([
          window.AuraAPI.getDoctorPerformance(doctorId),
          window.AuraAPI.getReportsByDoctor(doctorId),
          window.AuraAPI.getAllResults()
        ]);
      })
      .then(function (results) {
        if (!results) return;
        var perf = results[0];
        var reportsData = results[1];
        var resultsPayload = results[2];

        setStat(statPatients, (perf && perf.unique_patients != null) ? perf.unique_patients : '-');
        // Chỉ tính "Đã duyệt" khi validation_status = approved
        setStat(statReviews, (perf && perf.approved_reviews != null) ? perf.approved_reviews : '-');
        var reports = (reportsData && reportsData.reports) || [];
        setStat(statReports, (reportsData && reportsData.count != null) ? reportsData.count : reports.length);
        renderAnalysisResults(resultsPayload);
      })
      .catch(function (err) {
        showError(err.message || 'Tải dữ liệu thất bại.');
        setStat(statPatients, '-');
        setStat(statReviews, '-');
        setStat(statReports, '-');
        if (pendingList) pendingList.innerHTML = '<p class="text-muted mb-0">Không tải được dữ liệu.</p>';
        if (analysisResultsList) analysisResultsList.innerHTML = '<p class="text-muted mb-0">Không tải được dữ liệu.</p>';
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
