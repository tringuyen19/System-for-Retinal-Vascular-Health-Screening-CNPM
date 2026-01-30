/**
 * AURA - Clinic Analytics
 * Risk aggregation + Abnormal trends
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var riskContent = document.getElementById('riskContent');
  var trendContent = document.getElementById('trendContent');
  var trendDays = document.getElementById('trendDays');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function loadRisk() {
    if (!clinicId) return;
    window.AuraAPI.getClinicRiskAggregation(clinicId)
      .then(function (data) {
        var dist = (data && data.risk_distribution) || {};
        riskContent.innerHTML =
          '<p class="mb-1"><strong>Bệnh nhân:</strong> ' + ((data && data.total_patients != null) ? data.total_patients : '-') + '</p>' +
          '<p class="mb-1"><strong>Phân tích:</strong> ' + ((data && data.total_analyses != null) ? data.total_analyses : '-') + '</p>' +
          '<p class="mb-2"><strong>Nguy cơ cao:</strong> ' + ((data && data.high_risk_patients_count != null) ? data.high_risk_patients_count : '-') + '</p>' +
          '<ul class="list-unstyled mb-0">' +
          '<li>Thấp: ' + (dist.low != null ? dist.low : 0) + '</li>' +
          '<li>Trung bình: ' + (dist.medium != null ? dist.medium : 0) + '</li>' +
          '<li>Cao: ' + (dist.high != null ? dist.high : 0) + '</li>' +
          '<li>Nghiêm trọng: ' + (dist.critical != null ? dist.critical : 0) + '</li>' +
          '</ul>';
      })
      .catch(function (err) {
        riskContent.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được.') + '</p>';
      });
  }

  function loadTrends() {
    if (!clinicId) return;
    var days = trendDays && trendDays.value ? parseInt(trendDays.value, 10) : 30;
    window.AuraAPI.getClinicAbnormalTrends(clinicId, days)
      .then(function (data) {
        var abnormal = (data && data.abnormal_trends_detected) ? 'Có' : 'Không';
        var trends = (data && data.abnormal_trends) || {};
        var summary = (data && data.summary) || {};
        trendContent.innerHTML =
          '<p class="mb-1"><strong>Phát hiện bất thường:</strong> ' + abnormal + '</p>' +
          '<p class="mb-1"><strong>Bệnh nhân phân tích:</strong> ' + ((data && data.total_patients_analyzed != null) ? data.total_patients_analyzed : '-') + '</p>' +
          '<p class="mb-1"><strong>Tăng rủi ro:</strong> ' + (summary.risk_increases_count != null ? summary.risk_increases_count : 0) + '</p>' +
          '<p class="mb-0"><strong>Đột biến:</strong> ' + (summary.sudden_spikes_count != null ? summary.sudden_spikes_count : 0) + '</p>';
      })
      .catch(function (err) {
        trendContent.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được.') + '</p>';
      });
  }

  function load() {
    if (!clinicId) {
      showError('Bạn chưa được gán phòng khám.');
      return;
    }
    showError('');
    loadRisk();
    loadTrends();
  }

  if (trendDays) trendDays.addEventListener('change', loadTrends);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
