/**
 * AURA - Clinic Usage
 * GET /api/clinics/:id/usage
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var usageContent = document.getElementById('usageContent');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!clinicId) { showError('Bạn chưa được gán phòng khám.'); usageContent.innerHTML = ''; return; }
    showError('');
    window.AuraAPI.getClinicUsage(clinicId)
      .then(function (data) {
        usageContent.innerHTML =
          '<p class="mb-1"><strong>Ảnh đã upload:</strong> ' + ((data && data.total_images_uploaded != null) ? data.total_images_uploaded : '-') + '</p>' +
          '<p class="mb-1"><strong>Phân tích:</strong> ' + ((data && data.total_analyses != null) ? data.total_analyses : '-') + '</p>' +
          '<p class="mb-1"><strong>Gói đăng ký đang dùng:</strong> ' + ((data && data.active_subscriptions != null) ? data.active_subscriptions : '-') + '</p>' +
          '<p class="mb-1"><strong>Tổng credits:</strong> ' + ((data && data.total_credits_allocated != null) ? data.total_credits_allocated : '-') + '</p>' +
          '<p class="mb-1"><strong>Đã dùng:</strong> ' + ((data && data.credits_used != null) ? data.credits_used : '-') + '</p>' +
          '<p class="mb-0"><strong>Còn lại:</strong> ' + ((data && data.remaining_credits != null) ? data.remaining_credits : '-') + '</p>';
      })
      .catch(function (err) {
        usageContent.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được.') + '</p>';
        showError(err.message || 'Tải thất bại.');
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
