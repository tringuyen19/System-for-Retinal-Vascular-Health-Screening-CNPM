/**
 * AURA - Loading spinner component
 * Dùng: AuraSpinner.show() / AuraSpinner.hide()
 * Hoặc: AuraSpinner.showIn(containerId) để spinner trong container.
 */
(function () {
  'use strict';

  var OVERLAY_ID = 'auraSpinnerOverlay';
  var overlay = null;

  function show() {
    if (overlay && document.getElementById(OVERLAY_ID)) {
      overlay.style.display = 'flex';
      return;
    }
    overlay = document.createElement('div');
    overlay.id = OVERLAY_ID;
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    overlay.style.cssText = 'background: rgba(255,255,255,0.7); z-index: 9998;';
    overlay.innerHTML = '<div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;"><span class="visually-hidden">Đang tải...</span></div>';
    document.body.appendChild(overlay);
  }

  function hide() {
    var el = document.getElementById(OVERLAY_ID);
    if (el) el.style.display = 'none';
  }

  function showIn(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var wrap = container.querySelector('.aura-spinner-wrap');
    if (wrap) { wrap.style.display = ''; return; }
    wrap = document.createElement('div');
    wrap.className = 'aura-spinner-wrap d-flex align-items-center justify-content-center py-5';
    wrap.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Đang tải...</span></div>';
    container.innerHTML = '';
    container.appendChild(wrap);
  }

  function hideIn(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var wrap = container.querySelector('.aura-spinner-wrap');
    if (wrap) wrap.style.display = 'none';
  }

  window.AuraSpinner = { show: show, hide: hide, showIn: showIn, hideIn: hideIn };
})();
