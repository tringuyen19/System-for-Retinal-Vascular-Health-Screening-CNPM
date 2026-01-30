/**
 * AURA - Reset password page
 * Token lấy từ query ?token=... ; gửi token + new_password qua API
 */

(function () {
  'use strict';

  function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name) || '';
  }

  const form = document.getElementById('resetForm');
  const tokenInput = document.getElementById('resetToken');
  const newPasswordInput = document.getElementById('newPassword');
  const confirmInput = document.getElementById('confirmNewPassword');
  const btnSubmit = document.getElementById('btnResetSubmit');
  const messageEl = document.getElementById('resetMessage');

  const token = getQueryParam('token');
  if (tokenInput) tokenInput.value = token;
  if (!token) {
    if (messageEl) {
      messageEl.textContent = 'Link không hợp lệ hoặc đã hết hạn. Vui lòng yêu cầu đặt lại mật khẩu mới.';
      messageEl.classList.remove('d-none', 'alert-success');
      messageEl.classList.add('alert-danger');
    }
    if (btnSubmit) btnSubmit.disabled = true;
  }

  function showMessage(msg, isSuccess) {
    if (!messageEl) return;
    messageEl.textContent = msg;
    messageEl.classList.remove('d-none', 'alert-danger', 'alert-success');
    messageEl.classList.add(isSuccess ? 'alert-success' : 'alert-danger');
  }

  function setLoading(loading) {
    btnSubmit.disabled = loading;
    btnSubmit.textContent = loading ? 'Đang xử lý...' : 'Đặt lại mật khẩu';
  }

  function validate() {
    const newPwd = newPasswordInput ? newPasswordInput.value : '';
    const confirm = confirmInput ? confirmInput.value : '';
    let valid = true;

    if (newPwd.length < 6) {
      newPasswordInput.classList.add('is-invalid');
      document.getElementById('newPasswordError').textContent = 'Mật khẩu tối thiểu 6 ký tự.';
      valid = false;
    } else {
      newPasswordInput.classList.remove('is-invalid');
    }

    if (newPwd !== confirm) {
      confirmInput.classList.add('is-invalid');
      document.getElementById('confirmNewPasswordError').textContent = 'Mật khẩu không khớp.';
      valid = false;
    } else {
      confirmInput.classList.remove('is-invalid');
    }

    return valid;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (!token) return;
    if (!validate()) return;

    setLoading(true);
    try {
      await window.AuraAPI.resetPassword(token, newPasswordInput.value);
      showMessage('Đặt lại mật khẩu thành công. Bạn có thể đăng nhập bằng mật khẩu mới.', true);
      form.reset();
      setTimeout(function () {
        var loginUrl = (window.AuraAuth && window.AuraAuth.getLoginPageUrl) ? window.AuraAuth.getLoginPageUrl() : (window.location.origin + '/login.html');
        window.location.href = loginUrl;
      }, 2000);
    } catch (err) {
      if (err.message && (err.message.includes('404') || err.message.includes('Not Found') || err.message.includes('failed'))) {
        showMessage('Chức năng đặt lại mật khẩu đang được cập nhật. Vui lòng liên hệ quản trị viên.', false);
      } else {
        showMessage(err.message || 'Đặt lại mật khẩu thất bại. Vui lòng thử lại.', false);
      }
    } finally {
      setLoading(false);
    }
  });
})();
