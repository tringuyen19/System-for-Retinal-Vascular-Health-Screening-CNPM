/**
 * AURA - Doctor Profile
 * Load doctor by account, edit form, create or update via API
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var doctorId = null;

  var form = document.getElementById('profileForm');
  var doctorName = document.getElementById('doctorName');
  var specialization = document.getElementById('specialization');
  var licenseNumber = document.getElementById('licenseNumber');
  var btnSave = document.getElementById('btnSave');
  var profileError = document.getElementById('profileError');

  function showError(msg) {
    if (!profileError) return;
    profileError.textContent = msg || '';
    profileError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!accountId) {
      showError('Không tìm thấy tài khoản.');
      return;
    }
    showError('');
    if (btnSave) btnSave.disabled = true;
    window.AuraAPI.getDoctorByAccount(accountId)
      .then(function (d) {
        if (!d || !d.doctor_id) {
          showError('Chưa có hồ sơ bác sĩ. Điền form và bấm "Lưu" để tạo hồ sơ.');
          if (btnSave) btnSave.textContent = 'Tạo hồ sơ';
          doctorId = null;
          return;
        }
        doctorId = d.doctor_id;
        if (doctorName) doctorName.value = d.doctor_name || '';
        if (specialization) specialization.value = d.specialization || '';
        if (licenseNumber) licenseNumber.value = d.license_number || '';
        if (btnSave) btnSave.textContent = 'Lưu thay đổi';
      })
      .catch(function (err) {
        showError(err.message || 'Không tải được hồ sơ. Nếu chưa có hồ sơ, điền form và bấm "Tạo hồ sơ".');
        if (btnSave) btnSave.textContent = 'Tạo hồ sơ';
        doctorId = null;
        if (doctorName) doctorName.value = '';
        if (specialization) specialization.value = '';
        if (licenseNumber) licenseNumber.value = '';
      })
      .finally(function () {
        if (btnSave) btnSave.disabled = false;
      });
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = doctorName ? doctorName.value.trim() : '';
      var spec = specialization ? specialization.value.trim() : '';
      var license = licenseNumber ? licenseNumber.value.trim() : '';
      if (!name) {
        showError('Vui lòng nhập họ tên bác sĩ.');
        return;
      }
      if (!spec) {
        showError('Vui lòng nhập chuyên khoa.');
        return;
      }
      if (!license) {
        showError('Vui lòng nhập số chứng chỉ hành nghề.');
        return;
      }
      showError('');
      btnSave.disabled = true;
      var payload = { doctor_name: name, specialization: spec, license_number: license };
      var promise;
      if (doctorId) {
        promise = window.AuraAPI.updateDoctor(doctorId, payload);
      } else {
        payload.account_id = accountId;
        promise = window.AuraAPI.createDoctor(payload);
      }
      promise
        .then(function (data) {
          if (data && data.doctor_id) doctorId = data.doctor_id;
          load();
          if (window.AuraAlert && window.AuraAlert.toast) {
            window.AuraAlert.toast(doctorId ? 'Đã cập nhật hồ sơ.' : 'Đã tạo hồ sơ bác sĩ.', 'success');
          } else {
            alert(doctorId ? 'Đã cập nhật hồ sơ.' : 'Đã tạo hồ sơ bác sĩ.');
          }
        })
        .catch(function (err) {
          showError(err.message || 'Lưu thất bại.');
        })
        .finally(function () {
          btnSave.disabled = false;
        });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
