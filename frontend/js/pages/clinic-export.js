/**
 * AURA - Clinic Export
 * GET /api/clinics/:id/export-statistics?format=json|csv_data
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var exportFormat = document.getElementById('exportFormat');
  var btnExport = document.getElementById('btnExport');
  var previewContent = document.getElementById('previewContent');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!clinicId) { showError('Bạn chưa được gán phòng khám.'); return; }
    showError('');
    var format = (exportFormat && exportFormat.value) || 'json';
    btnExport.disabled = true;
    previewContent.textContent = 'Đang tải...';
    window.AuraAPI.exportClinicStatistics(clinicId, format)
      .then(function (data) {
        btnExport.disabled = false;
        if (format === 'csv_data' && data && data.csv_format && data.csv_format.length) {
          previewContent.innerHTML = '<pre class="mb-0 small">' + data.csv_format.map(function (row) { return row.join(', '); }).join('\n') + '</pre>';
        } else {
          previewContent.innerHTML = '<pre class="mb-0 small">' + (typeof data === 'object' ? JSON.stringify(data, null, 2) : data) + '</pre>';
        }
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã tải thống kê.', 'success');
      })
      .catch(function (err) {
        btnExport.disabled = false;
        previewContent.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được.') + '</p>';
        showError(err.message || 'Xuất thất bại.');
      });
  }

  if (btnExport) btnExport.addEventListener('click', load);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () {
    if (!clinicId) showError('Bạn chưa được gán phòng khám.');
  });
})();
