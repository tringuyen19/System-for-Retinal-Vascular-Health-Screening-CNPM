/**
 * AURA - FR-25: Theo dõi toàn bộ báo cáo phân tích và dữ liệu rủi ro tổng hợp
 * Risk aggregation, reports summary, abnormal trends
 */
(function () {
    'use strict';
  
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;
  
    var user = window.AuraAuth.getUser();
    var clinicId = user && user.clinic_id;
  
    var pageError = document.getElementById('pageError');
    var overviewAnalyses = document.getElementById('overviewAnalyses');
    var overviewReports = document.getElementById('overviewReports');
    var overviewHighRisk = document.getElementById('overviewHighRisk');
    var overviewAbnormal = document.getElementById('overviewAbnormal');
    var barLow = document.getElementById('barLow');
    var barMedium = document.getElementById('barMedium');
    var barHigh = document.getElementById('barHigh');
    var barCritical = document.getElementById('barCritical');
    var highRiskTableBody = document.getElementById('highRiskTableBody');
    var filterStartDate = document.getElementById('filterStartDate');
    var filterEndDate = document.getElementById('filterEndDate');
    var btnFilterReports = document.getElementById('btnFilterReports');
    var summaryTotalReports = document.getElementById('summaryTotalReports');
    var summaryUniquePatients = document.getElementById('summaryUniquePatients');
    var summaryUniqueDoctors = document.getElementById('summaryUniqueDoctors');
    var reportsByMonthContent = document.getElementById('reportsByMonthContent');
    var trendDays = document.getElementById('trendDays');
    var trendPatientsAnalyzed = document.getElementById('trendPatientsAnalyzed');
    var trendDetected = document.getElementById('trendDetected');
    var riskIncreasesBody = document.getElementById('riskIncreasesBody');
    var suddenSpikesBody = document.getElementById('suddenSpikesBody');
  
    function showError(msg) {
      if (!pageError) return;
      pageError.textContent = msg || '';
      pageError.classList.toggle('d-none', !msg);
    }
  
    function riskLabel(level) {
      var m = { low: 'Thấp', medium: 'Trung bình', high: 'Cao', critical: 'Nghiêm trọng' };
      return m[(level || '').toLowerCase()] || level || '-';
    }
  
    function setOverview(riskData, reportsData, trendData) {
      if (overviewAnalyses) overviewAnalyses.textContent = (riskData && riskData.total_analyses != null) ? riskData.total_analyses : '-';
      if (overviewReports) overviewReports.textContent = (reportsData && reportsData.total_reports != null) ? reportsData.total_reports : '-';
      if (overviewHighRisk) overviewHighRisk.textContent = (riskData && riskData.high_risk_patients_count != null) ? riskData.high_risk_patients_count : '-';
      var abnormalCount = 0;
      if (trendData && trendData.summary) {
        abnormalCount = (trendData.summary.risk_increases_count || 0) + (trendData.summary.sudden_spikes_count || 0);
      }
      if (overviewAbnormal) overviewAbnormal.textContent = abnormalCount;
    }
  
    function renderRiskBars(dist, total) {
      if (!dist || total === 0) total = 1;
      var low = dist.low != null ? dist.low : 0;
      var medium = dist.medium != null ? dist.medium : 0;
      var high = dist.high != null ? dist.high : 0;
      var critical = dist.critical != null ? dist.critical : 0;
      if (barLow) { barLow.style.width = (low / total * 100) + '%'; barLow.textContent = low; }
      if (barMedium) { barMedium.style.width = (medium / total * 100) + '%'; barMedium.textContent = medium; }
      if (barHigh) { barHigh.style.width = (high / total * 100) + '%'; barHigh.textContent = high; }
      if (barCritical) { barCritical.style.width = (critical / total * 100) + '%'; barCritical.textContent = critical; }
    }
  
    function renderHighRiskTable(list) {
      if (!highRiskTableBody) return;
      list = list || [];
      if (list.length === 0) {
        highRiskTableBody.innerHTML = '<tr><td colspan="3" class="text-muted">Không có bệnh nhân nguy cơ cao trong danh sách.</td></tr>';
        return;
      }
      highRiskTableBody.innerHTML = list.map(function (p) {
        return '<tr><td>' + (p.patient_id || '-') + '</td><td>' + (p.patient_name || '-') + '</td><td><span class="badge bg-danger">' + riskLabel(p.risk_level) + '</span></td></tr>';
      }).join('');
    }
  
    function loadRiskAggregation() {
      if (!clinicId) return Promise.resolve(null);
      return window.AuraAPI.getClinicRiskAggregation(clinicId)
        .then(function (data) {
          var dist = (data && data.risk_distribution) || {};
          var total = (dist.low || 0) + (dist.medium || 0) + (dist.high || 0) + (dist.critical || 0);
          renderRiskBars(dist, total);
          renderHighRiskTable(data && data.high_risk_patients ? data.high_risk_patients : []);
          return data;
        })
        .catch(function (err) {
          if (highRiskTableBody) highRiskTableBody.innerHTML = '<tr><td colspan="3" class="text-danger">' + (err.message || 'Không tải được.') + '</td></tr>';
          return null;
        });
    }
  
    function loadReportsSummary(startDate, endDate) {
      if (!clinicId) return Promise.resolve(null);
      return window.AuraAPI.getClinicReportsSummary(clinicId, startDate, endDate)
        .then(function (data) {
          if (summaryTotalReports) summaryTotalReports.textContent = (data && data.total_reports != null) ? data.total_reports : '-';
          if (summaryUniquePatients) summaryUniquePatients.textContent = (data && data.unique_patients != null) ? data.unique_patients : '-';
          if (summaryUniqueDoctors) summaryUniqueDoctors.textContent = (data && data.unique_doctors != null) ? data.unique_doctors : '-';
          if (overviewReports && data && data.total_reports != null) overviewReports.textContent = data.total_reports;
          var byMonth = (data && data.reports_by_month) || {};
          var months = Object.keys(byMonth).sort().reverse();
          if (reportsByMonthContent) {
            if (months.length === 0) {
              reportsByMonthContent.innerHTML = '<p class="text-muted mb-0">Chưa có dữ liệu theo tháng.</p>';
            } else {
              reportsByMonthContent.innerHTML = '<table class="table table-sm mb-0"><tbody>' +
                months.map(function (m) { return '<tr><td>' + m + '</td><td>' + byMonth[m] + ' báo cáo</td></tr>'; }).join('') +
                '</tbody></table>';
            }
          }
          return data;
        })
        .catch(function (err) {
          if (summaryTotalReports) summaryTotalReports.textContent = '-';
          if (reportsByMonthContent) reportsByMonthContent.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được.') + '</p>';
          return null;
        });
    }
  
    function loadAbnormalTrends(days) {
      if (!clinicId) return Promise.resolve(null);
      days = days || 30;
      return window.AuraAPI.getClinicAbnormalTrends(clinicId, days)
        .then(function (data) {
          if (trendPatientsAnalyzed) trendPatientsAnalyzed.textContent = (data && data.total_patients_analyzed != null) ? data.total_patients_analyzed : '-';
          if (trendDetected) trendDetected.textContent = (data && data.abnormal_trends_detected) ? 'Có' : 'Không';
          var trends = (data && data.abnormal_trends) || {};
          var increases = trends.risk_increases || [];
          var spikes = trends.sudden_spikes || [];
          if (riskIncreasesBody) {
            riskIncreasesBody.innerHTML = increases.length ? increases.map(function (x) {
              return '<tr><td>' + (x.patient_name || '#' + x.patient_id) + '</td><td>' + riskLabel(x.from_risk) + ' → ' + riskLabel(x.to_risk) + '</td></tr>';
            }).join('') : '<tr><td colspan="2" class="text-muted">Không có.</td></tr>';
          }
          if (suddenSpikesBody) {
            suddenSpikesBody.innerHTML = spikes.length ? spikes.map(function (x) {
              return '<tr><td>' + (x.patient_name || '#' + x.patient_id) + '</td><td>' + (x.date || '-') + '</td><td>' + riskLabel(x.to_risk) + '</td></tr>';
            }).join('') : '<tr><td colspan="3" class="text-muted">Không có.</td></tr>';
          }
          return data;
        })
        .catch(function (err) {
          if (trendPatientsAnalyzed) trendPatientsAnalyzed.textContent = '-';
          if (trendDetected) trendDetected.textContent = '-';
          if (riskIncreasesBody) riskIncreasesBody.innerHTML = '<tr><td colspan="2" class="text-danger">' + (err.message || 'Không tải được.') + '</td></tr>';
          if (suddenSpikesBody) suddenSpikesBody.innerHTML = '<tr><td colspan="3" class="text-danger">' + (err.message || 'Không tải được.') + '</td></tr>';
          return null;
        });
    }
  
    function loadAll() {
      if (!clinicId) {
        showError('Bạn chưa được gán phòng khám.');
        return;
      }
      showError('');
  
      var startDate = filterStartDate && filterStartDate.value ? filterStartDate.value : null;
      var endDate = filterEndDate && filterEndDate.value ? filterEndDate.value : null;
      var days = trendDays && trendDays.value ? parseInt(trendDays.value, 10) : 30;
  
      Promise.all([
        loadRiskAggregation(),
        loadReportsSummary(startDate, endDate),
        loadAbnormalTrends(days)
      ]).then(function (results) {
        var riskData = results[0];
        var reportsData = results[1];
        var trendData = results[2];
        setOverview(riskData, reportsData, trendData);
      });
    }
  
    if (btnFilterReports) btnFilterReports.addEventListener('click', function () {
      loadReportsSummary(filterStartDate && filterStartDate.value, filterEndDate && filterEndDate.value)
        .then(function (data) {
          if (overviewReports && data && data.total_reports != null) overviewReports.textContent = data.total_reports;
        });
    });
    if (trendDays) trendDays.addEventListener('change', function () { loadAll(); });
  
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', loadAll);
    else loadAll();
  })();
  