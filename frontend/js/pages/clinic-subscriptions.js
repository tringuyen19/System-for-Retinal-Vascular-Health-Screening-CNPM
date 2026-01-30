/**
 * AURA - Clinic Subscriptions
 * GET /api/subscriptions/account/:account_id (list), getActiveSubscription optional
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;

  var pageError = document.getElementById('pageError');
  var loading = document.getElementById('loading');
  var content = document.getElementById('content');
  var activeSummary = document.getElementById('activeSummary');
  var tbody = document.getElementById('tbody');
  var listSummary = document.getElementById('listSummary');
  var empty = document.getElementById('empty');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!accountId) { showError('Không tìm thấy tài khoản.'); loading.classList.add('d-none'); empty.classList.remove('d-none'); return; }
    showError('');
    loading.classList.remove('d-none');
    content.classList.add('d-none');
    empty.classList.add('d-none');
    window.AuraAPI.getSubscriptionsByAccount(accountId)
      .then(function (data) {
        loading.classList.add('d-none');
        var list = (data && data.subscriptions) || [];
        var count = (data && data.count != null) ? data.count : list.length;
        if (!list.length) {
          empty.classList.remove('d-none');
          empty.textContent = 'Chưa có gói đăng ký nào.';
          return;
        }
        content.classList.remove('d-none');
        activeSummary.textContent = '';
        window.AuraAPI.getActiveSubscription(accountId)
          .then(function (active) {
            if (activeSummary) activeSummary.innerHTML = active ? '<strong>Gói đang dùng:</strong> #' + (active.subscription_id || active.id) + ' – Credits còn lại: ' + (active.remaining_credits != null ? active.remaining_credits : '-') : '';
          })
          .catch(function () {
            if (activeSummary) activeSummary.innerHTML = '<span class="text-muted">Không có gói đang kích hoạt.</span>';
          });
        listSummary.textContent = 'Tổng: ' + count + ' gói.';
        var html = '';
        list.forEach(function (s) {
          var start = s.start_date ? new Date(s.start_date).toLocaleDateString('vi-VN') : '-';
          var end = s.end_date ? new Date(s.end_date).toLocaleDateString('vi-VN') : '-';
          html += '<tr><td>' + (s.subscription_id || s.id || '-') + '</td><td><span class="badge bg-' + (s.status === 'active' ? 'success' : 'secondary') + '">' + (s.status || '-') + '</span></td><td>' + (s.remaining_credits != null ? s.remaining_credits : '-') + '</td><td>' + start + '</td><td>' + end + '</td></tr>';
        });
        tbody.innerHTML = html;
      })
      .catch(function (err) {
        loading.classList.add('d-none');
        empty.classList.remove('d-none');
        empty.textContent = err.message || 'Không tải được danh sách.';
        showError(err.message || 'Tải thất bại.');
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
