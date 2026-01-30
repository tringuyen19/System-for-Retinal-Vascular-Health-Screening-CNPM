/**
 * AURA - Alert / Toast component (Bootstrap 5 Toast)
 * Dùng: AuraAlert.toast(message, type)  type: 'success'|'danger'|'warning'|'info'
 */
(function () {
  'use strict';

  var TOAST_CONTAINER_ID = 'auraToastContainer';

  function getOrCreateContainer() {
    var el = document.getElementById(TOAST_CONTAINER_ID);
    if (el) return el;
    el = document.createElement('div');
    el.id = TOAST_CONTAINER_ID;
    el.className = 'toast-container position-fixed top-0 end-0 p-3';
    el.style.zIndex = '9999';
    document.body.appendChild(el);
    return el;
  }

  function toast(message, type) {
    type = type || 'info';
    var container = getOrCreateContainer();
    var id = 'toast-' + Date.now();
    var bgClass = type === 'success' ? 'bg-success' : type === 'danger' ? 'bg-danger' : type === 'warning' ? 'bg-warning' : 'bg-info';
    var div = document.createElement('div');
    div.className = 'toast align-items-center text-white ' + bgClass + ' border-0';
    div.setAttribute('role', 'alert');
    div.id = id;
    div.innerHTML = '<div class="d-flex"><div class="toast-body">' + (message || '') + '</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Đóng"></button></div>';
    container.appendChild(div);
    var bsToast = window.bootstrap && window.bootstrap.Toast ? new window.bootstrap.Toast(div, { delay: 4000 }) : null;
    if (bsToast) {
      div.addEventListener('hidden.bs.toast', function () { div.remove(); }, { once: true });
      bsToast.show();
    }
  }

  window.AuraAlert = { toast: toast };
})();
