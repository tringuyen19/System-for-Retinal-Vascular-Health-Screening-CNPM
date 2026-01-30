/**
 * AURA - Patient My Images
 * Table images, filter (eye_side), search, pagination
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireLogin || !window.AuraAuth.requireLogin()) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var patientId = null;
  var allImages = [];
  var currentPage = 1;
  var pageSize = 10;

  var filterEye = document.getElementById('filterEye');
  var searchInput = document.getElementById('searchInput');
  var tableError = document.getElementById('tableError');
  var container = document.getElementById('imagesTableContainer');

  function showError(msg) {
    if (!tableError) return;
    tableError.textContent = msg || '';
    tableError.classList.toggle('d-none', !msg);
  }

  function getPatient() {
    if (!accountId) return Promise.reject(new Error('Không tìm thấy tài khoản.'));
    return window.AuraAPI.getPatientByAccount(accountId).then(function (p) {
      if (!p || !p.patient_id) return Promise.reject(new Error('Chưa có hồ sơ bệnh nhân.'));
      patientId = p.patient_id;
      return patientId;
    });
  }

  function loadImages(eyeSide) {
    if (!patientId) return Promise.reject(new Error('Chưa có patient_id.'));
    return window.AuraAPI.getImagesByPatient(patientId, eyeSide || '').then(function (data) {
      allImages = (data && data.images) || [];
      return allImages;
    });
  }

  function filterData() {
    var eye = filterEye ? filterEye.value : '';
    var q = (searchInput && searchInput.value) ? searchInput.value.trim().toLowerCase() : '';
    var list = allImages;
    if (eye) list = list.filter(function (img) { return (img.eye_side || '') === eye; });
    if (q) list = list.filter(function (img) {
      return (img.image_type || '').toLowerCase().indexOf(q) !== -1 ||
             String(img.image_id || '').indexOf(q) !== -1;
    });
    return list;
  }

  function render() {
    if (!container || !window.AuraTable) return;
    var filtered = filterData();
    var columns = [
      { key: 'image_id', label: 'ID' },
      { key: 'image_type', label: 'Loại ảnh' },
      { key: 'eye_side', label: 'Bên mắt' },
      { key: 'status', label: 'Trạng thái' },
      { key: 'created_at', label: 'Ngày tải', render: function (v) { return v ? v.slice(0, 10) : '-'; } },
      { key: 'image_url', label: 'Xem', render: function (v, row) {
        if (!v) return '-';
        return '<a href="' + (v.indexOf('data:') === 0 ? v : v) + '" target="_blank" class="btn btn-sm btn-outline-primary">Xem</a>';
      } }
    ];
    window.AuraTable.render('imagesTableContainer', {
      columns: columns,
      data: filtered,
      pageSize: pageSize,
      currentPage: currentPage,
      onPageChange: function (p) { currentPage = p; render(); }
    });
  }

  function init() {
    getPatient()
      .then(function () { return loadImages(); })
      .then(function () {
        showError('');
        render();
      })
      .catch(function (err) {
        showError(err.message || 'Không tải được danh sách ảnh.');
        container.innerHTML = '<p class="text-muted">Chưa có ảnh nào.</p>';
      });
  }

  if (filterEye) filterEye.addEventListener('change', function () { render(); });
  if (searchInput) searchInput.addEventListener('input', window.AuraUtils && window.AuraUtils.debounce ? window.AuraUtils.debounce(render, 300) : render);

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
