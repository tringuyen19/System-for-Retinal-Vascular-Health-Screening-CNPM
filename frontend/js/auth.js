/**
 * AURA Frontend - Authentication
 * Lưu/xóa token, kiểm tra đăng nhập, redirect theo role
 */

(function () {
  'use strict';

  const KEYS = window.AURA_CONFIG && window.AURA_CONFIG.STORAGE_KEYS
    ? window.AURA_CONFIG.STORAGE_KEYS
    : { TOKEN: 'aura_access_token', USER: 'aura_user', ROLE: 'aura_role' };

  function getToken() {
    return localStorage.getItem(KEYS.TOKEN);
  }

  function getUser() {
    try {
      const raw = localStorage.getItem(KEYS.USER);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function getRole() {
    return localStorage.getItem(KEYS.ROLE) || '';
  }

  function setAuth(token, user, role) {
    if (token) localStorage.setItem(KEYS.TOKEN, token);
    if (user) localStorage.setItem(KEYS.USER, JSON.stringify(user));
    if (role) localStorage.setItem(KEYS.ROLE, role);
  }

  function clearAuth() {
    localStorage.removeItem(KEYS.TOKEN);
    if (KEYS.REFRESH_TOKEN) localStorage.removeItem(KEYS.REFRESH_TOKEN);
    localStorage.removeItem(KEYS.USER);
    localStorage.removeItem(KEYS.ROLE);
  }

  function isLoggedIn() {
    return !!getToken();
  }

  /**
   * Trả về URL tuyệt đối của trang login (luôn đúng dù đang ở /, /patient/, /doctor/, ...).
   * Tránh lỗi 404 khi redirect từ patient/dashboard.html với 'login.html' thành patient/login.html.
   */
  function getLoginPageUrl() {
    const origin = window.location.origin || '';
    const pathname = window.location.pathname || '/';
    const segments = pathname.split('/').filter(Boolean);
    if (segments.length >= 2 && ['patient', 'doctor', 'admin', 'clinic'].indexOf(segments[segments.length - 2]) !== -1) {
      const base = segments.slice(0, -2).join('/');
      return origin + (base ? '/' + base + '/' : '/') + 'login.html';
    }
    if (segments.length >= 1) {
      const base = segments.slice(0, -1).join('/');
      return origin + (base ? '/' + base + '/' : '/') + 'login.html';
    }
    return origin + '/login.html';
  }

  /** Redirect về login nếu chưa đăng nhập (dùng cho trang cần bảo vệ) */
  function requireLogin(loginUrl) {
    if (!isLoggedIn()) {
      window.location.href = loginUrl || getLoginPageUrl();
      return false;
    }
    return true;
  }

  /** Kiểm tra đăng nhập và đúng role; nếu không đúng role thì redirect về dashboard của role hiện tại hoặc index. Trả về true nếu OK. */
  function requireRole(allowedRole) {
    if (!requireLogin()) return false;
    const role = getRole();
    if (role !== allowedRole) {
      const pathname = window.location.pathname || '';
      const parent = pathname.replace(/\/[^/]*$/, '').replace(/\/[^/]+$/, '') || '';
      const map = { Patient: 'patient/dashboard.html', Doctor: 'doctor/dashboard.html', ClinicManager: 'clinic/dashboard.html', Admin: 'admin/dashboard.html' };
      const rel = map[role] || 'index.html';
      const fullPath = (parent ? parent + '/' : '/') + rel;
      window.location.href = (window.location.origin || '') + fullPath;
      return false;
    }
    return true;
  }

  /** Map role_id (backend) -> role name (1=Admin, 2=Doctor, 3=Patient, 4=ClinicManager) */
  function getRoleNameByRoleId(roleId) {
    const map = { 1: 'Admin', 2: 'Doctor', 3: 'Patient', 4: 'ClinicManager' };
    return map[roleId] || '';
  }

  /** Lưu auth từ response login/register và redirect theo role */
  function setAuthFromResponse(responseData) {
    const data = responseData && responseData.data ? responseData.data : responseData;
    if (!data || !data.access_token) return false;
    const user = { account_id: data.account_id, email: data.email, role_id: data.role_id, clinic_id: data.clinic_id };
    const roleName = getRoleNameByRoleId(data.role_id);
    setAuth(data.access_token, user, roleName);
    return true;
  }

  function redirectByRole() {
    const role = getRole();
    const map = { Patient: 'patient/dashboard.html', Doctor: 'doctor/dashboard.html', ClinicManager: 'clinic/dashboard.html', Admin: 'admin/dashboard.html' };
    const path = map[role] || 'index.html';
    const origin = window.location.origin || '';
    const basePath = (window.location.pathname || '').replace(/\/[^/]*$/, '') || '';
    const fullPath = (basePath ? basePath + '/' : '/') + path;
    window.location.href = origin ? origin + fullPath : fullPath;
  }

  /**
   * Redirect theo role, nhưng với Patient và Doctor role thì kiểm tra profile trước.
   * Nếu chưa có profile, redirect đến setup-profile.html thay vì dashboard.
   */
  async function redirectByRoleWithProfileCheck() {
    const role = getRole();
    const user = getUser();
    const accountId = user && user.account_id;
    
    if (!accountId) {
      // Không có account_id, redirect bình thường
      redirectByRole();
      return;
    }

    // Nếu là Patient, kiểm tra xem đã có profile chưa
    if (role === 'Patient') {
      try {
        // Kiểm tra xem đã có patient profile chưa
        if (window.AuraAPI && window.AuraAPI.getPatientByAccount) {
          const patient = await window.AuraAPI.getPatientByAccount(accountId);
          if (patient && patient.patient_id) {
            // Đã có profile, redirect đến dashboard
            redirectByRole();
            return;
          }
        }
      } catch (err) {
        // Nếu lỗi (404 hoặc network), giả sử chưa có profile
        console.log('Chưa có patient profile hoặc lỗi khi kiểm tra:', err);
      }

      // Chưa có profile, redirect đến setup-profile.html
      const origin = window.location.origin || '';
      const basePath = (window.location.pathname || '').replace(/\/[^/]*$/, '') || '';
      const setupPath = (basePath ? basePath + '/' : '/') + 'patient/setup-profile.html';
      window.location.href = origin ? origin + setupPath : setupPath;
      return;
    }

    // Nếu là Doctor, kiểm tra xem đã có profile chưa
    if (role === 'Doctor') {
      try {
        // Kiểm tra xem đã có doctor profile chưa
        if (window.AuraAPI && window.AuraAPI.getDoctorByAccount) {
          const doctor = await window.AuraAPI.getDoctorByAccount(accountId);
          if (doctor && doctor.doctor_id) {
            // Đã có profile, redirect đến dashboard
            redirectByRole();
            return;
          }
        }
      } catch (err) {
        // Nếu lỗi (404 hoặc network), giả sử chưa có profile
        console.log('Chưa có doctor profile hoặc lỗi khi kiểm tra:', err);
      }

      // Chưa có profile, redirect đến setup-profile.html
      const origin = window.location.origin || '';
      const basePath = (window.location.pathname || '').replace(/\/[^/]*$/, '') || '';
      const setupPath = (basePath ? basePath + '/' : '/') + 'doctor/setup-profile.html';
      window.location.href = origin ? origin + setupPath : setupPath;
      return;
    }

    // Các role khác, redirect bình thường
    redirectByRole();
  }

  window.AuraAuth = {
    getToken,
    getUser,
    getRole,
    setAuth,
    clearAuth,
    isLoggedIn,
    requireLogin,
    requireRole,
    getLoginPageUrl,
    getRoleNameByRoleId,
    setAuthFromResponse,
    redirectByRole,
    redirectByRoleWithProfileCheck,
  };
})();
