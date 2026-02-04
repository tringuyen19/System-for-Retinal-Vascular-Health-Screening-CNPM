/**
 * AURA - Admin Accounts (FR-31)
 * Quản lý tài khoản người dùng, bác sĩ và phòng khám: danh sách, lọc, tạo/sửa/trạng thái/xóa, đổi mật khẩu, tạo hồ sơ bác sĩ.
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var pageError = document.getElementById('pageError');
  var filterRole = document.getElementById('filterRole');
  var filterStatus = document.getElementById('filterStatus');
  var filterSearch = document.getElementById('filterSearch');
  var btnReload = document.getElementById('btnReload');
  var btnCreate = document.getElementById('btnCreate');
  var accountsTableBody = document.getElementById('accountsTableBody');
  var modalAccount = document.getElementById('modalAccount');
  var modalAccountTitle = document.getElementById('modalAccountTitle');
  var accountId = document.getElementById('accountId');
  var accountEmail = document.getElementById('accountEmail');
  var accountPassword = document.getElementById('accountPassword');
  var labelPassword = document.getElementById('labelPassword');
  var wrapPassword = document.getElementById('wrapPassword');
  var accountRoleId = document.getElementById('accountRoleId');
  var accountClinicId = document.getElementById('accountClinicId');
  var accountStatus = document.getElementById('accountStatus');
  var wrapStatus = document.getElementById('wrapStatus');
  var wrapClinic = document.getElementById('wrapClinic');
  var wrapClinicCreate = document.getElementById('wrapClinicCreate');
  var newClinicName = document.getElementById('newClinicName');
  var newClinicAddress = document.getElementById('newClinicAddress');
  var newClinicPhone = document.getElementById('newClinicPhone');
  var newClinicLogoUrl = document.getElementById('newClinicLogoUrl');
  var newClinicLicenseNumber = document.getElementById('newClinicLicenseNumber');
  var newClinicTaxId = document.getElementById('newClinicTaxId');
  var newClinicVerificationDocs = document.getElementById('newClinicVerificationDocs');
  var btnSaveAccount = document.getElementById('btnSaveAccount');

  var modalDoctorProfile = document.getElementById('modalDoctorProfile');
  var doctorProfileAccountId = document.getElementById('doctorProfileAccountId');
  var doctorName = document.getElementById('doctorName');
  var doctorSpecialization = document.getElementById('doctorSpecialization');
  var doctorLicense = document.getElementById('doctorLicense');
  var btnSaveDoctorProfile = document.getElementById('btnSaveDoctorProfile');

  var modalPatientProfile = document.getElementById('modalPatientProfile');
  var patientProfileAccountId = document.getElementById('patientProfileAccountId');
  var patientName = document.getElementById('patientName');
  var patientDob = document.getElementById('patientDob');
  var patientGender = document.getElementById('patientGender');
  var patientMedicalHistory = document.getElementById('patientMedicalHistory');
  var btnSavePatientProfile = document.getElementById('btnSavePatientProfile');

  var roles = [];
  var accounts = [];
  var doctors = [];
  var patients = [];
  var clinics = [];
  var doctorByAccountId = {};
  var patientByAccountId = {};
  var clinicById = {};
  var roleMap = {};

  function updateClinicVisibility() {
    if (!wrapClinic) return;
    var roleId = accountRoleId && accountRoleId.value ? String(accountRoleId.value) : '';
    var roleName = roleMap[roleId] || '';
    var isCreate = !(accountId && accountId.value && String(accountId.value).trim());
    var isClinicManagerCreate = roleName === 'ClinicManager' && isCreate;

    // ClinicManager create => tạo clinic mới (không chọn clinic có sẵn)
    if (wrapClinicCreate) wrapClinicCreate.classList.toggle('d-none', !isClinicManagerCreate);

    // Clinic select: show for Doctor/Patient; hide for Admin; hide for ClinicManager create
    var showSelect = (roleName === 'Doctor' || roleName === 'Patient' || (roleName === 'ClinicManager' && !isCreate));
    wrapClinic.style.display = showSelect ? '' : 'none';
    if (!showSelect && accountClinicId) accountClinicId.value = '';

    // Với ClinicManager edit: tránh đổi clinic_id nhầm
    if (accountClinicId) accountClinicId.disabled = (roleName === 'ClinicManager' && !isCreate);
  }

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function getCurrentUser() {
    try {
      return (window.AuraAuth && window.AuraAuth.getUser && window.AuraAuth.getUser()) || null;
    } catch (e) {
      return null;
    }
  }

  function loadRoles() {
    return window.AuraAPI.getAllRoles().then(function (res) {
      roles = (res && res.roles) ? res.roles : [];
      roleMap = {};
      var opts = '<option value="">Tất cả vai trò</option>';
      roles.forEach(function (r) {
        var id = r.role_id != null ? r.role_id : r.id;
        var name = r.role_name || r.name || id;
        roleMap[id] = name;
        opts += '<option value="' + id + '">' + name + '</option>';
      });
      if (filterRole) filterRole.innerHTML = opts;
      var modalOpts = '';
      roles.forEach(function (r) {
        var id = r.role_id != null ? r.role_id : r.id;
        modalOpts += '<option value="' + id + '">' + (r.role_name || r.name || id) + '</option>';
      });
      if (accountRoleId) accountRoleId.innerHTML = modalOpts;
      updateClinicVisibility();
      return roles;
    });
  }

  function loadClinicsForSelect() {
    return window.AuraAPI.listClinics().then(function (res) {
      var list = (res && res.clinics) ? res.clinics : [];
      clinics = list;
      clinicById = {};
      list.forEach(function (c) {
        var id = c.clinic_id != null ? c.clinic_id : c.id;
        clinicById[id] = c;
      });
      var opts = '<option value="">-- Chọn phòng khám (nếu Quản lý phòng khám) --</option>';
      list.forEach(function (c) {
        var id = c.clinic_id != null ? c.clinic_id : c.id;
        var name = c.name || c.clinic_name || 'ID ' + id;
        opts += '<option value="' + id + '">' + name + ' (' + (c.verification_status || '') + ')</option>';
      });
      if (accountClinicId) accountClinicId.innerHTML = opts;
      updateClinicVisibility();
      return list;
    });
  }

  function loadDoctors() {
    return window.AuraAPI.getAllDoctors().then(function (res) {
      var list = (res && res.doctors) ? res.doctors : [];
      doctors = list;
      doctorByAccountId = {};
      list.forEach(function (d) {
        var aid = d.account_id != null ? d.account_id : d.account_id;
        if (aid != null) doctorByAccountId[aid] = d;
      });
      return list;
    });
  }

  function loadPatients() {
    return window.AuraAPI.getAllPatients().then(function (res) {
      var list = (res && res.patients) ? res.patients : [];
      patients = list;
      patientByAccountId = {};
      list.forEach(function (p) {
        var aid = p.account_id != null ? p.account_id : p.account_id;
        if (aid != null) patientByAccountId[aid] = p;
      });
      return list;
    });
  }

  function loadAccounts() {
    var roleVal = filterRole && filterRole.value ? filterRole.value : '';
    var statusVal = filterStatus && filterStatus.value ? filterStatus.value : '';
    if (accountsTableBody) accountsTableBody.innerHTML = '<tr><td colspan="7" class="text-center">Đang tải...</td></tr>';
    var promise;
    if (statusVal && roleVal) {
      promise = window.AuraAPI.getAllAccounts().then(function (res) {
        var list = (res && res.accounts) ? res.accounts : [];
        return list.filter(function (a) {
          return String(a.role_id) === roleVal && (a.status || '') === statusVal;
        });
      });
    } else if (statusVal) {
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
        var search = (filterSearch && filterSearch.value) ? filterSearch.value.trim().toLowerCase() : '';
        if (search) {
          accounts = accounts.filter(function (a) {
            return (a.email || '').toLowerCase().indexOf(search) !== -1;
          });
        }
        renderTable(accounts);
      })
      .catch(function (err) {
        showError(err.message || 'Tải danh sách thất bại.');
        if (accountsTableBody) accountsTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Lỗi tải dữ liệu</td></tr>';
      });
  }

  function formatDate(d) {
    if (!d) return '-';
    try {
      var dt = typeof d === 'string' ? new Date(d) : d;
      return dt.toLocaleDateString('vi-VN') + ' ' + dt.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return d;
    }
  }

  function renderTable(list) {
    if (!accountsTableBody) return;
    if (!list || list.length === 0) {
      accountsTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Không có tài khoản</td></tr>';
      return;
    }
    var currentUser = getCurrentUser();
    var currentAccountId = currentUser && currentUser.account_id != null ? String(currentUser.account_id) : null;
    var html = '';
    list.forEach(function (a) {
      var id = a.account_id != null ? a.account_id : a.id;
      var roleName = roleMap[a.role_id] || a.role_id || '-';
      var status = (a.status || 'active');
      var statusLabel = status === 'active' ? 'Hoạt động' : status === 'suspended' ? 'Đình chỉ' : 'Không HĐ';
      var statusClass = status === 'active' ? 'success' : status === 'suspended' ? 'danger' : 'secondary';
      var extra = '';
      var doc = doctorByAccountId[a.account_id != null ? a.account_id : a.id];
      var pat = patientByAccountId[a.account_id != null ? a.account_id : a.id];
      if (doc) {
        extra = '<span class="text-primary"><i class="bi bi-person-badge me-1"></i>' + (doc.doctor_name || '-') + '</span>';
        if (doc.specialization) extra += ' <small class="text-muted">' + doc.specialization + '</small>';
      } else if (pat) {
        extra = '<span class="text-success"><i class="bi bi-person-heart me-1"></i>' + (pat.patient_name || '-') + '</span>';
      } else if (a.clinic_id != null && clinicById[a.clinic_id]) {
        extra = '<span class="text-info"><i class="bi bi-building me-1"></i>' + (clinicById[a.clinic_id].name || clinicById[a.clinic_id].clinic_name || '') + '</span>';
      } else {
        extra = '<span class="text-muted">-</span>';
      }
      html += '<tr>';
      html += '<td>' + id + '</td>';
      html += '<td>' + (a.email || '-') + '</td>';
      html += '<td>' + roleName + '</td>';
      html += '<td><span class="badge bg-' + statusClass + '">' + statusLabel + '</span></td>';
      html += '<td>' + extra + '</td>';
      html += '<td>' + formatDate(a.created_at) + '</td>';
      html += '<td>';
      html += '<button type="button" class="btn btn-sm btn-outline-primary me-1 btn-edit" data-id="' + id + '" title="Sửa">Sửa</button>';
      if (roleMap[a.role_id] === 'Doctor' && !doc) {
        html += '<button type="button" class="btn btn-sm btn-outline-info me-1 btn-create-doctor" data-id="' + id + '" title="Tạo hồ sơ bác sĩ">Hồ sơ BS</button>';
      }
      if (roleMap[a.role_id] === 'Patient' && !pat) {
        html += '<button type="button" class="btn btn-sm btn-outline-success me-1 btn-create-patient" data-id="' + id + '" title="Tạo hồ sơ bệnh nhân">Hồ sơ BN</button>';
      }
      html += '<button type="button" class="btn btn-sm btn-outline-warning me-1 btn-status" data-id="' + id + '" data-status="' + status + '" title="Đổi trạng thái">TT</button>';
      var isSelf = currentAccountId && String(id) === currentAccountId;
      if (isSelf) {
        html += '<button type="button" class="btn btn-sm btn-outline-secondary" disabled title="Không thể xóa tài khoản của chính bạn">Xóa</button>';
      } else {
        html += '<button type="button" class="btn btn-sm btn-outline-danger btn-delete" data-id="' + id + '" title="Xóa">Xóa</button>';
      }
      html += '</td></tr>';
    });
    accountsTableBody.innerHTML = html;

    accountsTableBody.querySelectorAll('.btn-edit').forEach(function (btn) {
      btn.addEventListener('click', function () {
        openModalEdit(this.getAttribute('data-id'));
      });
    });
    accountsTableBody.querySelectorAll('.btn-create-doctor').forEach(function (btn) {
      btn.addEventListener('click', function () {
        openModalDoctorProfile(this.getAttribute('data-id'));
      });
    });
    accountsTableBody.querySelectorAll('.btn-create-patient').forEach(function (btn) {
      btn.addEventListener('click', function () {
        openModalPatientProfile(this.getAttribute('data-id'));
      });
    });
    accountsTableBody.querySelectorAll('.btn-status').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        var cur = this.getAttribute('data-status');
        var next = cur === 'active' ? 'suspended' : 'active';
        if (confirm('Đổi trạng thái tài khoản sang "' + (next === 'active' ? 'Hoạt động' : 'Đình chỉ') + '"?')) {
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
        if (currentAccountId && String(id) === currentAccountId) {
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Không thể xóa tài khoản của chính bạn.', 'warning');
          return;
        }
        if (confirm('Xóa tài khoản ID ' + id + '? Hành động không thể hoàn tác.')) {
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
    if (accountEmail) { accountEmail.value = ''; accountEmail.readOnly = false; accountEmail.required = true; }
    if (accountPassword) { accountPassword.value = ''; accountPassword.required = true; accountPassword.placeholder = 'Tối thiểu 6 ký tự'; }
    if (labelPassword) labelPassword.innerHTML = 'Mật khẩu <span class="text-danger">*</span>';
    if (wrapPassword) wrapPassword.style.display = '';
    if (accountClinicId) accountClinicId.value = '';
    if (accountStatus) accountStatus.value = 'active';
    if (wrapStatus) wrapStatus.style.display = 'none';
    if (accountRoleId && roles.length) accountRoleId.selectedIndex = 0;
    if (newClinicName) newClinicName.value = '';
    if (newClinicAddress) newClinicAddress.value = '';
    if (newClinicPhone) newClinicPhone.value = '';
    if (newClinicLogoUrl) newClinicLogoUrl.value = '';
    if (newClinicLicenseNumber) newClinicLicenseNumber.value = '';
    if (newClinicTaxId) newClinicTaxId.value = '';
    if (newClinicVerificationDocs) newClinicVerificationDocs.value = '';
    updateClinicVisibility();
    var modal = bootstrap.Modal.getOrCreateInstance(modalAccount);
    if (modal) modal.show();
  }

  function openModalEdit(id) {
    var acc = accounts.find(function (a) { return String(a.account_id || a.id) === String(id); });
    if (!acc) return;
    if (modalAccountTitle) modalAccountTitle.textContent = 'Sửa tài khoản';
    if (accountId) accountId.value = id;
    if (accountEmail) { accountEmail.value = acc.email || ''; accountEmail.readOnly = true; accountEmail.required = false; }
    if (accountPassword) { accountPassword.value = ''; accountPassword.required = false; accountPassword.placeholder = 'Để trống nếu không đổi mật khẩu'; }
    if (labelPassword) labelPassword.innerHTML = 'Mật khẩu mới (tùy chọn)';
    if (wrapPassword) wrapPassword.style.display = '';
    if (accountClinicId) {
      accountClinicId.value = acc.clinic_id != null ? acc.clinic_id : '';
    }
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
    updateClinicVisibility();
    var modal = bootstrap.Modal.getOrCreateInstance(modalAccount);
    if (modal) modal.show();
  }

  function saveAccount() {
    var id = accountId && accountId.value ? accountId.value.trim() : '';
    var email = accountEmail && accountEmail.value ? accountEmail.value.trim() : '';
    var password = accountPassword && accountPassword.value ? accountPassword.value : '';
    var roleId = accountRoleId && accountRoleId.value ? accountRoleId.value : '';
    var clinicIdVal = accountClinicId && accountClinicId.value ? accountClinicId.value.trim() : '';
    var status = accountStatus && accountStatus.value ? accountStatus.value : 'active';

    if (!email) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Vui lòng nhập email.', 'warning');
      return;
    }
    var roleName = roleMap[roleId] || '';
    // ClinicManager create => tạo clinic mới + manager account
    if (roleName === 'ClinicManager' && !id) {
      if (!password || password.length < 6) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Mật khẩu tối thiểu 6 ký tự khi tạo mới.', 'warning');
        return;
      }
      var cName = newClinicName && newClinicName.value ? newClinicName.value.trim() : '';
      var cAddr = newClinicAddress && newClinicAddress.value ? newClinicAddress.value.trim() : '';
      var cPhone = newClinicPhone && newClinicPhone.value ? newClinicPhone.value.trim() : '';
      if (!cName || !cAddr || !cPhone) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Vui lòng nhập đủ: Tên phòng khám, Địa chỉ, Số điện thoại.', 'warning');
        return;
      }
      var docsRaw = newClinicVerificationDocs && newClinicVerificationDocs.value ? newClinicVerificationDocs.value : '';
      var docs = docsRaw
        ? docsRaw.split(/\r?\n|,/).map(function (s) { return s.trim(); }).filter(Boolean)
        : null;
      var clinicPayload = {
        name: cName,
        address: cAddr,
        phone: cPhone,
        manager_email: email,
        manager_password: password
      };
      var logo = newClinicLogoUrl && newClinicLogoUrl.value ? newClinicLogoUrl.value.trim() : '';
      if (logo) clinicPayload.logo_url = logo;
      var lic = newClinicLicenseNumber && newClinicLicenseNumber.value ? newClinicLicenseNumber.value.trim() : '';
      if (lic) clinicPayload.license_number = lic;
      var tax = newClinicTaxId && newClinicTaxId.value ? newClinicTaxId.value.trim() : '';
      if (tax) clinicPayload.tax_id = tax;
      if (docs && docs.length) clinicPayload.verification_documents = docs;

      window.AuraAPI.registerClinic(clinicPayload)
        .then(function () {
          var modal = bootstrap.Modal.getOrCreateInstance(modalAccount);
          if (modal) modal.hide();
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã tạo phòng khám mới và tài khoản quản lý (pending).', 'success');
          loadClinicsForSelect();
          loadAccounts();
        })
        .catch(function (e) {
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
        });
      return;
    }
    if (!id) {
      if (!password || password.length < 6) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Mật khẩu tối thiểu 6 ký tự khi tạo mới.', 'warning');
        return;
      }
    }
    if (!roleId) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Vui lòng chọn vai trò.', 'warning');
      return;
    }

    var clinicId = clinicIdVal ? parseInt(clinicIdVal, 10) : null;
    var payload = {
      email: email,
      role_id: parseInt(roleId, 10),
      status: status
    };
    if (clinicId != null) payload.clinic_id = clinicId;
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
        if (id && password) {
          return window.AuraAPI.updateAccountPassword(id, password).then(function () {
            return { passwordUpdated: true };
          });
        }
        return {};
      })
      .then(function (result) {
        var modal = bootstrap.Modal.getOrCreateInstance(modalAccount);
        if (modal) modal.hide();
        if (window.AuraAlert && window.AuraAlert.toast) {
          window.AuraAlert.toast(id ? (result.passwordUpdated ? 'Đã cập nhật và đổi mật khẩu.' : 'Đã cập nhật.') : 'Đã tạo tài khoản.', 'success');
        }
        loadAccounts();
        loadDoctors();
        loadPatients();
      })
      .catch(function (e) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
      });
  }

  function openModalPatientProfile(accountIdVal) {
    if (patientProfileAccountId) patientProfileAccountId.value = accountIdVal;
    if (patientName) patientName.value = '';
    if (patientDob) patientDob.value = '';
    if (patientGender) patientGender.value = '';
    if (patientMedicalHistory) patientMedicalHistory.value = '';
    var modal = bootstrap.Modal.getOrCreateInstance(modalPatientProfile);
    if (modal) modal.show();
  }

  function savePatientProfile() {
    var accId = patientProfileAccountId && patientProfileAccountId.value ? patientProfileAccountId.value.trim() : '';
    var name = patientName && patientName.value ? patientName.value.trim() : '';
    var dob = patientDob && patientDob.value ? patientDob.value : null;
    var gender = patientGender && patientGender.value ? patientGender.value.trim() : null;
    var medicalHistory = patientMedicalHistory && patientMedicalHistory.value ? patientMedicalHistory.value.trim() : null;
    if (!accId || !name) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Vui lòng điền Họ tên bệnh nhân.', 'warning');
      return;
    }
    var payload = {
      account_id: parseInt(accId, 10),
      patient_name: name
    };
    if (dob) payload.date_of_birth = dob;
    if (gender) payload.gender = gender;
    if (medicalHistory) payload.medical_history = medicalHistory;
    window.AuraAPI.createPatient(payload)
      .then(function () {
        var modal = bootstrap.Modal.getOrCreateInstance(modalPatientProfile);
        if (modal) modal.hide();
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã tạo hồ sơ bệnh nhân.', 'success');
        loadPatients();
        loadAccounts();
      })
      .catch(function (e) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
      });
  }

  function openModalDoctorProfile(accountIdVal) {
    if (doctorProfileAccountId) doctorProfileAccountId.value = accountIdVal;
    if (doctorName) doctorName.value = '';
    if (doctorSpecialization) doctorSpecialization.value = '';
    if (doctorLicense) doctorLicense.value = '';
    var modal = bootstrap.Modal.getOrCreateInstance(modalDoctorProfile);
    if (modal) modal.show();
  }

  function saveDoctorProfile() {
    var accId = doctorProfileAccountId && doctorProfileAccountId.value ? doctorProfileAccountId.value.trim() : '';
    var name = doctorName && doctorName.value ? doctorName.value.trim() : '';
    var spec = doctorSpecialization && doctorSpecialization.value ? doctorSpecialization.value.trim() : '';
    var license = doctorLicense && doctorLicense.value ? doctorLicense.value.trim() : '';
    if (!accId || !name || !spec || !license) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Vui lòng điền đủ: Họ tên, Chuyên khoa, Số chứng chỉ.', 'warning');
      return;
    }
    window.AuraAPI.createDoctor({
      account_id: parseInt(accId, 10),
      doctor_name: name,
      specialization: spec,
      license_number: license
    })
      .then(function () {
        var modal = bootstrap.Modal.getOrCreateInstance(modalDoctorProfile);
        if (modal) modal.hide();
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã tạo hồ sơ bác sĩ.', 'success');
        loadDoctors();
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
  if (accountRoleId) accountRoleId.addEventListener('change', updateClinicVisibility);
  if (filterSearch) {
    filterSearch.addEventListener('input', function () {
      var t = this;
      clearTimeout(t._searchTimer);
      t._searchTimer = setTimeout(loadAccounts, 300);
    });
  }
  if (btnSaveDoctorProfile) btnSaveDoctorProfile.addEventListener('click', saveDoctorProfile);
  if (btnSavePatientProfile) btnSavePatientProfile.addEventListener('click', savePatientProfile);

  loadRoles()
    .then(function () { return loadClinicsForSelect(); })
    .then(function () { return loadDoctors(); })
    .then(function () { return loadPatients(); })
    .then(function () { loadAccounts(); })
    .catch(function (err) {
      showError(err.message || 'Tải dữ liệu thất bại.');
    });
})();
