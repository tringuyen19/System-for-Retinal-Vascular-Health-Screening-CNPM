/**
 * AURA - Patient Profile
 * Load patient by account, edit form, update via API
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireLogin || !window.AuraAuth.requireLogin()) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var patientId = null;

  var form = document.getElementById('profileForm');
  var patientName = document.getElementById('patientName');
  var dateOfBirth = document.getElementById('dateOfBirth');
  var gender = document.getElementById('gender');
  var medicalHistory = document.getElementById('medicalHistory');
  var btnSave = document.getElementById('btnSave');
  var profileError = document.getElementById('profileError');

  function showError(msg) {
    if (!profileError) return;
    profileError.textContent = msg || '';
    profileError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!accountId) { showError('Không tìm thấy tài khoản.'); return; }
    showError('');
    btnSave.disabled = true;
    window.AuraAPI.getPatientByAccount(accountId)
      .then(function (p) {
        if (!p || !p.patient_id) {
          showError('Chưa có hồ sơ bệnh nhân. Điền form và bấm "Tạo hồ sơ" bên dưới.');
          if (btnSave) btnSave.textContent = 'Tạo hồ sơ';
          patientId = null;
          return;
        }
        patientId = p.patient_id;
        if (patientName) patientName.value = p.patient_name || '';
        if (dateOfBirth) dateOfBirth.value = p.date_of_birth ? (p.date_of_birth.slice ? p.date_of_birth.slice(0, 10) : p.date_of_birth) : '';
        if (gender) gender.value = p.gender || '';
        if (medicalHistory) medicalHistory.value = p.medical_history || '';
        if (btnSave) btnSave.textContent = 'Lưu thay đổi';
      })
      .catch(function (err) {
        showError(err.message || 'Không tải được hồ sơ.');
        if (btnSave) btnSave.textContent = 'Tạo hồ sơ';
      })
      .finally(function () {
        btnSave.disabled = false;
      });
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = patientName ? patientName.value.trim() : '';
      if (!name) { showError('Vui lòng nhập họ tên.'); return; }
      showError('');
      btnSave.disabled = true;
      var payload = {
        patient_name: name,
        date_of_birth: dateOfBirth && dateOfBirth.value ? dateOfBirth.value : null,
        gender: gender && gender.value ? gender.value : null,
        medical_history: (medicalHistory ? medicalHistory.value.trim() : '') || null
      };
      if (patientId) {
        window.AuraAPI.updatePatient(patientId, payload)
          .then(function () {
            if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã lưu hồ sơ.', 'success');
          })
          .catch(function (err) {
            showError(err.message || 'Lưu thất bại.');
          })
          .finally(function () { btnSave.disabled = false; });
      } else {
        payload.account_id = accountId;
        window.AuraAPI.createPatient(payload)
          .then(function () {
            if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã tạo hồ sơ bệnh nhân.', 'success');
            load();
          })
          .catch(function (err) {
            showError(err.message || 'Tạo hồ sơ thất bại.');
          })
          .finally(function () { btnSave.disabled = false; });
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
