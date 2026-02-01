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
      clinicsTableBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Không có phòng khám</td></tr>';
      return;
    }
    var html = '';
    list.forEach(function (c) {
      var id = c.clinic_id != null ? c.clinic_id : c.id;
      var status = (c.verification_status || c.status || 'pending');
      var badgeClass = status === 'verified' ? 'success' : status === 'pending' ? 'warning' : status === 'rejected' ? 'danger' : status === 'suspended' ? 'secondary' : 'secondary';
      html += '<tr>';
      html += '<td>' + id + '</td>';
      html += '<td>' + (c.name || c.clinic_name || '-') + '</td>';
      html += '<td>' + (c.address || '-') + '</td>';
      html += '<td><span class="badge bg-' + badgeClass + '">' + status + '</span></td>';
      html += '<td>';
      if (status === 'pending') {
        html += '<button type="button" class="btn btn-sm btn-success me-1 btn-verify" data-id="' + id + '">Duyệt</button>';
        html += '<button type="button" class="btn btn-sm btn-danger me-1 btn-reject" data-id="' + id + '">Từ chối</button>';
      }
      if (status === 'verified') {
        html += '<button type="button" class="btn btn-sm btn-warning me-1 btn-suspend" data-id="' + id + '">Treo</button>';
      }
      if (status === 'suspended' || status === 'rejected') {
        html += '<button type="button" class="btn btn-sm btn-primary me-1 btn-approve" data-id="' + id + '">Phê duyệt</button>';
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