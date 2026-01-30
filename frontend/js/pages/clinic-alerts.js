/**
 * AURA - Clinic Alerts
 * GET /api/clinics/:id/high-risk-alerts?risk_level=high|critical
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var loading = document.getElementById('loading');
  var content = document.getElementById('content');
  var tbody = document.getElementById('tbody');
  var summary = document.getElementById('summary');
  var empty = document.getElementById('empty');
  var riskLevel = document.getElementById('riskLevel');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!clinicId) { showError('Bạn chưa được gán phòng khám.'); return; }
    showError('');
    var level = riskLevel && riskLevel.value ? riskLevel.value : 'high';
    loading.classList.remove('d-none');
    content.classList.add('d-none');
    empty.classList.add('d-none');
    window.AuraAPI.getHighRiskAlerts(clinicId, level)
      .then(function (data) {
        loading.classList.add('d-none');
        var list = (data && data.alerts) || [];
        var count = (data && data.count != null) ? data.count : list.length;
        if (!list.length) {
          empty.classList.remove('d-none');
          return;
        }
        content.classList.remove('d-none');
        summary.textContent = 'Tổng: ' + count + ' cảnh báo.';
        var html = '';
        list.forEach(function (a) {
          var latest = (a.latest_analysis && (a.latest_analysis.risk_level || a.latest_analysis.confidence_score != null)) ? (a.latest_analysis.risk_level || '-') + ' (' + (a.latest_analysis.confidence_score != null ? a.latest_analysis.confidence_score + '%' : '') + ')' : '-';
          var ts = a.alert_timestamp ? new Date(a.alert_timestamp).toLocaleString('vi-VN') : '-';
          html += '<tr><td>' + (a.patient_name || '') + ' (#' + (a.patient_id || '') + ')</td><td><span class="badge bg-danger">' + (a.risk_level || level) + '</span></td><td>' + latest + '</td><td>' + ts + '</td></tr>';
        });
        tbody.innerHTML = html;
      })
      .catch(function (err) {
        loading.classList.add('d-none');
        empty.classList.remove('d-none');
        empty.textContent = err.message || 'Không tải được.';
        showError(err.message || 'Tải thất bại.');
      });
  }

  if (riskLevel) riskLevel.addEventListener('change', load);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
