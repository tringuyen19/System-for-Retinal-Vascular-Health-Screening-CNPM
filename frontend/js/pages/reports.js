/**
 * AURA - Patient Reports
 * List medical reports, view detail, download
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Patient')) return;

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

  function escapeHtml(s) {
    if (!s) return '';
    var div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function onExportPdfClick(e) {
    var btn = e.target && e.target.closest && e.target.closest('.js-export-report-pdf');
    if (!btn) return;
    var reportId = btn.getAttribute('data-report-id');
    if (!reportId || !window.AuraAPI || !window.AuraAPI.exportMedicalReportPdf) return;
    btn.disabled = true;
    window.AuraAPI.exportMedicalReportPdf(reportId)
      .then(function () {
        if (window.AuraAlert && window.AuraAlert.toast) {
          window.AuraAlert.toast('Đã tải PDF.', 'success');
        }
      })
      .catch(function (err) {
        showError(err.message || 'Không tải được PDF.');
      })
      .finally(function () {
        btn.disabled = false;
      });
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
        var reportId = r.report_id || r.id;
        var date = r.created_at ? r.created_at.slice(0, 10) : '-';
        var pdfBtn = '<button type="button" class="btn btn-sm btn-outline-primary js-export-report-pdf" data-report-id="' + reportId + '">Xem / Tải PDF</button>';
        var notes = (r.medical_notes || '').trim();
        var diagnosis = (r.diagnosis || '').trim();
        var recommendations = (r.treatment_recommendations || '').trim();
        var hasContent = notes || diagnosis || recommendations;
        var contentBlock = hasContent ? '<div class="mt-2 small text-muted border-top pt-2">' +
          (notes ? '<div><strong>Ghi chú:</strong> ' + escapeHtml(notes) + '</div>' : '') +
          (diagnosis ? '<div><strong>Chẩn đoán:</strong> ' + escapeHtml(diagnosis) + '</div>' : '') +
          (recommendations ? '<div><strong>Khuyến nghị điều trị:</strong> ' + escapeHtml(recommendations) + '</div>' : '') +
          '</div>' : '';
        return '<div class="list-group-item">' +
          '<div class="d-flex justify-content-between align-items-center">' +
          '<div><strong>Báo cáo ' + reportId + '</strong> - ' + date + '</div>' +
          '<div>' + pdfBtn + '</div></div>' +
          contentBlock + '</div>';
      }).join('') + '</div>';
    })
    .catch(function (err) {
      showError(err.message || 'Không tải được danh sách báo cáo.');
      if (reportsList) reportsList.innerHTML = '<p class="text-muted">Không tải được dữ liệu.</p>';
    });

  if (reportsList) {
    reportsList.addEventListener('click', onExportPdfClick);
  }
})();
