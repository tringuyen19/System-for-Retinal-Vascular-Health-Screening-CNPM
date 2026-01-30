/**
 * AURA - Clinic Profile
 * Load clinic by clinic_id (user.clinic_id), form name/address/phone/logo_url, update via API
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var form = document.getElementById('profileForm');
  var clinicName = document.getElementById('clinicName');
  var clinicAddress = document.getElementById('clinicAddress');
  var clinicPhone = document.getElementById('clinicPhone');
  var clinicLogoUrl = document.getElementById('clinicLogoUrl');
  var verificationStatus = document.getElementById('verificationStatus');
  var btnSave = document.getElementById('btnSave');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!clinicId) {
      showError('Bạn chưa được gán phòng khám.');
      return;
    }
    showError('');
    btnSave.disabled = true;
    window.AuraAPI.getClinic(clinicId)
      .then(function (c) {
        if (clinicName) clinicName.value = c.name || '';
        if (clinicAddress) clinicAddress.value = c.address || '';
        if (clinicPhone) clinicPhone.value = c.phone || '';
        if (clinicLogoUrl) clinicLogoUrl.value = c.logo_url || '';
        if (verificationStatus) {
          verificationStatus.textContent = c.verification_status || '-';
          verificationStatus.className = 'badge bg-' + (c.verification_status === 'verified' ? 'success' : c.verification_status === 'rejected' ? 'danger' : 'warning');
        }
      })
      .catch(function (err) {
        showError(err.message || 'Không tải được thông tin phòng khám.');
      })
      .finally(function () {
        btnSave.disabled = false;
      });
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!clinicId) return;
      var name = clinicName ? clinicName.value.trim() : '';
      var address = clinicAddress ? clinicAddress.value.trim() : '';
      var phone = clinicPhone ? clinicPhone.value.trim() : '';
      var logo_url = clinicLogoUrl ? clinicLogoUrl.value.trim() : '';
      if (!name || !address || !phone) {
        showError('Vui lòng nhập tên, địa chỉ và số điện thoại.');
        return;
      }
      showError('');
      btnSave.disabled = true;
      window.AuraAPI.updateClinic(clinicId, { name: name, address: address, phone: phone, logo_url: logo_url || undefined })
        .then(function () {
          load();
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã cập nhật hồ sơ.', 'success');
          else alert('Đã cập nhật hồ sơ.');
        })
        .catch(function (err) {
          showError(err.message || 'Lưu thất bại.');
        })
        .finally(function () {
          btnSave.disabled = false;
        });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
