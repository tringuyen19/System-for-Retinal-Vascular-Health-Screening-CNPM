/**
 * AURA - FR-29: Cảnh báo bệnh nhân nguy cơ cao & xu hướng bất thường
 * GET /api/clinics/:id/high-risk-alerts, GET /api/clinics/:id/abnormal-trends
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

  var trendsLoading = document.getElementById('trendsLoading');
  var trendsContent = document.getElementById('trendsContent');
  var trendsSummary = document.getElementById('trendsSummary');
  var noTrends = document.getElementById('noTrends');
  var trendsData = document.getElementById('trendsData');
  var riskIncreasesTbody = document.getElementById('riskIncreasesTbody');
  var suddenSpikesTbody = document.getElementById('suddenSpikesTbody');
  var trendDays = document.getElementById('trendDays');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function loadHighRiskAlerts() {
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
          empty.textContent = 'Không có cảnh báo nguy cơ cao.';
          return;
        }
        content.classList.remove('d-none');
        empty.classList.add('d-none');
        summary.textContent = 'Tổng: ' + count + ' cảnh báo.';
        var html = '';
        list.forEach(function (a) {
          var latest = '-';
          if (a.latest_analysis) {
            var la = a.latest_analysis;
            var parts = [la.risk_level || ''];
            if (la.confidence_score != null) {
              var c = Number(la.confidence_score);
              parts.push((c <= 1 && c >= 0 ? (c * 100).toFixed(1) : c.toFixed(1)) + '%');
            }
            if (la.disease_type) parts.push(la.disease_type);
            latest = parts.filter(Boolean).join(' · ') || '-';
          }
          var analysisTime = (a.latest_analysis && a.latest_analysis.analysis_time)
            ? new Date(a.latest_analysis.analysis_time).toLocaleString('vi-VN') : '-';
          var riskBadge = (a.risk_level || '').toLowerCase() === 'critical' ? 'bg-danger' : 'bg-warning text-dark';
          html += '<tr>' +
            '<td>' + (a.patient_name || '-') + '</td>' +
            '<td><span class="badge ' + riskBadge + '">' + (a.risk_level || level) + '</span></td>' +
            '<td>' + latest + '</td>' +
            '<td class="small">' + analysisTime + '</td></tr>';
        });
        tbody.innerHTML = html;
      })
      .catch(function (err) {
        loading.classList.add('d-none');
        empty.classList.remove('d-none');
        empty.textContent = err.message || 'Không tải được cảnh báo.';
        showError(err.message || 'Tải thất bại.');
      });
  }

  function loadAbnormalTrends() {
    if (!clinicId) return;
    var days = trendDays && trendDays.value ? parseInt(trendDays.value, 10) : 30;
    if (trendsLoading) trendsLoading.classList.remove('d-none');
    if (trendsContent) trendsContent.classList.add('d-none');
    window.AuraAPI.getClinicAbnormalTrends(clinicId, days)
      .then(function (data) {
        if (trendsLoading) trendsLoading.classList.add('d-none');
        if (!trendsContent) return;
        trendsContent.classList.remove('d-none');
        var totalPatients = (data && data.total_patients_analyzed != null) ? data.total_patients_analyzed : 0;
        var periodDays = (data && data.period_days != null) ? data.period_days : days;
        var trends = (data && data.abnormal_trends) || {};
        var riskIncreases = trends.risk_increases || [];
        var suddenSpikes = trends.sudden_spikes || [];
        var totalCases = trends.total_abnormal_cases != null ? trends.total_abnormal_cases : (riskIncreases.length + suddenSpikes.length);

        if (trendsSummary) {
          trendsSummary.textContent = 'Đã phân tích ' + totalPatients + ' bệnh nhân trong ' + periodDays + ' ngày qua. ' +
            (totalCases > 0 ? 'Phát hiện ' + totalCases + ' trường hợp bất thường.' : 'Không phát hiện xu hướng bất thường.');
        }

        if (totalCases === 0) {
          if (noTrends) noTrends.classList.remove('d-none');
          if (trendsData) trendsData.classList.add('d-none');
          if (riskIncreasesTbody) riskIncreasesTbody.innerHTML = '';
          if (suddenSpikesTbody) suddenSpikesTbody.innerHTML = '';
          return;
        }

        if (noTrends) noTrends.classList.add('d-none');
        if (trendsData) trendsData.classList.remove('d-none');

        var riHtml = riskIncreases.map(function (r) {
          return '<tr>' +
            '<td>' + (r.patient_name || '-') + '</td>' +
            '<td><span class="badge bg-secondary">' + (r.from_risk || '-') + '</span></td>' +
            '<td><span class="badge bg-warning text-dark">' + (r.to_risk || '-') + '</span></td>' +
            '<td>' + (r.increase != null ? '+' + r.increase : '-') + '</td></tr>';
        }).join('');
        if (riskIncreasesTbody) riskIncreasesTbody.innerHTML = riHtml || '<tr><td colspan="4" class="text-muted">Không có</td></tr>';

        var ssHtml = suddenSpikes.map(function (s) {
          var conf = s.confidence != null ? (Number(s.confidence) <= 1 ? (Number(s.confidence) * 100).toFixed(1) + '%' : s.confidence + '%') : '-';
          return '<tr>' +
            '<td>' + (s.patient_name || '-') + '</td>' +
            '<td class="small">' + (s.date || '-') + '</td>' +
            '<td><span class="badge bg-secondary">' + (s.from_risk || '-') + '</span></td>' +
            '<td><span class="badge bg-danger">' + (s.to_risk || '-') + '</span></td>' +
            '<td>' + conf + '</td></tr>';
        }).join('');
        if (suddenSpikesTbody) suddenSpikesTbody.innerHTML = ssHtml || '<tr><td colspan="5" class="text-muted">Không có</td></tr>';
      })
      .catch(function (err) {
        if (trendsLoading) trendsLoading.classList.add('d-none');
        if (trendsContent) trendsContent.classList.remove('d-none');
        if (trendsSummary) trendsSummary.textContent = err.message || 'Không tải được xu hướng.';
        if (noTrends) { noTrends.classList.remove('d-none'); noTrends.textContent = err.message || 'Lỗi tải dữ liệu.'; }
        if (trendsData) trendsData.classList.add('d-none');
      });
  }

  function load() {
    loadHighRiskAlerts();
    loadAbnormalTrends();
  }

  if (riskLevel) riskLevel.addEventListener('change', loadHighRiskAlerts);
  if (trendDays) trendDays.addEventListener('change', loadAbnormalTrends);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
