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

  function setPre(el, data) {
    if (!el) return;
    try {
      el.textContent = typeof data === 'object' ? JSON.stringify(data, null, 2) : (data || '-');
    } catch (e) {
      el.textContent = String(data);
    }
  }

  function load() {
    showError('');
    var days = getDays();
    if (imageAnalytics) imageAnalytics.textContent = 'Đang tải...';
    if (riskDistribution) riskDistribution.textContent = 'Đang tải...';
    if (revenueAnalytics) revenueAnalytics.textContent = 'Đang tải...';
    if (errorRates) errorRates.textContent = 'Đang tải...';

    var revenueDays = days;
    if (daysFilter && daysFilter.value === 'all') revenueDays = 'all';

    Promise.all([
      window.AuraAPI.getAdminImageAnalytics(days),
      window.AuraAPI.getAdminRiskDistribution(),
      window.AuraAPI.getAdminRevenueAnalytics(revenueDays),
      window.AuraAPI.getAdminErrorRateAnalytics()
    ])
      .then(function (results) {
        setPre(imageAnalytics, results[0]);
        setPre(riskDistribution, results[1]);
        setPre(revenueAnalytics, results[2]);
        setPre(errorRates, results[3]);
      })
      .catch(function (err) {
        showError(err.message || 'Tải thống kê thất bại.');
        setPre(imageAnalytics, 'Lỗi');
        setPre(riskDistribution, 'Lỗi');
        setPre(revenueAnalytics, 'Lỗi');
        setPre(errorRates, 'Lỗi');
      });
  }

  if (daysFilter) daysFilter.addEventListener('change', load);
  load();
})();