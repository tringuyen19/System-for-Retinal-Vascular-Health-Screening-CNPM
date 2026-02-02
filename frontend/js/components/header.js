/**
 * AURA - Header component
 * Hiển thị user info, notifications, logout. Responsive (Bootstrap collapse).
 */
(function () {
  'use strict';

  var ROLE_BASE = { Patient: 'patient', Doctor: 'doctor', ClinicManager: 'clinic', Admin: 'admin' };

  function updateUserDisplay() {
    var el = document.getElementById('headerUserName');
    if (!el) return;
    var user = window.AuraAuth && window.AuraAuth.getUser ? window.AuraAuth.getUser() : null;
    el.textContent = user && user.email ? user.email : 'Tài khoản';
  }

  function rolePagePath(page) {
    var role = window.AuraAuth && window.AuraAuth.getRole ? window.AuraAuth.getRole() : '';
    var base = ROLE_BASE[role];
    if (!base) return page === 'profile' ? 'login.html' : '#';
    var pathname = (window.location && window.location.pathname) || '';
    var inRoleFolder = pathname.indexOf('/' + base + '/') !== -1 || pathname.indexOf('/' + base + '\\') !== -1;
    return inRoleFolder ? page + '.html' : base + '/' + page + '.html';
  }

  function setupProfileLink() {
    var el = document.getElementById('headerProfileLink');
    if (!el) return;
    var role = window.AuraAuth && window.AuraAuth.getRole ? window.AuraAuth.getRole() : '';
    var base = ROLE_BASE[role];
    el.href = rolePagePath('profile');
    el.style.display = base ? '' : 'none';
  }

  function setupSettingsLink() {
    var el = document.getElementById('headerSettingsLink');
    if (!el) return;
    var role = window.AuraAuth && window.AuraAuth.getRole ? window.AuraAuth.getRole() : '';
    var base = ROLE_BASE[role];
    el.href = rolePagePath('settings');
    el.style.display = base ? '' : 'none';
  }

  function setupLogout() {
    var el = document.getElementById('headerLogout');
    if (!el) return;
    el.addEventListener('click', function (e) {
      e.preventDefault();
      if (window.AuraAuth && window.AuraAuth.clearAuth) window.AuraAuth.clearAuth();
      var loginUrl = (window.AuraAuth && window.AuraAuth.getLoginPageUrl) ? window.AuraAuth.getLoginPageUrl() : (window.location.origin + '/login.html');
      window.location.href = loginUrl;
    });
  }

  function toggleNavByAuth() {
    var loggedIn = window.AuraAuth && window.AuraAuth.isLoggedIn && window.AuraAuth.isLoggedIn();
    var header = document.querySelector('.aura-header');
    if (!header) return;
    // Ẩn Trang chủ, Đăng nhập, Đăng ký khi đã đăng nhập (href có thể là ../login.html hoặc login.html)
    header.querySelectorAll('.navbar-nav.me-auto .nav-item').forEach(function (navItem) {
      var link = navItem.querySelector('.nav-link[href*="index.html"], .nav-link[href*="login.html"], .nav-link[href*="register.html"]');
      if (link) navItem.style.display = loggedIn ? 'none' : '';
    });
    var userDropdown = document.getElementById('userDropdown');
    if (userDropdown) userDropdown.closest('.nav-item').style.display = loggedIn ? '' : 'none';
  }

  /** Khi đã đăng nhập: click AURA -> dashboard của role (giữ nguyên patient/dashboard.html, không về index) */
  function setupBrandLink() {
    var header = document.querySelector('.aura-header');
    if (!header) return;
    var brand = header.querySelector('.navbar-brand');
    if (!brand) return;
    var loggedIn = window.AuraAuth && window.AuraAuth.isLoggedIn && window.AuraAuth.isLoggedIn();
    var path = (window.location && window.location.pathname) || '';
    var inRoleFolder = /[\/\\](patient|doctor|clinic|admin)[\/\\]/.test(path);
    if (loggedIn && inRoleFolder) {
      brand.setAttribute('href', 'dashboard.html');
    }
  }

  function init() {
    updateUserDisplay();
    setupProfileLink();
    setupSettingsLink();
    setupLogout();
    toggleNavByAuth();
    setupBrandLink();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.AuraHeader = { init: init, updateUserDisplay: updateUserDisplay };
})();
