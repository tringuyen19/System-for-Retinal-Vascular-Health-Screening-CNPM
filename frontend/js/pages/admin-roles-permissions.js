/**
 * AURA - Admin Roles & Permissions Management (FR-32)
 * Integrated into accounts page
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var rolesList = document.getElementById('rolesList');
  var selectedRoleId = document.getElementById('selectedRoleId');
  var selectedRoleName = document.getElementById('selectedRoleName');
  var permissionsMatrix = document.getElementById('permissionsMatrix');
  var btnCreateRole = document.getElementById('btnCreateRole');

  var roles = [];
  var allPermissions = [];
  var currentRolePermissions = [];

  // Load roles
  function loadRoles() {
    if (!rolesList) return;
    rolesList.innerHTML = '<div class="p-3 text-center text-muted">Đang tải...</div>';
    
    window.AuraAPI.getAllRoles()
      .then(function (res) {
        roles = (res && res.roles) ? res.roles : [];
        renderRolesList(roles);
      })
      .catch(function (e) {
        rolesList.innerHTML = '<div class="p-3 text-center text-danger">Lỗi tải vai trò</div>';
      });
  }

  function renderRolesList(list) {
    if (!rolesList) return;
    if (!list || list.length === 0) {
      rolesList.innerHTML = '<div class="p-3 text-center text-muted">Không có vai trò</div>';
      return;
    }
    var html = '';
    list.forEach(function (r) {
      var id = r.role_id || r.id;
      var name = r.role_name || r.name || id;
      html += '<a href="#" class="list-group-item list-group-item-action role-item" data-id="' + id + '" data-name="' + name + '">';
      html += '<div class="d-flex w-100 justify-content-between align-items-center">';
      html += '<span>' + name + '</span>';
      html += '<span class="badge bg-info">' + (r.permission_count || 0) + ' quyền</span>';
      html += '</div></a>';
    });
    rolesList.innerHTML = html;

    // Add click handlers
    rolesList.querySelectorAll('.role-item').forEach(function (item) {
      item.addEventListener('click', function (e) {
        e.preventDefault();
        var id = this.getAttribute('data-id');
        var name = this.getAttribute('data-name');
        selectRole(id, name);
      });
    });
  }

  function selectRole(roleId, roleName) {
    if (selectedRoleId) selectedRoleId.value = roleId;
    if (selectedRoleName) selectedRoleName.textContent = roleName;

    // Load permissions for this role
    window.AuraAPI.getPermissionsByRole(roleId)
      .then(function (res) {
        currentRolePermissions = (res && res.permissions) ? res.permissions : [];
        renderPermissionsMatrix(currentRolePermissions);
      })
      .catch(function (e) {
        if (window.AuraAlert && window.AuraAlert.toast) {
          window.AuraAlert.toast('Lỗi tải quyền: ' + (e.message || ''), 'danger');
        }
      });
  }

  function renderPermissionsMatrix(permissions) {
    if (!permissionsMatrix) return;

    // Group permissions by resource
    var grouped = {};
    permissions.forEach(function (p) {
      var resource = p.resource || 'Other';
      if (!grouped[resource]) grouped[resource] = [];
      grouped[resource].push(p);
    });

    var html = '<div class="row g-3">';
    Object.keys(grouped).forEach(function (resource) {
      html += '<div class="col-md-6">';
      html += '<div class="card border-0 bg-light">';
      html += '<div class="card-header bg-white"><strong>' + resource + '</strong></div>';
      html += '<div class="card-body">';
      grouped[resource].forEach(function (p) {
        var permId = p.permission_id || p.id;
        var action = p.action || '';
        html += '<div class="form-check mb-2">';
        html += '<input class="form-check-input permission-check" type="checkbox" value="' + permId + '" id="perm' + permId + '" checked>';
        html += '<label class="form-check-label" for="perm' + permId + '"><strong>' + action + '</strong></label>';
        html += '</div>';
      });
      html += '</div></div></div>';
    });
    html += '</div>';
    html += '<div class="mt-3">';
    html += '<button type="button" class="btn btn-primary" id="btnSaveRolePermissions">Lưu quyền</button>';
    html += '</div>';

    permissionsMatrix.innerHTML = html;

    // Add save handler
    var btnSave = document.getElementById('btnSaveRolePermissions');
    if (btnSave) {
      btnSave.addEventListener('click', function () {
        var roleId = selectedRoleId && selectedRoleId.value ? selectedRoleId.value : '';
        if (!roleId) {
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Chọn vai trò', 'warning');
          return;
        }
        var checked = Array.from(document.querySelectorAll('.permission-check:checked')).map(function (el) {
          return el.value;
        });
        window.AuraAPI.assignPermissionsToRole(roleId, checked)
          .then(function () {
            if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã lưu quyền', 'success');
          })
          .catch(function (e) {
            if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi lưu quyền', 'danger');
          });
      });
    }
  }

  // Initialize
  loadRoles();
  
  // Refresh when tab is shown
  var rolesTab = document.getElementById('tab-roles');
  if (rolesTab) {
    rolesTab.addEventListener('shown.bs.tab', function () {
      loadRoles();
    });
  }
})();
