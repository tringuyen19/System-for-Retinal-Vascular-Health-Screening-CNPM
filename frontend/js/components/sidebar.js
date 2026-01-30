/**
 * AURA - Sidebar component
 * Menu theo role, active state theo URL, responsive (Bootstrap: ẩn trên mobile bằng d-none d-md-flex).
 */
(function () {
  'use strict';

  var ROLE_BASE = { Patient: 'patient', Doctor: 'doctor', ClinicManager: 'clinic', Admin: 'admin' };

  function getCurrentPath() {
    var path = window.location.pathname || '';
    path = path.replace(/^\//, '').replace(/\/$/, '');
    return path || 'index.html';
  }

  function setActiveState() {
    var current = getCurrentPath();
    var sidebar = document.querySelector('.aura-sidebar');
    if (!sidebar) return;
    sidebar.querySelectorAll('.nav-link').forEach(function (a) {
      var href = (a.getAttribute('href') || '').replace(/^\//, '');
      var isActive = href === current || current.indexOf(href.replace('.html', '')) === 0;
      a.classList.toggle('active', isActive);
    });
  }

  function toggleByRole() {
    var role = window.AuraAuth && window.AuraAuth.getRole ? window.AuraAuth.getRole() : '';
    var base = ROLE_BASE[role];
    var sidebar = document.querySelector('.aura-sidebar');
    if (!sidebar) return;
    sidebar.querySelectorAll('[data-role]').forEach(function (el) {
      var allowed = el.getAttribute('data-role');
      var show = !allowed || allowed === role || (role && allowed.split(',').indexOf(role) !== -1);
      el.style.display = show ? '' : 'none';
    });
  }

  function init() {
    setActiveState();
    toggleByRole();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.AuraSidebar = { init: init, setActiveState: setActiveState };
})();
