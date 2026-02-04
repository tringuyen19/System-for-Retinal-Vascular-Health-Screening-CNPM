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

  function esc(s) {
    if (s == null || s === '') return '';
    return ('' + s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
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
          var url = (img.image_url || img.full_url || '').trim();
          var imgCell = url
            ? '<img src="' + url + '" alt="" class="rounded" style="width:48px;height:48px;object-fit:cover;" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'inline-block\';"><span class="d-none"><i class="bi bi-image text-muted"></i></span><br><button type="button" class="btn btn-sm btn-outline-primary mt-1 btn-view-image" data-url="' + url.replace(/"/g, '&quot;') + '"><i class="bi bi-image me-1"></i>Xem ảnh</button>'
            : '<button type="button" class="btn btn-sm btn-outline-secondary btn-view-image" disabled><i class="bi bi-image me-1"></i>Không có ảnh</button>';
          var patientDisplay = (img.patient_name || '').trim() || (img.patient_id != null ? img.patient_id : '-');
        html += '<tr><td>' + (img.image_id || img.id || '-') + '</td><td>' + imgCell + '</td><td>' + esc(patientDisplay) + '</td><td>' + esc(img.image_type || '-') + '</td><td>' + esc(img.eye_side || '-') + '</td><td><span class="badge bg-secondary">' + esc(img.status || '-') + '</span></td><td>' + created + '</td></tr>';
        });
        tbody.innerHTML = html;
        tbody.querySelectorAll('.btn-view-image:not([disabled])').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var u = btn.getAttribute('data-url');
            if (u) window.open(u, '_blank', 'noopener,noreferrer');
          });
        });
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
