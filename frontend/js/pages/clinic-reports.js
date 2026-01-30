/**
 * AURA - Clinic Reports
 * Reports summary + Screening report
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var summaryContent = document.getElementById('summaryContent');
  var screeningContent = document.getElementById('screeningContent');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!clinicId) { showError('Bạn chưa được gán phòng khám.'); return; }
    showError('');
    window.AuraAPI.getClinicReportsSummary(clinicId)
      .then(function (data) {
        summaryContent.innerHTML =
          '<p class="mb-1"><strong>Tổng báo cáo:</strong> ' + ((data && data.total_reports != null) ? data.total_reports : '-') + '</p>' +
          '<p class="mb-1"><strong>Bệnh nhân:</strong> ' + ((data && data.unique_patients != null) ? data.unique_patients : '-') + '</p>' +
          '<p class="mb-0"><strong>Bác sĩ:</strong> ' + ((data && data.unique_doctors != null) ? data.unique_doctors : '-') + '</p>';
      })
      .catch(function (err) {
        summaryContent.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được.') + '</p>';
      });
    window.AuraAPI.getClinicScreeningReport(clinicId)
      .then(function (data) {
        screeningContent.innerHTML =
          '<p class="mb-1"><strong>Chiến dịch:</strong> ' + ((data && data.campaign_name) || '-') + '</p>' +
          '<p class="mb-1"><strong>Phòng khám ID:</strong> ' + ((data && data.clinic_id != null) ? data.clinic_id : '-') + '</p>' +
          '<p class="mb-0"><strong>Giai đoạn:</strong> ' + (data && data.period ? (data.period.start_date || '') + ' → ' + (data.period.end_date || '') : '-') + '</p>';
      })
      .catch(function (err) {
        screeningContent.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được.') + '</p>';
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
