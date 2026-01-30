/**
 * AURA - Modal component (Bootstrap 5)
 * Dùng: AuraModal.show({ title, body, footerHtml, onClose })
 */
(function () {
  'use strict';

  var modalId = 'auraModal';
  var modalEl = null;

  function getOrCreate() {
    if (modalEl && document.getElementById(modalId)) return modalEl;
    var div = document.createElement('div');
    div.className = 'modal fade';
    div.id = modalId;
    div.setAttribute('tabindex', '-1');
    div.innerHTML =
      '<div class="modal-dialog modal-dialog-centered">' +
        '<div class="modal-content">' +
          '<div class="modal-header">' +
            '<h5 class="modal-title" id="auraModalTitle"></h5>' +
            '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Đóng"></button>' +
          '</div>' +
          '<div class="modal-body" id="auraModalBody"></div>' +
          '<div class="modal-footer" id="auraModalFooter"></div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(div);
    modalEl = div;
    return div;
  }

  function show(options) {
    var opts = options || {};
    var el = getOrCreate();
    var titleEl = document.getElementById('auraModalTitle');
    var bodyEl = document.getElementById('auraModalBody');
    var footerEl = document.getElementById('auraModalFooter');
    if (titleEl) titleEl.textContent = opts.title || '';
    if (bodyEl) bodyEl.innerHTML = opts.body != null ? opts.body : '';
    if (footerEl) footerEl.innerHTML = opts.footerHtml != null ? opts.footerHtml : '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>';
    var modal = window.bootstrap && window.bootstrap.Modal ? new window.bootstrap.Modal(el) : null;
    if (modal) {
      el.addEventListener('hidden.bs.modal', function onHidden() {
        el.removeEventListener('hidden.bs.modal', onHidden);
        if (typeof opts.onClose === 'function') opts.onClose();
      }, { once: true });
      modal.show();
    }
  }

  function hide() {
    var el = document.getElementById(modalId);
    if (!el) return;
    var modal = window.bootstrap && window.bootstrap.Modal ? window.bootstrap.Modal.getInstance(el) : null;
    if (modal) modal.hide();
  }

  window.AuraModal = { show: show, hide: hide };
})();
