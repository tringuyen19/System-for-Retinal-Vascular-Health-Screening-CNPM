/**
 * AURA - Doctor: Patient history & trend (FR-17)
 * - Lịch sử phân tích: /api/ai-analysis/patient/:id (pagination)
 * - Xu hướng: /api/ai-analysis/patient/:id/trend?days=
 * - Tóm tắt kết quả AI: /api/ai-results/analysis/:analysis_id
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;

  var pageError = document.getElementById('pageError');
  var patientNameEl = document.getElementById('patientName');
  var patientMetaEl = document.getElementById('patientMeta');
  var trendLabelEl = document.getElementById('trendLabel');
  var trendHintEl = document.getElementById('trendHint');
  var trendChartWrap = document.getElementById('trendChartWrap');
  var riskDistribution = document.getElementById('riskDistribution');
  var trendDays = document.getElementById('trendDays');

  var historyLoading = document.getElementById('historyLoading');
  var historyEmpty = document.getElementById('historyEmpty');
  var historyTableWrap = document.getElementById('historyTableWrap');
  var historyBody = document.getElementById('historyBody');
  var btnLoadMore = document.getElementById('btnLoadMore');

  var patientId = null;
  var limit = 10;
  var offset = 0;
  var loadingHistory = false;
  var loadedAll = false;

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function qs(name) {
    var p = new URLSearchParams(window.location.search || '');
    return p.get(name);
  }

  function fmtDate(str) {
    if (!str) return '-';
    var d = new Date(str);
    return isNaN(d.getTime()) ? str : d.toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' });
  }

  function statusLabel(s) {
    var map = { completed: 'Hoàn thành', processing: 'Đang xử lý', pending: 'Chờ xử lý', failed: 'Thất bại' };
    return map[s] || s || '-';
  }

  function riskLabel(s) {
    var map = { low: 'Thấp', medium: 'Trung bình', high: 'Cao', critical: 'Rất cao' };
    return map[(s || '').toLowerCase()] || s || '-';
  }

  function riskBadgeClass(s) {
    var map = { low: 'success', medium: 'info', high: 'warning', critical: 'danger' };
    return map[(s || '').toLowerCase()] || 'secondary';
  }

  function confidenceDisplay(val) {
    if (val == null) return '-';
    var n = parseFloat(val);
    return isNaN(n) ? val : (n <= 1 ? (n * 100).toFixed(1) : n.toFixed(1)) + '%';
  }

  function aggregateResults(results) {
    // Pick worst risk and max confidence; show disease list
    var order = { low: 1, medium: 2, high: 3, critical: 4 };
    var worst = null;
    var bestConf = null;
    var diseases = [];
    (results || []).forEach(function (r) {
      var rl = (r.risk_level || '').toLowerCase();
      if (!worst || (order[rl] || 0) > (order[(worst || '').toLowerCase()] || 0)) worst = r.risk_level;
      var c = r.confidence_score != null ? parseFloat(r.confidence_score) : NaN;
      if (!isNaN(c) && (bestConf == null || c > bestConf)) bestConf = c;
      if (r.disease_type) diseases.push((r.disease_type + '').replace(/_/g, ' '));
    });
    var diseaseText = diseases.length ? diseases.slice(0, 2).join(', ') + (diseases.length > 2 ? '…' : '') : '-';
    return { worstRisk: worst, bestConfidence: bestConf, diseaseText: diseaseText };
  }

  function renderRiskDistribution(dist) {
    if (!riskDistribution) return;
    var total = 0;
    Object.keys(dist || {}).forEach(function (k) { total += dist[k] || 0; });
    if (!total) {
      riskDistribution.innerHTML = '<div class="text-muted small">Chưa có dữ liệu phân phối rủi ro.</div>';
      return;
    }
    var levels = ['low', 'medium', 'high', 'critical'];
    var html = '<div class="text-muted small mb-2">Phân phối rủi ro (' + total + ' lần)</div>';
    html += '<div class="d-flex flex-column gap-2">';
    levels.forEach(function (lv) {
      var v = (dist && dist[lv]) || 0;
      var pct = total ? Math.round((v / total) * 100) : 0;
      html += '<div>' +
        '<div class="d-flex justify-content-between small mb-1"><span>' + riskLabel(lv) + '</span><span>' + v + ' (' + pct + '%)</span></div>' +
        '<div class="progress" style="height: 8px;"><div class="progress-bar bg-' + riskBadgeClass(lv) + '" style="width:' + pct + '%"></div></div>' +
        '</div>';
    });
    html += '</div>';
    riskDistribution.innerHTML = html;
  }

  function renderTrendChart(trend) {
    if (!trendChartWrap) return;
    // Xu hướng theo Mức rủi ro: dùng trend_dates + trend_risk_numeric (1=Thấp..4=Rất cao)
    var trendDates = (trend && trend.trend_dates) || [];
    var trendNumeric = (trend && trend.trend_risk_numeric) || [];
    var trendLabels = (trend && trend.trend_risk_levels) || [];
    if (!trendDates.length || !trendNumeric.length) {
      trendChartWrap.innerHTML = '<div class="text-muted small">Chưa đủ dữ liệu để vẽ xu hướng theo mức rủi ro.</div>';
      return;
    }
    var points = trendNumeric; // 1..4
    if (points.length < 2) {
      trendChartWrap.innerHTML = '<div class="text-muted small">Chưa đủ dữ liệu để vẽ xu hướng.</div>';
      return;
    }
    var w = 520, h = 120, pad = 8;
    var minR = 1, maxR = 4;
    var span = maxR - minR;
    var stepX = (w - pad * 2) / (points.length - 1);
    var poly = points.map(function (v, i) {
      var x = pad + stepX * i;
      var y = pad + (h - pad * 2) * (1 - (v - minR) / span);
      return x.toFixed(1) + ',' + y.toFixed(1);
    }).join(' ');

    var minLabel = riskLabel((trendLabels[points.indexOf(Math.min.apply(null, points))] || 'low').toLowerCase());
    var maxLabel = riskLabel((trendLabels[points.indexOf(Math.max.apply(null, points))] || 'critical').toLowerCase());
    trendChartWrap.innerHTML =
      '<div class="d-flex justify-content-between align-items-center mb-1">' +
      '<div class="text-muted small">Mức rủi ro theo thời gian</div>' +
      '<div class="text-muted small">min ' + minLabel + ' • max ' + maxLabel + '</div>' +
      '</div>' +
      '<svg width="100%" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none" class="bg-white rounded border">' +
      '<polyline fill="none" stroke="#1976D2" stroke-width="2" points="' + poly + '"></polyline>' +
      '</svg>';
  }

  function renderTrendMeta(trend) {
    var t = (trend && trend.trend) || '';
    var map = { improving: 'Cải thiện', worsening: 'Xấu đi', stable: 'Ổn định', no_data: 'Chưa có dữ liệu' };
    if (trendLabelEl) trendLabelEl.textContent = map[t] || (t || '-');
    if (trendHintEl) {
      var total = (trend && trend.total_analyses != null) ? trend.total_analyses : '-';
      trendHintEl.textContent = 'Tổng ' + total + ' lần (xu hướng tính theo mức rủi ro)';
    }
  }

  function loadPatientInfo() {
    return window.AuraAPI.getPatient(patientId).then(function (p) {
      if (patientNameEl) patientNameEl.textContent = (p && (p.patient_name || p.full_name)) || ('Bệnh nhân #' + patientId);
      if (patientMetaEl) {
        var dob = p && p.date_of_birth ? new Date(p.date_of_birth).toLocaleDateString('vi-VN') : '-';
        var gender = (p && (p.gender === 'M' || p.gender === 'male')) ? 'Nam' : ((p && (p.gender === 'F' || p.gender === 'female')) ? 'Nữ' : '-');
        patientMetaEl.textContent = 'ID #' + patientId + ' • ' + dob + ' • ' + gender;
      }
    });
  }

  function loadTrend() {
    var days = trendDays ? parseInt(trendDays.value, 10) : 90;
    return window.AuraAPI.getPatientTrend(patientId, days).then(function (res) {
      var trend = (res && res.data !== undefined) ? res.data : res;
      renderTrendMeta(trend);
      renderTrendChart(trend);
      renderRiskDistribution(trend && trend.risk_distribution);
    });
  }

  function ensureHistoryState() {
    if (historyLoading) historyLoading.classList.toggle('d-none', !loadingHistory);
    if (historyEmpty) historyEmpty.classList.toggle('d-none', loadingHistory || !loadedAll || (historyBody && historyBody.children.length));
    if (historyTableWrap) historyTableWrap.classList.toggle('d-none', !(historyBody && historyBody.children.length));
    if (btnLoadMore) btnLoadMore.disabled = loadingHistory || loadedAll;
  }

  function appendHistoryRows(analyses) {
    if (!historyBody) return;
    var rowsHtml = '';
    analyses.forEach(function (a) {
      rowsHtml += '<tr data-analysis-id="' + a.analysis_id + '">' +
        '<td>' + fmtDate(a.analysis_time) + '</td>' +
        '<td><span class="badge bg-' + (a.status === 'completed' ? 'success' : a.status === 'failed' ? 'danger' : 'secondary') + '">' + statusLabel(a.status) + '</span></td>' +
        '<td class="text-muted small">Đang tải...</td>' +
        '<td>-</td>' +
        '<td>-</td>' +
        '<td>' + (a.image_id != null ? ('#' + a.image_id) : '-') + '</td>' +
        '<td><a class="btn btn-sm btn-outline-secondary" href="analysis-results.html"><i class="bi bi-box-arrow-up-right me-1"></i>Xem</a></td>' +
        '</tr>';
    });
    historyBody.insertAdjacentHTML('beforeend', rowsHtml);

    // Fetch results per analysis to fill summary
    analyses.forEach(function (a) {
      window.AuraAPI.getResultsByAnalysis(a.analysis_id)
        .then(function (res) {
          var results = (res && res.results) || [];
          var agg = aggregateResults(results);
          var tr = historyBody.querySelector('tr[data-analysis-id=\"' + a.analysis_id + '\"]');
          if (!tr) return;
          var tds = tr.querySelectorAll('td');
          if (tds && tds.length >= 5) {
            tds[2].textContent = agg.diseaseText;
            tds[3].innerHTML = agg.worstRisk ? ('<span class="badge bg-' + riskBadgeClass(agg.worstRisk) + '">' + riskLabel(agg.worstRisk) + '</span>') : '-';
            tds[4].innerHTML = '<strong>' + confidenceDisplay(agg.bestConfidence) + '</strong>';
          }
        })
        .catch(function () {
          var tr = historyBody.querySelector('tr[data-analysis-id=\"' + a.analysis_id + '\"]');
          if (!tr) return;
          var tds = tr.querySelectorAll('td');
          if (tds && tds.length >= 3) tds[2].textContent = '-';
        });
    });
  }

  function loadHistoryPage() {
    if (loadingHistory || loadedAll) return;
    loadingHistory = true;
    ensureHistoryState();

    return window.AuraAPI.getPatientAnalyses(patientId, limit, offset)
      .then(function (data) {
        var analyses = (data && data.analyses) || [];
        if (!analyses.length) {
          loadedAll = true;
          return;
        }
        appendHistoryRows(analyses);
        offset += analyses.length;
        if (analyses.length < limit) loadedAll = true;
      })
      .catch(function (err) {
        showError(err.message || 'Không tải được lịch sử phân tích.');
        loadedAll = true;
      })
      .finally(function () {
        loadingHistory = false;
        ensureHistoryState();
      });
  }

  function init() {
    showError('');
    var pidStr = qs('patient_id');
    patientId = pidStr ? parseInt(pidStr, 10) : NaN;
    if (!patientId || isNaN(patientId) || patientId <= 0) {
      showError('Thiếu patient_id trên URL. Ví dụ: patient-history.html?patient_id=2');
      if (historyLoading) historyLoading.classList.add('d-none');
      if (btnLoadMore) btnLoadMore.disabled = true;
      return;
    }

    if (trendDays) {
      trendDays.addEventListener('change', function () { loadTrend().catch(function () {}); });
    }
    if (btnLoadMore) {
      btnLoadMore.addEventListener('click', function () { loadHistoryPage(); });
    }

    Promise.all([loadPatientInfo(), loadTrend()])
      .catch(function (err) { showError(err.message || 'Không tải được dữ liệu bệnh nhân.'); });

    loadHistoryPage();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

