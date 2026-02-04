/**
 * AURA - Admin Clinics
 * Danh sách phòng khám, verify/reject/approve/suspend
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var pageError = document.getElementById('pageError');
  var filterStatus = document.getElementById('filterStatus');
  var btnReload = document.getElementById('btnReload');
  var clinicsTableBody = document.getElementById('clinicsTableBody');
  var modalAction = document.getElementById('modalAction');
  var modalActionTitle = document.getElementById('modalActionTitle');
  var modalActionMessage = document.getElementById('modalActionMessage');
  var wrapReason = document.getElementById('wrapReason');
  var labelReason = document.getElementById('labelReason');
  var inputReason = document.getElementById('inputReason');
  var btnConfirmAction = document.getElementById('btnConfirmAction');

  var pendingAction = null;

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function loadClinics() {
    var status = filterStatus && filterStatus.value ? filterStatus.value : '';
    if (clinicsTableBody) clinicsTableBody.innerHTML = '<tr><td colspan="5" class="text-center">Đang tải...</td></tr>';
    window.AuraAPI.listClinics(status || undefined)
      .then(function (res) {
        var list = (res && res.clinics) ? res.clinics : [];
        renderTable(list);
      })
      .catch(function (err) {
        showError(err.message || 'Tải danh sách thất bại.');
        if (clinicsTableBody) clinicsTableBody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Lỗi tải dữ liệu</td></tr>';
      });
  }

  function renderTable(list) {
    if (!clinicsTableBody) return;
    if (!list || list.length === 0) {
      clinicsTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Không có phòng khám</td></tr>';
      return;
    }
    var html = '';
    list.forEach(function (c) {
      var id = c.clinic_id != null ? c.clinic_id : c.id;
      var status = (c.verification_status || c.status || 'pending');
      var badgeClass = status === 'verified' ? 'success' : status === 'pending' ? 'warning' : status === 'rejected' ? 'danger' : status === 'suspended' ? 'secondary' : 'secondary';
      
      // Verification info
      var verificationInfo = [];
      if (c.license_number) verificationInfo.push('<small class="d-block"><i class="bi bi-file-earmark-text me-1"></i>GP: ' + c.license_number + '</small>');
      if (c.tax_id) verificationInfo.push('<small class="d-block"><i class="bi bi-receipt me-1"></i>MST: ' + c.tax_id + '</small>');
      if (c.manager_email) verificationInfo.push('<small class="d-block"><i class="bi bi-envelope me-1"></i>' + c.manager_email + '</small>');
      if (c.verification_documents && Array.isArray(c.verification_documents) && c.verification_documents.length > 0) {
        verificationInfo.push('<small class="d-block"><i class="bi bi-paperclip me-1"></i>' + c.verification_documents.length + ' tài liệu</small>');
      }
      var verificationHtml = verificationInfo.length > 0 ? verificationInfo.join('') : '<small class="text-muted">Chưa có</small>';
      
      html += '<tr>';
      html += '<td>' + id + '</td>';
      html += '<td><strong>' + (c.name || c.clinic_name || '-') + '</strong></td>';
      html += '<td>' + (c.address || '-') + '</td>';
      html += '<td>' + verificationHtml + '</td>';
      html += '<td><span class="badge bg-' + badgeClass + '">' + status + '</span></td>';
      html += '<td>';
      if (status === 'pending') {
        html += '<button type="button" class="btn btn-sm btn-success me-1 btn-verify" data-id="' + id + '" title="Duyệt phòng khám"><i class="bi bi-check-circle"></i> Duyệt</button>';
        html += '<button type="button" class="btn btn-sm btn-danger me-1 btn-reject" data-id="' + id + '" title="Từ chối"><i class="bi bi-x-circle"></i> Từ chối</button>';
        html += '<button type="button" class="btn btn-sm btn-info btn-detail" data-id="' + id + '" title="Xem chi tiết"><i class="bi bi-eye"></i></button>';
      }
      if (status === 'verified') {
        html += '<button type="button" class="btn btn-sm btn-warning me-1 btn-suspend" data-id="' + id + '" title="Treo phòng khám"><i class="bi bi-pause-circle"></i> Treo</button>';
        html += '<button type="button" class="btn btn-sm btn-info btn-detail" data-id="' + id + '" title="Xem chi tiết"><i class="bi bi-eye"></i></button>';
      }
      if (status === 'suspended' || status === 'rejected') {
        html += '<button type="button" class="btn btn-sm btn-primary me-1 btn-approve" data-id="' + id + '" title="Phê duyệt/Gỡ treo"><i class="bi bi-check-circle"></i> Phê duyệt</button>';
        html += '<button type="button" class="btn btn-sm btn-info btn-detail" data-id="' + id + '" title="Xem chi tiết"><i class="bi bi-eye"></i></button>';
      }
      html += '</td></tr>';
    });
    clinicsTableBody.innerHTML = html;

    clinicsTableBody.querySelectorAll('.btn-verify').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        confirmAction({ type: 'verify', clinicId: id, title: 'Duyệt phòng khám', message: 'Duyệt phòng khám ID ' + id + '?', showReason: true, reasonLabel: 'Ghi chú (tùy chọn)' });
      });
    });
    clinicsTableBody.querySelectorAll('.btn-reject').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        confirmAction({ type: 'reject', clinicId: id, title: 'Từ chối phòng khám', message: 'Từ chối phòng khám ID ' + id + '?', showReason: true, reasonLabel: 'Lý do từ chối (tùy chọn)' });
      });
    });
    clinicsTableBody.querySelectorAll('.btn-approve').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        confirmAction({ type: 'approve', clinicId: id, title: 'Phê duyệt phòng khám', message: 'Phê duyệt / gỡ treo phòng khám ID ' + id + '?', showReason: true, reasonLabel: 'Ghi chú (tùy chọn)' });
      });
    });
    clinicsTableBody.querySelectorAll('.btn-suspend').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        confirmAction({ type: 'suspend', clinicId: id, title: 'Treo phòng khám', message: 'Treo phòng khám ID ' + id + '?', showReason: true, reasonLabel: 'Lý do treo (tùy chọn)' });
      });
    });
    clinicsTableBody.querySelectorAll('.btn-detail').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        showClinicDetail(id);
      });
    });
  }

  function showClinicDetail(clinicId) {
    window.AuraAPI.listClinics()
      .then(function (res) {
        var list = (res && res.clinics) ? res.clinics : [];
        var clinic = list.find(function (c) {
          return (c.clinic_id || c.id) == clinicId;
        });
        if (!clinic) {
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Không tìm thấy phòng khám', 'warning');
          return;
        }
        
        var detailHtml = '<div class="mb-3"><strong>Tên phòng khám:</strong> ' + (clinic.name || clinic.clinic_name || '-') + '</div>';
        detailHtml += '<div class="mb-3"><strong>Địa chỉ:</strong> ' + (clinic.address || '-') + '</div>';
        detailHtml += '<div class="mb-3"><strong>Số điện thoại:</strong> ' + (clinic.phone || '-') + '</div>';
        if (clinic.license_number) detailHtml += '<div class="mb-3"><strong>Số giấy phép:</strong> ' + clinic.license_number + '</div>';
        if (clinic.tax_id) detailHtml += '<div class="mb-3"><strong>Mã số thuế:</strong> ' + clinic.tax_id + '</div>';
        if (clinic.manager_email) detailHtml += '<div class="mb-3"><strong>Email quản lý:</strong> ' + clinic.manager_email + '</div>';
        if (clinic.verification_documents && Array.isArray(clinic.verification_documents) && clinic.verification_documents.length > 0) {
          detailHtml += '<div class="mb-3"><strong>Tài liệu xác minh:</strong><ul class="mb-0">';
          clinic.verification_documents.forEach(function (doc) {
            detailHtml += '<li><a href="' + doc + '" target="_blank">' + doc + '</a></li>';
          });
          detailHtml += '</ul></div>';
        }
        detailHtml += '<div class="mb-3"><strong>Trạng thái:</strong> <span class="badge bg-' + (clinic.verification_status === 'verified' ? 'success' : clinic.verification_status === 'pending' ? 'warning' : clinic.verification_status === 'rejected' ? 'danger' : 'secondary') + '">' + (clinic.verification_status || 'pending') + '</span></div>';
        detailHtml += '<div class="mb-0"><strong>Ngày tạo:</strong> ' + (clinic.created_at ? new Date(clinic.created_at).toLocaleString('vi-VN') : '-') + '</div>';
        
        if (modalActionMessage) {
          modalActionMessage.innerHTML = detailHtml;
          modalActionTitle.textContent = 'Chi tiết phòng khám #' + clinicId;
          if (wrapReason) wrapReason.classList.add('d-none');
          if (btnConfirmAction) btnConfirmAction.style.display = 'none';
          var modal = bootstrap.Modal.getOrCreateInstance(modalAction);
          if (modal) modal.show();
          
          // Restore button when modal is hidden
          modalAction.addEventListener('hidden.bs.modal', function handler() {
            if (btnConfirmAction) btnConfirmAction.style.display = '';
            modalAction.removeEventListener('hidden.bs.modal', handler);
          });
        }
      })
      .catch(function (e) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
      });
  }

  function confirmAction(opts) {
    pendingAction = opts;
    if (modalActionTitle) modalActionTitle.textContent = opts.title || 'Xác nhận';
    if (modalActionMessage) modalActionMessage.textContent = opts.message || '';
    if (wrapReason) {
      wrapReason.classList.toggle('d-none', !opts.showReason);
      if (labelReason) labelReason.textContent = opts.reasonLabel || 'Lý do';
    }
    if (inputReason) inputReason.value = '';
    var modal = bootstrap.Modal.getOrCreateInstance(modalAction);
    if (modal) modal.show();
  }

  function doAction() {
    if (!pendingAction) return;
    var clinicId = pendingAction.clinicId;
    var reason = (inputReason && inputReason.value) ? inputReason.value.trim() : '';
    var promise;
    switch (pendingAction.type) {
      case 'verify':
        promise = window.AuraAPI.verifyClinic(clinicId, reason);
        break;
      case 'reject':
        promise = window.AuraAPI.rejectClinic(clinicId, reason);
        break;
      case 'approve':
        promise = window.AuraAPI.approveClinic(clinicId, reason);
        break;
      case 'suspend':
        promise = window.AuraAPI.suspendClinic(clinicId, reason);
        break;
      default:
        return;
    }
    promise
      .then(function () {
        var modal = bootstrap.Modal.getOrCreateInstance(modalAction);
        if (modal) modal.hide();
        pendingAction = null;
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã thực hiện.', 'success');
        loadClinics();
      })
      .catch(function (e) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
      });
  }

  if (btnReload) btnReload.addEventListener('click', loadClinics);
  if (filterStatus) filterStatus.addEventListener('change', loadClinics);
  if (btnConfirmAction) btnConfirmAction.addEventListener('click', doAction);

  loadClinics();
})();
