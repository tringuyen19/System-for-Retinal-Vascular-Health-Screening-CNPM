/**
 * AURA - Admin Accounts
 * Danh sách tài khoản, lọc theo role/status, tạo/sửa/đổi trạng thái/xóa
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var pageError = document.getElementById('pageError');
  var filterRole = document.getElementById('filterRole');
  var filterStatus = document.getElementById('filterStatus');
  var btnReload = document.getElementById('btnReload');
  var btnCreate = document.getElementById('btnCreate');
  var accountsTableBody = document.getElementById('accountsTableBody');
  var modalAccount = document.getElementById('modalAccount');
  var modalAccountTitle = document.getElementById('modalAccountTitle');
  var accountId = document.getElementById('accountId');
  var accountEmail = document.getElementById('accountEmail');
  var accountPassword = document.getElementById('accountPassword');
  var wrapPassword = document.getElementById('wrapPassword');
  var accountRoleId = document.getElementById('accountRoleId');
  var accountClinicId = document.getElementById('accountClinicId');
  var accountStatus = document.getElementById('accountStatus');
  var wrapStatus = document.getElementById('wrapStatus');
  var btnSaveAccount = document.getElementById('btnSaveAccount');

  var roles = [];
  var accounts = [];

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function loadRoles() {
    return window.AuraAPI.getAllRoles().then(function (res) {
      roles = (res && res.roles) ? res.roles : [];
      var opts = '<option value="">Tất cả vai trò</option>';
      roles.forEach(function (r) {
        opts += '<option value="' + (r.role_id || r.id) + '">' + (r.role_name || r.name || r.role_id) + '</option>';
      });
      if (filterRole) filterRole.innerHTML = opts;
      var modalOpts = '';
      roles.forEach(function (r) {
        var id = r.role_id != null ? r.role_id : r.id;
        modalOpts += '<option value="' + id + '">' + (r.role_name || r.name || id) + '</option>';
      });
      if (accountRoleId) accountRoleId.innerHTML = modalOpts;
      return roles;
    });
  }

  function loadAccounts() {
    var roleVal = filterRole && filterRole.value ? filterRole.value : '';
    var statusVal = filterStatus && filterStatus.value ? filterStatus.value : '';
    if (accountsTableBody) accountsTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Đang tải...</td></tr>';
    var promise;
    if (statusVal) {
      promise = window.AuraAPI.getAccountsByStatus(statusVal).then(function (res) {
        return (res && res.accounts) ? res.accounts : [];
      });
    } else if (roleVal) {
      promise = window.AuraAPI.getAccountsByRole(roleVal).then(function (res) {
        return (res && res.accounts) ? res.accounts : [];
      });
    } else {
      promise = window.AuraAPI.getAllAccounts().then(function (res) {
        return (res && res.accounts) ? res.accounts : [];
      });
    }
    promise
      .then(function (list) {
        accounts = list || [];
        if (roleVal && statusVal) {
          accounts = accounts.filter(function (a) {
            return String(a.role_id) === roleVal && (a.status || '') === statusVal;
          });
        } else if (roleVal && list) {
          accounts = list;
        }
        renderTable(accounts);
      })
      .catch(function (err) {
        showError(err.message || 'Tải danh sách thất bại.');
        if (accountsTableBody) accountsTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Lỗi tải dữ liệu</td></tr>';
      });
  }

  function renderTable(list) {
    if (!accountsTableBody) return;
    if (!list || list.length === 0) {
      accountsTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Không có tài khoản</td></tr>';
      return;
    }
    var roleMap = {};
    roles.forEach(function (r) {
      roleMap[r.role_id != null ? r.role_id : r.id] = r.role_name || r.name || '';
    });
    var html = '';
    list.forEach(function (a) {
      var id = a.account_id != null ? a.account_id : a.id;
      var roleName = roleMap[a.role_id] || a.role_id || '-';
      var status = (a.status || 'active');
      html += '<tr>';
      html += '<td>' + id + '</td>';
      html += '<td>' + (a.email || '-') + '</td>';
      html += '<td>' + roleName + '</td>';
      html += '<td><span class="badge bg-' + (status === 'active' ? 'success' : status === 'suspended' ? 'danger' : 'secondary') + '">' + status + '</span></td>';
      html += '<td>' + (a.clinic_id != null ? a.clinic_id : '-') + '</td>';
      html += '<td>';
      html += '<button type="button" class="btn btn-sm btn-outline-primary me-1 btn-edit" data-id="' + id + '">Sửa</button>';
      html += '<button type="button" class="btn btn-sm btn-outline-warning me-1 btn-status" data-id="' + id + '" data-status="' + status + '">Trạng thái</button>';
      html += '<button type="button" class="btn btn-sm btn-outline-danger btn-delete" data-id="' + id + '">Xóa</button>';
      html += '</td></tr>';
    });
    accountsTableBody.innerHTML = html;

    accountsTableBody.querySelectorAll('.btn-edit').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        openModalEdit(id);
      });
    });
    accountsTableBody.querySelectorAll('.btn-status').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        var cur = this.getAttribute('data-status');
        var next = cur === 'active' ? 'suspended' : 'active';
        if (confirm('Đổi trạng thái tài khoản ' + id + ' sang "' + next + '"?')) {
          window.AuraAPI.updateAccountStatus(id, next)
            .then(function () {
              if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã cập nhật trạng thái.', 'success');
              loadAccounts();
            })
            .catch(function (e) {
              if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
            });
        }
      });
    });
    accountsTableBody.querySelectorAll('.btn-delete').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        if (confirm('Xóa tài khoản ID ' + id + '? Không thể hoàn tác.')) {
          window.AuraAPI.deleteAccount(id)
            .then(function () {
              if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã xóa tài khoản.', 'success');
              loadAccounts();
            })
            .catch(function (e) {
              if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
            });
        }
      });
    });
  }

  function openModalCreate() {
    if (modalAccountTitle) modalAccountTitle.textContent = 'Tạo tài khoản';
    if (accountId) accountId.value = '';
    if (accountEmail) accountEmail.value = '';
    if (accountPassword) accountPassword.value = '';
    if (accountClinicId) accountClinicId.value = '';
    if (accountStatus) accountStatus.value = 'active';
    if (wrapPassword) wrapPassword.style.display = '';
    if (accountPassword) accountPassword.required = true;
    if (wrapStatus) wrapStatus.style.display = 'none';
    if (roles.length && accountRoleId) accountRoleId.selectedIndex = 0;
    var modal = bootstrap.Modal.getOrCreateInstance(modalAccount);
    if (modal) modal.show();
  }

  function openModalEdit(id) {
    var acc = accounts.find(function (a) { return String(a.account_id || a.id) === String(id); });
    if (!acc) return;
    if (modalAccountTitle) modalAccountTitle.textContent = 'Sửa tài khoản';
    if (accountId) accountId.value = id;
    if (accountEmail) accountEmail.value = acc.email || '';
    if (accountEmail) accountEmail.readOnly = true;
    if (accountPassword) accountPassword.value = '';
    if (wrapPassword) wrapPassword.style.display = '';
    if (accountPassword) accountPassword.required = false;
    if (accountPassword) accountPassword.placeholder = 'Để trống nếu không đổi';
    if (accountClinicId) accountClinicId.value = acc.clinic_id != null ? acc.clinic_id : '';
    if (accountStatus) accountStatus.value = acc.status || 'active';
    if (wrapStatus) wrapStatus.style.display = '';
    if (accountRoleId) {
      for (var i = 0; i < accountRoleId.options.length; i++) {
        if (String(accountRoleId.options[i].value) === String(acc.role_id)) {
          accountRoleId.selectedIndex = i;
          break;
        }
      }
    }
    var modal = bootstrap.Modal.getOrCreateInstance(modalAccount);
    if (modal) modal.show();
  }

  function saveAccount() {
    var id = accountId && accountId.value ? accountId.value.trim() : '';
    var email = accountEmail && accountEmail.value ? accountEmail.value.trim() : '';
    var password = accountPassword && accountPassword.value ? accountPassword.value : '';
    var roleId = accountRoleId && accountRoleId.value ? accountRoleId.value : '';
    var clinicId = accountClinicId && accountClinicId.value ? accountClinicId.value.trim() : '';
    var status = accountStatus && accountStatus.value ? accountStatus.value : 'active';

    if (!email) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Nhập email.', 'warning');
      return;
    }
    if (!id && !password) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Nhập mật khẩu khi tạo mới.', 'warning');
      return;
    }
    if (!roleId) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Chọn vai trò.', 'warning');
      return;
    }

    var payload = {
      email: email,
      role_id: parseInt(roleId, 10),
      status: status
    };
    if (clinicId) payload.clinic_id = parseInt(clinicId, 10);
    if (!id) payload.password = password;

    var promise;
    if (id) {
      delete payload.email;
      delete payload.password;
      promise = window.AuraAPI.updateAccountById(id, payload);
    } else {
      promise = window.AuraAPI.createAccount(payload);
    }
    promise
      .then(function () {
        var modal = bootstrap.Modal.getOrCreateInstance(modalAccount);
        if (modal) modal.hide();
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(id ? 'Đã cập nhật.' : 'Đã tạo tài khoản.', 'success');
        loadAccounts();
      })
      .catch(function (e) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
      });
  }

  if (btnReload) btnReload.addEventListener('click', loadAccounts);
  if (btnCreate) btnCreate.addEventListener('click', openModalCreate);
  if (btnSaveAccount) btnSaveAccount.addEventListener('click', saveAccount);
  if (filterRole) filterRole.addEventListener('change', loadAccounts);
  if (filterStatus) filterStatus.addEventListener('change', loadAccounts);

  loadRoles().then(function () {
    loadAccounts();
  }).catch(function (err) {
    showError(err.message || 'Tải vai trò thất bại.');
  });
})();