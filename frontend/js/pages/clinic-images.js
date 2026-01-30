/**
 * AURA - Clinic Images
 * GET /api/retinal-images/clinic/:id
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

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!clinicId) { showError('Bạn chưa được gán phòng khám.'); return; }
    showError('');
    loading.classList.remove('d-none');
    content.classList.add('d-none');
    empty.classList.add('d-none');
    window.AuraAPI.getImagesByClinic(clinicId)
      .then(function (data) {
        loading.classList.add('d-none');
        var list = (data && data.images) || [];
        var count = (data && data.count != null) ? data.count : list.length;
        if (!list.length) {
          empty.classList.remove('d-none');
          return;
        }
        content.classList.remove('d-none');
        summary.textContent = 'Tổng: ' + count + ' ảnh.';
        var html = '';
        list.forEach(function (img) {
          var created = (img.upload_time || img.created_at) ? new Date(img.upload_time || img.created_at).toLocaleDateString('vi-VN') : '-';
          html += '<tr><td>' + (img.image_id || img.id || '-') + '</td><td>' + (img.patient_id || '-') + '</td><td>' + (img.image_type || '-') + '</td><td>' + (img.eye_side || '-') + '</td><td><span class="badge bg-secondary">' + (img.status || '-') + '</span></td><td>' + created + '</td></tr>';
        });
        tbody.innerHTML = html;
      })
      .catch(function (err) {
        loading.classList.add('d-none');
        empty.classList.remove('d-none');
        empty.textContent = err.message || 'Không tải được danh sách.';
        showError(err.message || 'Tải thất bại.');
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
