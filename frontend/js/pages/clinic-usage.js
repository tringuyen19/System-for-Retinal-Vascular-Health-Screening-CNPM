/**
 * AURA - FR-27: Theo dõi số lượng ảnh đã phân tích và 
 * GET /api/clinics/:id/usage
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var totalImagesUploaded = document.getElementById('totalImagesUploaded');
  var totalAnalyses = document.getElementById('totalAnalyses');
  var totalCreditsAllocated = document.getElementById('totalCreditsAllocated');
  var creditsUsed = document.getElementById('creditsUsed');
  var remainingCredits = document.getElementById('remainingCredits');
  var imagesUsedByClinic = document.getElementById('imagesUsedByClinic');
  var imagesUsedByPatients = document.getElementById('imagesUsedByPatients');
  var usageProgressBar = document.getElementById('usageProgressBar');
  var activeSubsCount = document.getElementById('activeSubsCount');
  var usageLoading = document.getElementById('usageLoading');
  var usageContent = document.getElementById('usageContent');
  var packageUsageTableWrap = document.getElementById('packageUsageTableWrap');
  var packageUsageTbody = document.getElementById('packageUsageTbody');
  var packageUsageSummary = document.getElementById('packageUsageSummary');
  var usageEmpty = document.getElementById('usageEmpty');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function setVal(el, value, fallback) {
    if (!el) return;
    el.textContent = value != null && value !== '' ? value : (fallback != null ? fallback : '-');
  }

  function load() {
    if (!clinicId) {
      showError('Bạn chưa được gán phòng khám.');
      if (usageLoading) usageLoading.classList.add('d-none');
      if (usageEmpty) { usageEmpty.classList.remove('d-none'); usageEmpty.textContent = 'Bạn chưa được gán phòng khám.'; }
      return;
    }
    showError('');
    if (usageLoading) usageLoading.classList.remove('d-none');
    if (usageEmpty) usageEmpty.classList.add('d-none');
    if (packageUsageTableWrap) packageUsageTableWrap.classList.add('d-none');

    window.AuraAPI.getClinicUsage(clinicId)
      .then(function (data) {
        if (usageLoading) usageLoading.classList.add('d-none');

        var totalImg = (data && data.total_images_uploaded != null) ? data.total_images_uploaded : null;
        var totalAna = (data && data.total_analyses != null) ? data.total_analyses : null;
        var totalAlloc = (data && data.total_credits_allocated != null) ? data.total_credits_allocated : null;
        var used = (data && data.credits_used != null) ? data.credits_used : null;
        var remaining = (data && data.remaining_credits != null) ? data.remaining_credits : null;
        var usagePct = (data && data.usage_percentage != null) ? data.usage_percentage : (totalAlloc > 0 ? Math.round((used / totalAlloc) * 1000) / 10 : 0);
        var activeCount = (data && data.active_subscriptions != null) ? data.active_subscriptions : 0;
        var packages = (data && data.package_usage && Array.isArray(data.package_usage)) ? data.package_usage : [];

        setVal(totalImagesUploaded, totalImg);
        setVal(totalAnalyses, totalAna);
        setVal(totalCreditsAllocated, totalAlloc);
        setVal(creditsUsed, used);
        setVal(remainingCredits, remaining);
        setVal(imagesUsedByClinic, (data && data.images_used_by_clinic != null) ? data.images_used_by_clinic : null);
        setVal(imagesUsedByPatients, (data && data.images_used_by_patients != null) ? data.images_used_by_patients : null);
        setVal(activeSubsCount, activeCount);

        if (usageProgressBar) {
          var pct = Math.min(100, Math.max(0, parseFloat(usagePct) || 0));
          usageProgressBar.style.width = pct + '%';
          usageProgressBar.setAttribute('aria-valuenow', pct);
          usageProgressBar.textContent = pct + '%';
        }

        if (packages.length === 0) {
          usageEmpty.classList.remove('d-none');
          usageEmpty.innerHTML = 'Chưa có gói đăng ký đang kích hoạt. <a href="subscriptions.html">Xem gói đăng ký</a>.';
          return;
        }

        packageUsageTableWrap.classList.remove('d-none');
        usageEmpty.classList.add('d-none');
        var rows = packages.map(function (p) {
          var start = (p.start_date ? new Date(p.start_date).toLocaleDateString('vi-VN') : '-');
          var end = (p.end_date ? new Date(p.end_date).toLocaleDateString('vi-VN') : '-');
          var period = start + ' → ' + end;
          var nameCell = (p.package_name || 'Gói #' + p.package_id);
          return '<tr>' +
            '<td><strong>' + nameCell + '</strong></td>' +
            '<td>' + (p.initial_credits != null ? p.initial_credits.toLocaleString('vi-VN') : '-') + '</td>' +
            '<td>' + (p.credits_used != null ? p.credits_used.toLocaleString('vi-VN') : '-') + '</td>' +
            '<td>' + (p.remaining_credits != null ? p.remaining_credits.toLocaleString('vi-VN') : '-') + '</td>' +
            '<td class="small">' + period + '</td></tr>';
        }).join('');
        packageUsageTbody.innerHTML = rows;
      })
      .catch(function (err) {
        if (usageLoading) usageLoading.classList.add('d-none');
        usageEmpty.classList.remove('d-none');
        usageEmpty.textContent = err.message || 'Không tải được dữ liệu.';
        packageUsageTableWrap.classList.add('d-none');
        showError(err.message || 'Tải thất bại.');
        setVal(totalImagesUploaded, null);
        setVal(totalAnalyses, null);
        setVal(totalCreditsAllocated, null);
        setVal(creditsUsed, null);
        setVal(remainingCredits, null);
        setVal(imagesUsedByClinic, null);
        setVal(imagesUsedByPatients, null);
        if (usageProgressBar) { usageProgressBar.style.width = '0%'; usageProgressBar.textContent = '0%'; }
        setVal(activeSubsCount, null);
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
