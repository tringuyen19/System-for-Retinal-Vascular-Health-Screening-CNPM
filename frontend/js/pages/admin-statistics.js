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

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function getDays() {
    var v = daysFilter && daysFilter.value ? daysFilter.value : '30';
    if (v === 'all') return null;
    return parseInt(v, 10) || 30;
  }

  function renderImageAnalytics(data) {
    if (!imageAnalytics) return;
    if (!data) {
      imageAnalytics.innerHTML = '<p class="text-muted">Không có dữ liệu</p>';
      return;
    }
    
    var html = '<div class="stats-cards">';
    
    // Daily upload trend
    if (data.daily_upload_trend && Array.isArray(data.daily_upload_trend)) {
      var totalUploaded = 0;
      data.daily_upload_trend.forEach(function (d) {
        totalUploaded += (d.count || 0);
      });
      html += '<div class="stat-box">';
      html += '<h6>📤 Tổng ảnh tải lên</h6>';
      html += '<div class="stat-value">' + totalUploaded + '</div>';
      html += '<small class="text-muted">trong ' + getDays() + ' ngày</small>';
      html += '</div>';
    }
    
    // Image types
    if (data.type_distribution && typeof data.type_distribution === 'object') {
      html += '<div class="stat-box">';
      html += '<h6>🔍 Loại ảnh</h6>';
      var types = [];
      for (var type in data.type_distribution) {
        types.push(type + ': ' + data.type_distribution[type]);
      }
      html += '<small>' + types.join(', ') + '</small>';
      html += '</div>';
    }
    
    html += '</div>';
    html += '<style>.stats-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; } .stat-box { padding: 1rem; background: #f8f9fa; border-radius: 4px; } .stat-value { font-size: 28px; font-weight: bold; color: #007bff; margin: 0.5rem 0; } .stat-box h6 { margin: 0 0 0.5rem 0; font-weight: 600; }</style>';
    imageAnalytics.innerHTML = html;
  }

  function renderRiskDistribution(data) {
    if (!riskDistribution) return;
    if (!data) {
      riskDistribution.innerHTML = '<p class="text-muted">Không có dữ liệu</p>';
      return;
    }
    
    var html = '<div class="risk-cards">';
    
    if (data.risk_distribution && typeof data.risk_distribution === 'object') {
      var distribution = data.risk_distribution;
      var riskLevels = ['critical', 'high', 'medium', 'low'];
      var colors = { critical: '#dc3545', high: '#fd7e14', medium: '#ffc107', low: '#28a745' };
      
      riskLevels.forEach(function (level) {
        if (distribution[level] != null) {
          var count = distribution[level];
          var color = colors[level] || '#6c757d';
          var label = { critical: '🔴 Nguy hiểm', high: '🟠 Cao', medium: '🟡 Trung bình', low: '🟢 Thấp' }[level];
          
          html += '<div class="risk-item" style="border-left: 4px solid ' + color + '; padding-left: 12px;">';
          html += '<strong>' + label + '</strong>';
          html += '<div style="font-size: 24px; color: ' + color + '; font-weight: bold;">' + count + '</div>';
          html += '</div>';
        }
      });
    }
    
    html += '</div>';
    html += '<style>.risk-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; } .risk-item { padding: 1rem; background: #f8f9fa; border-radius: 4px; }</style>';
    riskDistribution.innerHTML = html;
  }

  function renderRevenueAnalytics(data) {
    if (!revenueAnalytics) return;
    if (!data) {
      revenueAnalytics.innerHTML = '<p class="text-muted">Không có dữ liệu</p>';
      return;
    }
    
    var html = '<div class="revenue-stats">';
    
    if (data.all_time_total_revenue != null) {
      html += '<div class="revenue-box">';
      html += '<h6>💰 Tổng doanh thu</h6>';
      html += '<div class="revenue-value">' + new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(data.all_time_total_revenue || 0) + '</div>';
      html += '</div>';
    }
    
    if (data.period_days && data.total_revenue != null) {
      html += '<div class="revenue-box">';
      html += '<h6>' + (data.period_days || getDays()) + ' ngày gần đây</h6>';
      html += '<div class="revenue-value">' + new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(data.total_revenue || 0) + '</div>';
      html += '</div>';
    }
    
    if (data.total_payments != null) {
      html += '<div class="revenue-box">';
      html += '<h6>💳 Số lần thanh toán</h6>';
      html += '<div class="revenue-value">' + data.total_payments + '</div>';
      html += '</div>';
    }
    
    html += '</div>';
    html += '<style>.revenue-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; } .revenue-box { padding: 1rem; background: #f8f9fa; border-radius: 4px; } .revenue-box h6 { margin: 0 0 0.5rem 0; color: #666; } .revenue-value { font-size: 20px; font-weight: bold; color: #28a745; }</style>';
    revenueAnalytics.innerHTML = html;
  }

  function renderErrorRates(data) {
    if (!errorRates) return;
    if (!data) {
      errorRates.innerHTML = '<p class="text-muted">Không có dữ liệu</p>';
      return;
    }
    
    var html = '<div class="error-stats">';
    
    if (data.error_rate != null) {
      var rate = parseFloat(data.error_rate) || 0;
      var color = rate > 0.1 ? '#dc3545' : rate > 0.05 ? '#fd7e14' : '#28a745';
      html += '<div class="error-box">';
      html += '<h6>⚠️ Tỷ lệ lỗi</h6>';
      html += '<div class="error-value" style="color: ' + color + ';">' + (rate * 100).toFixed(2) + '%</div>';
      html += '</div>';
    }
    
    if (data.failed_analyses != null) {
      html += '<div class="error-box">';
      html += '<h6>❌ Phân tích thất bại</h6>';
      html += '<div class="error-value">' + data.failed_analyses + '</div>';
      html += '</div>';
    }
    
    if (data.status_breakdown && typeof data.status_breakdown === 'object') {
      var completed = data.status_breakdown.completed || 0;
      html += '<div class="error-box">';
      html += '<h6>✅ Phân tích hoàn thành</h6>';
      html += '<div class="error-value">' + completed + '</div>';
      html += '</div>';
    }
    
    html += '</div>';
    html += '<style>.error-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; } .error-box { padding: 1rem; background: #f8f9fa; border-radius: 4px; } .error-box h6 { margin: 0 0 0.5rem 0; color: #666; } .error-value { font-size: 24px; font-weight: bold; }</style>';
    errorRates.innerHTML = html;
  }

  function load() {
    showError('');
    var days = getDays();
    if (imageAnalytics) imageAnalytics.innerHTML = '<div class="placeholder-glow"><div class="placeholder col-12" style="height: 100px;"></div></div>';
    if (riskDistribution) riskDistribution.innerHTML = '<div class="placeholder-glow"><div class="placeholder col-12" style="height: 100px;"></div></div>';
    if (revenueAnalytics) revenueAnalytics.innerHTML = '<div class="placeholder-glow"><div class="placeholder col-12" style="height: 100px;"></div></div>';
    if (errorRates) errorRates.innerHTML = '<div class="placeholder-glow"><div class="placeholder col-12" style="height: 100px;"></div></div>';

    var revenueDays = days;
    if (daysFilter && daysFilter.value === 'all') revenueDays = 'all';

    Promise.all([
      window.AuraAPI.getAdminImageAnalytics(days),
      window.AuraAPI.getAdminRiskDistribution(),
      window.AuraAPI.getAdminRevenueAnalytics(revenueDays),
      window.AuraAPI.getAdminErrorRateAnalytics()
    ])
      .then(function (results) {
        renderImageAnalytics(results[0]);
        renderRiskDistribution(results[1]);
        renderRevenueAnalytics(results[2]);
        renderErrorRates(results[3]);
      })
      .catch(function (err) {
        showError(err.message || 'Tải thống kê thất bại.');
        if (imageAnalytics) imageAnalytics.innerHTML = '<p class="text-danger">Lỗi tải dữ liệu</p>';
        if (riskDistribution) riskDistribution.innerHTML = '<p class="text-danger">Lỗi tải dữ liệu</p>';
        if (revenueAnalytics) revenueAnalytics.innerHTML = '<p class="text-danger">Lỗi tải dữ liệu</p>';
        if (errorRates) errorRates.innerHTML = '<p class="text-danger">Lỗi tải dữ liệu</p>';
      });
  }

  if (daysFilter) daysFilter.addEventListener('change', load);
  load();
})();