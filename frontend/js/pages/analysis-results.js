/**
 * AURA - Patient Analysis Results
 * Hiển thị danh sách ảnh đã phân tích (từ images với status analyzed)
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireLogin || !window.AuraAuth.requireLogin()) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var patientId = null;
  var listEl = document.getElementById('analysisList');

  function getPatient() {
    if (!accountId) return Promise.reject(new Error('Không tìm thấy tài khoản.'));
    return window.AuraAPI.getPatientByAccount(accountId).then(function (p) {
      if (!p || !p.patient_id) return Promise.reject(new Error('Chưa có hồ sơ bệnh nhân.'));
      patientId = p.patient_id;
      return patientId;
    });
  }

  getPatient()
    .then(function () { return window.AuraAPI.getImagesByPatient(patientId); })
    .then(function (data) {
      var images = (data && data.images) || [];
      var analyzed = images.filter(function (img) { return (img.status || '').toLowerCase().indexOf('analyz') !== -1 || img.status === 'analyzed'; });
      if (!listEl) return;
      if (!analyzed.length) {
        listEl.innerHTML = '<div class="col-12"><div class="card border-0 shadow-sm"><div class="card-body text-center text-muted py-5">Chưa có kết quả phân tích. <a href="upload-image.html">Upload ảnh</a> để bắt đầu.</div></div></div>';
        return;
      }
      listEl.innerHTML = analyzed.map(function (img) {
        return '<div class="col-md-4"><div class="card border-0 shadow-sm h-100">' +
          (img.image_url ? '<img src="' + img.image_url + '" class="card-img-top" alt="Ảnh" style="height: 180px; object-fit: cover;">' : '') +
          '<div class="card-body"><h6 class="card-title">Ảnh #' + (img.image_id || img.id) + '</h6>' +
          '<p class="card-text small text-muted">Loại: ' + (img.image_type || '-') + ' | Mắt: ' + (img.eye_side || '-') + '</p>' +
          '<a href="reports.html" class="btn btn-sm btn-outline-primary">Xem báo cáo</a></div></div></div>';
      }).join('');
    })
    .catch(function (err) {
      if (listEl) listEl.innerHTML = '<div class="col-12"><div class="alert alert-warning">' + (err.message || 'Không tải được dữ liệu.') + '</div></div>';
    });
})();
