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

  function renderPending(pendingData) {
    var list = (pendingData && pendingData.pending_analyses) || [];
    if (!pendingList) return;
    if (!list.length) {
      pendingList.innerHTML = '<p class="text-muted mb-0">Không có kết quả AI nào chờ duyệt.</p>';
      return;
    }
    var html = '<ul class="list-group list-group-flush">';
    list.slice(0, 5).forEach(function (a) {
      var completed = a.completed_at ? new Date(a.completed_at).toLocaleDateString('vi-VN') : '-';
      html += '<li class="list-group-item d-flex justify-content-between align-items-center">' +
        '<span>Phân tích' + (a.analysis_id || a.id) + ' (Ảnh' + (a.image_id || '-') + ') - ' + completed + '</span>' +
        '<a href="reviews.html?analysis_id=' + (a.analysis_id || a.id) + '" class="btn btn-sm btn-outline-primary">Duyệt</a></li>';
    });
    html += '</ul>';
    pendingList.innerHTML = html;
  }

  function renderAnalysisResults(analyses) {
    if (!analysisResultsList) return;
    var list = (analyses && analyses.analyses) || analyses || [];
    if (!list.length) {
      analysisResultsList.innerHTML = '<p class="text-muted mb-0">Chưa có kết quả phân tích nào. Xem chi tiết tại <a href="analysis-results.html">Kết quả & chú thích AI</a>.</p>';
      return;
    }
    var html = '<ul class="list-group list-group-flush">';
    list.slice(0, 5).forEach(function (a) {
      var aid = a.analysis_id || a.id;
      var dateStr = a.analysis_time ? new Date(a.analysis_time).toLocaleDateString('vi-VN') : '-';
      html += '<li class="list-group-item d-flex justify-content-between align-items-center">' +
        '<span>Phân tích ' + aid + ' - ' + dateStr + '</span>' +
        '<a href="analysis-results.html" class="btn btn-sm btn-outline-primary">Xem kết quả & chú thích</a></li>';
    });
    html += '</ul>';
    analysisResultsList.innerHTML = html;
  }

  function load() {
    if (!accountId) {
      showError('Không tìm thấy thông tin tài khoản.');
      return;
    }
    showError('');
    if (pendingList) pendingList.innerHTML = 'Đang tải...';
    if (analysisResultsList) analysisResultsList.innerHTML = 'Đang tải...';

    window.AuraAPI.getDoctorByAccount(accountId)
      .then(function (doctor) {
        if (!doctor || !doctor.doctor_id) {
          showError('Bạn chưa có hồ sơ bác sĩ. Vui lòng cập nhật <a href="profile.html">Hồ sơ</a>.');
          setStat(statPatients, 0);
          setStat(statReviews, 0);
          setStat(statReports, 0);
          renderPending({ pending_analyses: [] });
          renderAnalysisResults([]);
          return null;
        }
        doctorId = doctor.doctor_id;
        return Promise.all([
          window.AuraAPI.getDoctorPerformance(doctorId),
          window.AuraAPI.getPendingReviews(),
          window.AuraAPI.getReportsByDoctor(doctorId),
          window.AuraAPI.getCompletedAnalyses()
        ]);
      })
      .then(function (results) {
        if (!results) return;
        var perf = results[0];
        var pendingData = results[1];
        var reportsData = results[2];
        var completedData = results[3];

        setStat(statPatients, (perf && perf.unique_patients != null) ? perf.unique_patients : '-');
        setStat(statReviews, (perf && perf.total_reviews != null) ? perf.total_reviews : '-');
        var reports = (reportsData && reportsData.reports) || [];
        setStat(statReports, (reportsData && reportsData.count != null) ? reportsData.count : reports.length);
        renderPending(pendingData);
        renderAnalysisResults(completedData);
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
