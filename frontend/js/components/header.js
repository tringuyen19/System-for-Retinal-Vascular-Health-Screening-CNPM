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

  function setupProfileLink() {
    var el = document.getElementById('headerProfileLink');
    if (!el) return;
    var role = window.AuraAuth && window.AuraAuth.getRole ? window.AuraAuth.getRole() : '';
    var base = ROLE_BASE[role];
    el.href = base ? base + '/profile.html' : 'login.html';
    el.style.display = base ? '' : 'none';
  }

  function setupSettingsLink() {
    var el = document.getElementById('headerSettingsLink');
    if (!el) return;
    var role = window.AuraAuth && window.AuraAuth.getRole ? window.AuraAuth.getRole() : '';
    var base = ROLE_BASE[role];
    el.href = base ? base + '/settings.html' : '#';
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
    var loginItem = document.querySelector('.aura-header .nav-link[href="login.html"]');
    var registerItem = document.querySelector('.aura-header .nav-link[href="register.html"]');
    var userDropdown = document.getElementById('userDropdown');
    if (loginItem) loginItem.closest('.nav-item').style.display = loggedIn ? 'none' : '';
    if (registerItem) registerItem.closest('.nav-item').style.display = loggedIn ? 'none' : '';
    if (userDropdown) userDropdown.closest('.nav-item').style.display = loggedIn ? '' : 'none';
  }

  function init() {
    updateUserDisplay();
    setupProfileLink();
    setupSettingsLink();
    setupLogout();
    toggleNavByAuth();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.AuraHeader = { init: init, updateUserDisplay: updateUserDisplay };
})();
