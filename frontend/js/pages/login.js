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
  const btnLoginGoogle = document.getElementById('btnLoginGoogle');

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

  async function handleEmailPasswordLogin(e) {
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
        // Sử dụng redirectByRoleWithProfileCheck để kiểm tra profile
        if (window.AuraAuth.redirectByRoleWithProfileCheck) {
          window.AuraAuth.redirectByRoleWithProfileCheck();
        } else {
          window.AuraAuth.redirectByRole();
        }
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
  }

  // Google OAuth: nếu trên URL có ?google_token=... thì tự động hoàn tất đăng nhập
  async function handleGoogleTokenIfPresent() {
    try {
      var params = new URLSearchParams(window.location.search || '');
      var token = params.get('google_token');
      if (!token) return;

      // Gọi /api/auth/me để lấy thông tin user từ token
      const API_BASE = window.AURA_CONFIG ? window.AURA_CONFIG.API_BASE_URL : 'http://localhost:9999';
      const res = await fetch(API_BASE + '/api/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer ' + token
        }
      });
      if (!res.ok) {
        // Nếu token không hợp lệ, chỉ hiện lỗi nhẹ, cho phép user đăng nhập thủ công
        const data = await res.json().catch(function () { return {}; });
        console.warn('Google token invalid:', data);
        return;
      }
      const data = await res.json();
      var user = data && data.data ? data.data : null;
      if (!user || !window.AuraAuth) return;

      // Dùng cùng format với setAuthFromResponse
      var payload = {
        data: {
          access_token: token,
          account_id: user.account_id,
          email: user.email,
          role_id: user.role_id,
          clinic_id: user.clinic_id
        }
      };
      if (window.AuraAuth.setAuthFromResponse(payload)) {
        if (window.AuraUtils && window.AuraUtils.showToast) {
          window.AuraUtils.showToast('Đăng nhập bằng Google thành công.', 'success');
        }
        // Xóa google_token khỏi URL cho đẹp
        if (window.history && window.history.replaceState) {
          var url = new URL(window.location.href);
          url.searchParams.delete('google_token');
          window.history.replaceState({}, '', url.toString());
        }
        // Sử dụng redirectByRoleWithProfileCheck để kiểm tra patient profile
        if (window.AuraAuth.redirectByRoleWithProfileCheck) {
          window.AuraAuth.redirectByRoleWithProfileCheck();
        } else {
          window.AuraAuth.redirectByRole();
        }
      }
    } catch (err) {
      console.warn('Error when handling google_token:', err);
    }
  }

  if (form) form.addEventListener('submit', handleEmailPasswordLogin);

  if (btnLoginGoogle) {
    btnLoginGoogle.addEventListener('click', function () {
      var API_BASE = window.AURA_CONFIG ? window.AURA_CONFIG.API_BASE_URL : 'http://localhost:9999';
      window.location.href = API_BASE + '/api/auth/google/login';
    });
  }

  // Thử xử lý token Google (nếu callback redirect về trang này)
  handleGoogleTokenIfPresent();
})();
