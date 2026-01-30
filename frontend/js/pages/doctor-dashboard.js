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
    if (!list.length) {
      pendingList.innerHTML = '<p class="text-muted mb-0">Không có kết quả AI nào chờ duyệt.</p>';
      return;
    }
    var html = '<ul class="list-group list-group-flush">';
    list.slice(0, 5).forEach(function (a) {
      var completed = a.completed_at ? new Date(a.completed_at).toLocaleDateString('vi-VN') : '-';
      html += '<li class="list-group-item d-flex justify-content-between align-items-center">' +
        '<span>Phân tích #' + (a.analysis_id || a.id) + ' (Ảnh #' + (a.image_id || '-') + ') - ' + completed + '</span>' +
        '<a href="reviews.html?analysis_id=' + (a.analysis_id || a.id) + '" class="btn btn-sm btn-outline-primary">Duyệt</a></li>';
    });
    html += '</ul>';
    pendingList.innerHTML = html;
  }

  function load() {
    if (!accountId) {
      showError('Không tìm thấy thông tin tài khoản.');
      return;
    }
    showError('');
    pendingList.innerHTML = 'Đang tải...';

    window.AuraAPI.getDoctorByAccount(accountId)
      .then(function (doctor) {
        if (!doctor || !doctor.doctor_id) {
          showError('Bạn chưa có hồ sơ bác sĩ. Vui lòng cập nhật <a href="profile.html">Hồ sơ</a>.');
          setStat(statPatients, 0);
          setStat(statReviews, 0);
          setStat(statReports, 0);
          renderPending({ pending_analyses: [] });
          return null;
        }
        doctorId = doctor.doctor_id;
        return Promise.all([
          window.AuraAPI.getDoctorPerformance(doctorId),
          window.AuraAPI.getPendingReviews(),
          window.AuraAPI.getReportsByDoctor(doctorId)
        ]);
      })
      .then(function (results) {
        if (!results) return;
        var perf = results[0];
        var pendingData = results[1];
        var reportsData = results[2];

        setStat(statPatients, (perf && perf.unique_patients != null) ? perf.unique_patients : '-');
        setStat(statReviews, (perf && perf.total_reviews != null) ? perf.total_reviews : '-');
        var reports = (reportsData && reportsData.reports) || [];
        setStat(statReports, (reportsData && reportsData.count != null) ? reportsData.count : reports.length);
        renderPending(pendingData);
      })
      .catch(function (err) {
        showError(err.message || 'Tải dữ liệu thất bại.');
        setStat(statPatients, '-');
        setStat(statReviews, '-');
        setStat(statReports, '-');
        pendingList.innerHTML = '<p class="text-muted mb-0">Không tải được dữ liệu.</p>';
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
