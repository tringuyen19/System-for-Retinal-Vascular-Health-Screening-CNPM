/**
 * AURA - Login page
 * Form submit, validation, gọi API login, lưu token, redirect theo role
 */

(function () {
  'use strict';

  const form = document.getElementById('loginForm');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const btnSubmit = document.getElementById('btnSubmit');
  const loginErrorEl = document.getElementById('loginError');

  function showError(msg) {
    if (!loginErrorEl) return;
    loginErrorEl.textContent = msg || 'Đăng nhập thất bại.';
    loginErrorEl.classList.remove('d-none');
  }

  function hideError() {
    if (loginErrorEl) loginErrorEl.classList.add('d-none');
  }

  function setLoading(loading) {
    btnSubmit.disabled = loading;
    btnSubmit.textContent = loading ? 'Đang xử lý...' : 'Đăng nhập';
  }

  function validate() {
    let valid = true;
    const email = (emailInput && emailInput.value) ? emailInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';

    if (!email) {
      if (emailInput) {
        emailInput.classList.add('is-invalid');
        const err = document.getElementById('emailError');
        if (err) err.textContent = 'Vui lòng nhập email.';
      }
      valid = false;
    } else {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!re.test(email)) {
        emailInput.classList.add('is-invalid');
        const err = document.getElementById('emailError');
        if (err) err.textContent = 'Email không hợp lệ.';
        valid = false;
      } else {
        emailInput.classList.remove('is-invalid');
      }
    }

    if (!password) {
      passwordInput.classList.add('is-invalid');
      const err = document.getElementById('passwordError');
      if (err) err.textContent = 'Vui lòng nhập mật khẩu.';
      valid = false;
    } else {
      passwordInput.classList.remove('is-invalid');
    }

    return valid;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    hideError();
    if (!validate()) return;

    setLoading(true);
    try {
      const res = await window.AuraAPI.login({
        email: emailInput.value.trim(),
        password: passwordInput.value,
      });
      if (window.AuraAuth && window.AuraAuth.setAuthFromResponse(res)) {
        if (window.AuraUtils && window.AuraUtils.showToast) {
          window.AuraUtils.showToast('Đăng nhập thành công.', 'success');
        }
        window.AuraAuth.redirectByRole();
        return;
      }
      showError('Phản hồi từ server không hợp lệ.');
    } catch (err) {
      var msg = err && err.message ? err.message : 'Email hoặc mật khẩu không đúng.';
      if (msg.indexOf('Failed to fetch') !== -1 || msg.indexOf('NetworkError') !== -1 || msg.indexOf('Load failed') !== -1) {
        msg = 'Không thể kết nối máy chủ. Kiểm tra backend đã chạy tại http://localhost:9999 chưa.';
      }
      showError(msg);
    } finally {
      setLoading(false);
    }
  });
})();
