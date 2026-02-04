/**
 * AURA - Admin Statistics
 * Thống kê: analytics ảnh, phân bố rủi ro, doanh thu, tỷ lệ lỗi
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var pageError = document.getElementById('pageError');
  var daysFilter = document.getElementById('daysFilter');
  var imageAnalytics = document.getElementById('imageAnalytics');
  var riskDistribution = document.getElementById('riskDistribution');
  var revenueAnalytics = document.getElementById('revenueAnalytics');
  var errorRates = document.getElementById('errorRates');
  var statTotalImages = document.getElementById('statTotalImages');
  var statImagesLabel = document.getElementById('statImagesLabel');
  var statTotalAnalyses = document.getElementById('statTotalAnalyses');
  var statAnalysesLabel = document.getElementById('statAnalysesLabel');
  var statErrorRate = document.getElementById('statErrorRate');
  var statFailedAnalyses = document.getElementById('statFailedAnalyses');
  var statHighCritical = document.getElementById('statHighCritical');
  var statRiskLabel = document.getElementById('statRiskLabel');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function setText(el, v) {
    if (!el) return;
    el.textContent = (v != null && v !== '') ? String(v) : '-';
  }

  function getDaysParam() {
    return (daysFilter && daysFilter.value) ? daysFilter.value : '30';
  }

  function riskLabel(s) {
    var map = { low: 'Thấp', medium: 'Trung bình', high: 'Cao', critical: 'Rất cao', unknown: 'Không rõ' };
    return map[(s || '').toLowerCase()] || s || '-';
  }
  function riskBadgeClass(s) {
    var map = { low: 'success', medium: 'info', high: 'warning', critical: 'danger', unknown: 'secondary' };
    return map[(s || '').toLowerCase()] || 'secondary';
  }

  function renderSparkline(trend, valueField, color) {
    trend = trend || [];
    valueField = valueField || 'count';
    color = color || '#1976D2';
    if (!trend.length) return '<div class="text-muted small">Chưa có dữ liệu xu hướng.</div>';
    var points = trend.map(function (x) { return Number(x && x[valueField]); }).filter(function (n) { return !isNaN(n); });
    if (points.length < 2) return '<div class="text-muted small">Chưa đủ dữ liệu để vẽ xu hướng.</div>';

    var w = 520, h = 120, pad = 10;
    var minV = Math.min.apply(null, points);
    var maxV = Math.max.apply(null, points);
    if (minV === maxV) maxV = minV + 1;

    var stepX = (w - pad * 2) / (points.length - 1);
    var poly = points.map(function (v, i) {
      var x = pad + stepX * i;
      var y = pad + (h - pad * 2) * (1 - (v - minV) / (maxV - minV));
      return x.toFixed(1) + ',' + y.toFixed(1);
    }).join(' ');

    return '' +
      '<svg width="100%" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none" class="bg-white rounded border">' +
      '<polyline fill="none" stroke="' + color + '" stroke-width="2" points="' + poly + '"></polyline>' +
      '</svg>';
  }

  function renderDistributionBars(dist, levels, labelFn, badgeFn) {
    dist = dist || {};
    levels = levels || Object.keys(dist);
    var total = 0;
    levels.forEach(function (k) { total += Number(dist[k] || 0); });
    if (!total) return '<div class="text-muted small">Chưa có dữ liệu phân phối.</div>';

    var html = '<div class="d-flex flex-column gap-2">';
    levels.forEach(function (lv) {
      var v = Number(dist[lv] || 0);
      var pct = total ? Math.round((v / total) * 100) : 0;
      html += '<div>' +
        '<div class="d-flex justify-content-between small mb-1"><span>' + (labelFn ? labelFn(lv) : lv) + '</span><span>' + v.toLocaleString('vi-VN') + ' (' + pct + '%)</span></div>' +
        '<div class="progress" style="height: 8px;"><div class="progress-bar bg-' + (badgeFn ? badgeFn(lv) : 'primary') + '" style="width:' + pct + '%"></div></div>' +
        '</div>';
    });
    html += '</div>';
    return html;
  }

  function renderKeyValueTable(obj, keyLabelFn) {
    obj = obj || {};
    var keys = Object.keys(obj);
    if (!keys.length) return '<div class="text-muted small">Chưa có dữ liệu.</div>';
    keys.sort(function (a, b) { return String(a).localeCompare(String(b)); });
    var html = '<div class="table-responsive"><table class="table table-sm mb-0"><tbody>';
    keys.forEach(function (k) {
      var v = obj[k];
      var kk = keyLabelFn ? keyLabelFn(k) : k;
      html += '<tr><td class="text-muted" style="width:45%">' + kk + '</td><td class="fw-semibold">' + (Number.isFinite(Number(v)) ? Number(v).toLocaleString('vi-VN') : (v == null ? '-' : String(v))) + '</td></tr>';
    });
    html += '</tbody></table></div>';
    return html;
  }

  function imageTypeLabel(s) {
    // Do NOT translate: fundus, oct
    var k = (s || '').toLowerCase();
    if (k === 'fundus' || k === 'oct') return s;
    var map = { unknown: 'Không rõ', other: 'Khác' };
    return map[k] || s || '-';
  }

  function statusLabel(s) {
    // Do NOT translate: pending, uploaded
    var k = (s || '').toLowerCase();
    if (k === 'pending' || k === 'uploaded') return s;
    var map = {
      processing: 'Đang xử lý',
      analyzed: 'Đã phân tích',
      completed: 'Hoàn thành',
      failed: 'Thất bại',
      error: 'Lỗi',
      unknown: 'Không rõ'
    };
    return map[k] || s || '-';
  }

  function paymentMethodLabel(s) {
    var k = (s || '').toLowerCase();
    var map = {
      bank_transfer: 'Chuyển khoản',
      transfer: 'Chuyển khoản',
      cash: 'Tiền mặt',
      momo: 'MoMo',
      vnpay: 'VNPay',
      paypal: 'PayPal',
      card: 'Thẻ'
    };
    return map[k] || s || '-';
  }

  function renderImageAnalytics(a) {
    if (!imageAnalytics) return;
    a = a || {};
    var total = a.total_images != null ? a.total_images : 0;
    var label = a.period_label || '-';
    setText(statTotalImages, Number(total).toLocaleString('vi-VN'));
    setText(statImagesLabel, label);

    var html = '' +
      '<div class="d-flex justify-content-between align-items-center mb-2">' +
      '<div class="text-muted small">' + label + '</div>' +
      '<div class="small">Tổng: <strong>' + Number(total).toLocaleString('vi-VN') + '</strong></div>' +
      '</div>' +
      '<div class="mb-3">' + renderSparkline(a.daily_upload_trend, 'count', '#1976D2') + '</div>' +
      '<div class="row g-3">' +
      '<div class="col-md-6"><div class="text-muted small mb-2">Theo loại ảnh</div>' + renderKeyValueTable(a.type_distribution, imageTypeLabel) + '</div>' +
      '<div class="col-md-6"><div class="text-muted small mb-2">Theo trạng thái</div>' + renderKeyValueTable(a.status_distribution, statusLabel) + '</div>' +
      '</div>';
    imageAnalytics.innerHTML = html;
  }

  function renderRiskAnalytics(r) {
    if (!riskDistribution) return;
    r = r || {};
    var dist = r.risk_distribution || {};
    var total = r.total_analyses != null ? r.total_analyses : 0;
    var highCritical = Number(dist.high || 0) + Number(dist.critical || 0);
    setText(statHighCritical, highCritical.toLocaleString('vi-VN'));
    setText(statRiskLabel, r.period_label || '-');

    var avg = r.average_confidence;
    var avgText = '-';
    if (avg != null && avg !== '') {
      var n = Number(avg);
      avgText = isNaN(n) ? String(avg) : ((n >= 0 && n <= 1) ? (n * 100).toFixed(1) + '%' : n.toFixed(1) + '%');
    }

    var html = '' +
      '<div class="d-flex justify-content-between align-items-center mb-2">' +
      '<div class="text-muted small">' + (r.period_label || '-') + '</div>' +
      '<div class="small">Phân tích: <strong>' + Number(total).toLocaleString('vi-VN') + '</strong> • Độ tin cậy TB: <strong>' + avgText + '</strong></div>' +
      '</div>' +
      renderDistributionBars(dist, ['low', 'medium', 'high', 'critical', 'unknown'], riskLabel, riskBadgeClass);
    riskDistribution.innerHTML = html;
  }

  function renderRevenueAnalytics(a) {
    if (!revenueAnalytics) return;
    a = a || {};
    var total = a.total_revenue != null ? a.total_revenue : 0;
    var html = '' +
      '<div class="d-flex justify-content-between align-items-center mb-2">' +
      '<div class="text-muted small">' + (a.period_label || '-') + '</div>' +
      '<div class="small">Tổng: <strong>' + (Number(total).toLocaleString('vi-VN')) + '</strong> • Giao dịch: <strong>' + (Number(a.total_payments || 0).toLocaleString('vi-VN')) + '</strong></div>' +
      '</div>' +
      '<div class="mb-3">' + renderSparkline(a.daily_revenue_trend, 'amount', '#FF8F00') + '</div>' +
      '<div class="row g-3">' +
      '<div class="col-md-6"><div class="text-muted small mb-2">Theo phương thức</div>' + renderKeyValueTable(a.payment_method_distribution, paymentMethodLabel) + '</div>' +
      '<div class="col-md-6"><div class="text-muted small mb-2">Tất cả thời gian</div>' +
      '<div class="text-muted small">Tổng doanh thu: <strong class="text-dark">' + Number(a.all_time_total_revenue || 0).toLocaleString('vi-VN') + '</strong></div>' +
      '<div class="text-muted small">Tổng giao dịch: <strong class="text-dark">' + Number(a.all_time_total_payments || 0).toLocaleString('vi-VN') + '</strong></div>' +
      '</div>' +
      '</div>';
    revenueAnalytics.innerHTML = html;
  }

  function renderErrorAnalytics(a) {
    if (!errorRates) return;
    a = a || {};
    var total = Number(a.total_analyses || 0);
    var failed = Number(a.failed_analyses || 0);
    var completed = Number(a.completed_analyses || 0);
    var terminalTotal = Number(a.terminal_total || (failed + completed) || 0);
    setText(statTotalAnalyses, total.toLocaleString('vi-VN'));
    setText(statAnalysesLabel, a.period_label || '-');
    setText(statErrorRate, (a.error_rate != null ? Number(a.error_rate).toFixed(2) : 0) + '%');
    setText(statFailedAnalyses, 'Thất bại/Đã xong: ' + failed.toLocaleString('vi-VN') + '/' + terminalTotal.toLocaleString('vi-VN'));

    // Đảm bảo luôn có dòng Hoàn thành và Thất bại
    var breakdown = a.status_breakdown || {};
    if (breakdown.completed == null) breakdown.completed = 0;
    if (breakdown.failed == null) breakdown.failed = 0;

    var html = '' +
      '<div class="d-flex justify-content-between align-items-center mb-2">' +
      '<div class="text-muted small">' + (a.period_label || '-') + '</div>' +
      '<div class="small">Tổng phân tích: <strong>' + total.toLocaleString('vi-VN') + '</strong></div>' +
      '</div>' +
      '<div class="mb-2">' + renderSparkline(a.daily_failure_trend, 'error_rate_all', '#D32F2F') + '</div>' +
      '<div class="text-muted small mb-3">Tỷ lệ lỗi chính = Thất bại / (Tổng phân tích)</div>' +
      renderKeyValueTable(breakdown, statusLabel);
    errorRates.innerHTML = html;
  }

  function load() {
    showError('');
    var daysParam = getDaysParam();
    if (imageAnalytics) imageAnalytics.innerHTML = '<div class="text-muted small">Đang tải...</div>';
    if (riskDistribution) riskDistribution.innerHTML = '<div class="text-muted small">Đang tải...</div>';
    if (revenueAnalytics) revenueAnalytics.innerHTML = '<div class="text-muted small">Đang tải...</div>';
    if (errorRates) errorRates.innerHTML = '<div class="text-muted small">Đang tải...</div>';
    setText(statTotalImages, '...');
    setText(statImagesLabel, '...');
    setText(statTotalAnalyses, '...');
    setText(statAnalysesLabel, '...');
    setText(statErrorRate, '...');
    setText(statFailedAnalyses, '...');
    setText(statHighCritical, '...');
    setText(statRiskLabel, '...');

    Promise.all([
      window.AuraAPI.getAdminImageAnalytics(daysParam),
      window.AuraAPI.getAdminRiskDistribution(daysParam),
      window.AuraAPI.getAdminRevenueAnalytics(daysParam),
      window.AuraAPI.getAdminErrorRateAnalytics(daysParam)
    ])
      .then(function (results) {
        renderImageAnalytics(results[0]);
        renderRiskAnalytics(results[1]);
        renderRevenueAnalytics(results[2]);
        renderErrorAnalytics(results[3]);
      })
      .catch(function (err) {
        showError(err.message || 'Tải thống kê thất bại.');
        if (imageAnalytics) imageAnalytics.innerHTML = '<div class="text-danger small">Lỗi</div>';
        if (riskDistribution) riskDistribution.innerHTML = '<div class="text-danger small">Lỗi</div>';
        if (revenueAnalytics) revenueAnalytics.innerHTML = '<div class="text-danger small">Lỗi</div>';
        if (errorRates) errorRates.innerHTML = '<div class="text-danger small">Lỗi</div>';
        setText(statTotalImages, '-');
        setText(statImagesLabel, '-');
        setText(statTotalAnalyses, '-');
        setText(statAnalysesLabel, '-');
        setText(statErrorRate, '-');
        setText(statFailedAnalyses, '-');
        setText(statHighCritical, '-');
        setText(statRiskLabel, '-');
      });
  }

  if (daysFilter) daysFilter.addEventListener('change', load);
  load();
})();
