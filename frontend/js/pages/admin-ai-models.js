/**
 * AURA - Admin AI Models
 * Danh sách phiên bản AI, kích hoạt / tắt
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var pageError = document.getElementById('pageError');
  var statTotal = document.getElementById('statTotal');
  var statActive = document.getElementById('statActive');
  var btnReload = document.getElementById('btnReload');
  var modelsTableBody = document.getElementById('modelsTableBody');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    showError('');
    if (modelsTableBody) modelsTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Đang tải...</td></tr>';
    Promise.all([
      window.AuraAPI.getAllAiModelVersions(),
      window.AuraAPI.getAiModelStats()
    ])
      .then(function (results) {
        var listRes = results[0];
        var statsRes = results[1];
        var list = (listRes && listRes.models) ? listRes.models : [];
        if (statTotal) statTotal.textContent = (statsRes && statsRes.total_models != null) ? statsRes.total_models : list.length;
        if (statActive) statActive.textContent = (statsRes && statsRes.active_models != null) ? statsRes.active_models : list.filter(function (m) { return m.active_flag; }).length;
        renderTable(list);
      })
      .catch(function (err) {
        showError(err.message || 'Tải danh sách thất bại.');
        if (statTotal) statTotal.textContent = '-';
        if (statActive) statActive.textContent = '-';
        if (modelsTableBody) modelsTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Lỗi tải dữ liệu</td></tr>';
      });
  }

  function renderTable(list) {
    if (!modelsTableBody) return;
    if (!list || list.length === 0) {
      modelsTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Chưa có phiên bản AI</td></tr>';
      return;
    }
    var html = '';
    list.forEach(function (m) {
      var id = m.ai_model_version_id != null ? m.ai_model_version_id : m.id;
      var active = !!m.active_flag;
      var threshold = (m.threshold_config || '-');
      if (typeof threshold === 'object') threshold = JSON.stringify(threshold);
      html += '<tr>';
      html += '<td>' + id + '</td>';
      html += '<td>' + (m.model_name || '-') + '</td>';
      html += '<td>' + (m.version || '-') + '</td>';
      html += '<td><span class="badge bg-' + (active ? 'success' : 'secondary') + '">' + (active ? 'Active' : 'Inactive') + '</span></td>';
      html += '<td><small class="text-muted">' + (threshold.length > 40 ? threshold.substring(0, 40) + '...' : threshold) + '</small></td>';
      html += '<td>';
      if (active) {
        html += '<button type="button" class="btn btn-sm btn-warning me-1 btn-deactivate" data-id="' + id + '">Tắt</button>';
      } else {
        html += '<button type="button" class="btn btn-sm btn-success me-1 btn-activate" data-id="' + id + '">Kích hoạt</button>';
      }
      html += '</td></tr>';
    });
    modelsTableBody.innerHTML = html;

    modelsTableBody.querySelectorAll('.btn-activate').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        if (confirm('Kích hoạt phiên bản AI ID ' + id + '?')) {
          window.AuraAPI.activateAiModel(id)
            .then(function () {
              if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã kích hoạt.', 'success');
              load();
            })
            .catch(function (e) {
              if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
            });
        }
      });
    });
    modelsTableBody.querySelectorAll('.btn-deactivate').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        if (confirm('Tắt phiên bản AI ID ' + id + '?')) {
          window.AuraAPI.deactivateAiModel(id)
            .then(function () {
              if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã tắt.', 'success');
              load();
            })
            .catch(function (e) {
              if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
            });
        }
      });
    });
  }

  if (btnReload) btnReload.addEventListener('click', load);
  load();
})();