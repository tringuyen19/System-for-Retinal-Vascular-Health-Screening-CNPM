/**
 * AURA - Forgot password page
 * Gửi email -> API /api/auth/forgot-password (backend có thể chưa có)
 */

(function () {
  'use strict';

  const form = document.getElementById('forgotForm');
  const emailInput = document.getElementById('forgotEmail');
  const btnSubmit = document.getElementById('btnForgotSubmit');
  const messageEl = document.getElementById('forgotMessage');

  function showMessage(msg, isSuccess) {
    if (!messageEl) return;
    messageEl.textContent = msg;
    messageEl.classList.remove('d-none', 'alert-danger', 'alert-success');
    messageEl.classList.add(isSuccess ? 'alert-success' : 'alert-danger');
  }

  function setLoading(loading) {
    btnSubmit.disabled = loading;
    btnSubmit.textContent = loading ? 'Đang gửi...' : 'Gửi hướng dẫn';
  }

  function validate() {
    const email = (emailInput && emailInput.value) ? emailInput.value.trim() : '';
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !re.test(email)) {
      emailInput.classList.add('is-invalid');
      document.getElementById('forgotEmailError').textContent = 'Vui lòng nhập email hợp lệ.';
      return false;
    }
    emailInput.classList.remove('is-invalid');
    return true;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await window.AuraAPI.forgotPassword(emailInput.value.trim());
      showMessage('Nếu email tồn tại, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu qua email.', true);
      form.reset();
    } catch (err) {
      var msg = err && err.message ? err.message : 'Gửi yêu cầu thất bại. Vui lòng thử lại.';
      if (msg.indexOf('Không thể kết nối') !== -1 || msg.indexOf('Failed to fetch') !== -1 || msg.indexOf('NetworkError') !== -1) {
        msg = 'Không thể kết nối máy chủ. Kiểm tra backend đã chạy tại http://localhost:9999 chưa.';
      } else if (msg.indexOf('404') !== -1 || msg.indexOf('Not Found') !== -1 || msg.indexOf('failed') !== -1) {
        msg = 'Chức năng quên mật khẩu đang được cập nhật. Vui lòng liên hệ quản trị viên.';
      }
      showMessage(msg, false);
    } finally {
      setLoading(false);
    }
  });
})();
