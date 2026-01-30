/**
 * AURA - Patient Reports
 * List medical reports, view detail, download
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireLogin || !window.AuraAuth.requireLogin()) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var patientId = null;
  var reportsError = document.getElementById('reportsError');
  var reportsList = document.getElementById('reportsList');

  function showError(msg) {
    if (!reportsError) return;
    reportsError.textContent = msg || '';
    reportsError.classList.toggle('d-none', !msg);
  }

  function getPatient() {
    if (!accountId) return Promise.reject(new Error('Không tìm thấy tài khoản.'));
    return window.AuraAPI.getPatientByAccount(accountId).then(function (p) {
      if (!p || !p.patient_id) return Promise.reject(new Error('Chưa có hồ sơ bệnh nhân.'));
      patientId = p.patient_id;
      return patientId;
    });
  }

  getPatient()
    .then(function () { return window.AuraAPI.getReportsByPatient(patientId, 50); })
    .then(function (data) {
      var reports = (data && data.reports) || [];
      showError('');
      if (!reportsList) return;
      if (!reports.length) {
        reportsList.innerHTML = '<p class="text-muted">Chưa có báo cáo nào.</p>';
        return;
      }
      reportsList.innerHTML = '<div class="list-group">' + reports.map(function (r) {
        var date = r.created_at ? r.created_at.slice(0, 10) : '-';
        var url = r.report_url ? '<a href="' + r.report_url + '" target="_blank" class="btn btn-sm btn-outline-primary">Xem / Tải PDF</a>' : '<span class="text-muted small">Chưa có file</span>';
        return '<div class="list-group-item d-flex justify-content-between align-items-center">' +
          '<div><strong>Báo cáo #' + (r.report_id || r.id) + '</strong> – Phân tích #' + (r.analysis_id || '-') + ' – ' + date + '</div>' +
          '<div>' + url + '</div></div>';
      }).join('') + '</div>';
    })
    .catch(function (err) {
      showError(err.message || 'Không tải được danh sách báo cáo.');
      if (reportsList) reportsList.innerHTML = '<p class="text-muted">Không tải được dữ liệu.</p>';
    });
})();
