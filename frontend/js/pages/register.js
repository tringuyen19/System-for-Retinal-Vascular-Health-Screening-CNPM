/**
 * AURA - Register page
 * Validation (email, password >= 6, confirm password), submit, redirect
 */

(function () {
  'use strict';

  const form = document.getElementById('registerForm');
  const emailInput = document.getElementById('regEmail');
  const passwordInput = document.getElementById('regPassword');
  const confirmInput = document.getElementById('regConfirmPassword');
  const roleSelect = document.getElementById('regRole');
  const wrapClinic = document.getElementById('wrapRegClinic');
  const clinicSelect = document.getElementById('regClinic');
  const btnSubmit = document.getElementById('btnRegisterSubmit');
  const registerErrorEl = document.getElementById('registerError');

  function toggleClinicByRole() {
    if (!wrapClinic) return;
    const roleId = roleSelect ? String(roleSelect.value || '') : '';
    const show = roleId === '2' || roleId === '3'; // Doctor or Patient
    wrapClinic.classList.toggle('d-none', !show);
    if (!show && clinicSelect) clinicSelect.value = '';
  }

  async function loadClinics() {
    if (!clinicSelect || !window.AuraAPI || !window.AuraAPI.listClinics) return;
    try {
      const res = await window.AuraAPI.listClinics('verified');
      const list = (res && res.clinics) ? res.clinics : [];
      let opts = '<option value="">-- Chọn phòng khám --</option>';
      list.forEach(function (c) {
        const id = c.clinic_id != null ? c.clinic_id : c.id;
        const name = c.name || c.clinic_name || ('Clinic #' + id);
        opts += '<option value="' + id + '">' + name + '</option>';
      });
      clinicSelect.innerHTML = opts;
    } catch (e) {
      // Nếu lỗi tải clinics thì chỉ ẩn phần chọn clinic, không chặn đăng ký
      if (wrapClinic) wrapClinic.classList.add('d-none');
    }
  }

  function showError(msg) {
    if (!registerErrorEl) return;
    registerErrorEl.textContent = msg || 'Đăng ký thất bại.';
    registerErrorEl.classList.remove('d-none');
  }

  function hideError() {
    if (registerErrorEl) registerErrorEl.classList.add('d-none');
  }

  function setLoading(loading) {
    btnSubmit.disabled = loading;
    btnSubmit.textContent = loading ? 'Đang xử lý...' : 'Đăng ký';
  }

  function validate() {
    let valid = true;
    const email = (emailInput && emailInput.value) ? emailInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';
    const confirm = confirmInput ? confirmInput.value : '';
    const roleId = roleSelect ? roleSelect.value : '';

    if (!email) {
      emailInput.classList.add('is-invalid');
      document.getElementById('regEmailError').textContent = 'Vui lòng nhập email.';
      valid = false;
    } else {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!re.test(email)) {
        emailInput.classList.add('is-invalid');
        document.getElementById('regEmailError').textContent = 'Email không hợp lệ.';
        valid = false;
      } else {
        emailInput.classList.remove('is-invalid');
      }
    }

    if (password.length < 6) {
      passwordInput.classList.add('is-invalid');
      document.getElementById('regPasswordError').textContent = 'Mật khẩu tối thiểu 6 ký tự.';
      valid = false;
    } else {
      passwordInput.classList.remove('is-invalid');
    }

    if (password !== confirm) {
      confirmInput.classList.add('is-invalid');
      document.getElementById('regConfirmPasswordError').textContent = 'Mật khẩu không khớp.';
      valid = false;
    } else {
      confirmInput.classList.remove('is-invalid');
    }

    if (!roleId) {
      roleSelect.classList.add('is-invalid');
      document.getElementById('regRoleError').textContent = 'Vui lòng chọn vai trò.';
      valid = false;
    } else {
      roleSelect.classList.remove('is-invalid');
    }

    return valid;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    hideError();
    if (!validate()) return;

    setLoading(true);
    try {
      const payload = {
        email: emailInput.value.trim(),
        password: passwordInput.value,
        role_id: parseInt(roleSelect.value, 10),
      };
      if (clinicSelect && clinicSelect.value) payload.clinic_id = parseInt(clinicSelect.value, 10);
      const res = await window.AuraAPI.register(payload);
      if (window.AuraAuth && window.AuraAuth.setAuthFromResponse(res)) {
        if (window.AuraUtils && window.AuraUtils.showToast) {
          window.AuraUtils.showToast('Đăng ký thành công.', 'success');
        }
        window.AuraAuth.redirectByRole();
        return;
      }
      showError('Phản hồi từ server không hợp lệ.');
    } catch (err) {
      var msg = err && err.message ? err.message : 'Đăng ký thất bại. Vui lòng thử lại.';
      if (msg.indexOf('Failed to fetch') !== -1 || msg.indexOf('NetworkError') !== -1 || msg.indexOf('Load failed') !== -1) {
        msg = 'Không thể kết nối máy chủ. Kiểm tra backend đã chạy tại http://localhost:9999 chưa.';
      }
      showError(msg);
    } finally {
      setLoading(false);
    }
  });

  if (roleSelect) roleSelect.addEventListener('change', toggleClinicByRole);
  toggleClinicByRole();
  loadClinics();
})();
