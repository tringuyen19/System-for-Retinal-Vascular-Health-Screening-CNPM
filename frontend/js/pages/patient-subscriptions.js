/**
 * AURA - Patient Subscriptions (FR-11, FR-12)
 * Hiển thị số lượt còn lại, danh sách gói (id 1-5), mua gói demo PTT chuyển khoản, lịch sử thanh toán.
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Patient')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;

  var subscriptionsError = document.getElementById('subscriptionsError');
  var remainingCredits = document.getElementById('remainingCredits');
  var creditsNote = document.getElementById('creditsNote');
  var packagesList = document.getElementById('packagesList');
  var paymentHistoryList = document.getElementById('paymentHistoryList');
  var confirmPurchaseModal = document.getElementById('confirmPurchaseModal');
  var confirmPurchaseText = document.getElementById('confirmPurchaseText');
  var confirmPurchaseBtn = document.getElementById('confirmPurchaseBtn');

  var selectedPackageId = null;
  var selectedPackageName = null;

  function showError(msg) {
    if (!subscriptionsError) return;
    subscriptionsError.textContent = msg || '';
    subscriptionsError.classList.toggle('d-none', !msg);
  }

  function formatMoney(n) {
    if (n == null || isNaN(n)) return '-';
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(n);
  }

  function formatDate(s) {
    if (!s) return '-';
    try {
      var d = new Date(s);
      return isNaN(d.getTime()) ? s : d.toLocaleString('vi-VN');
    } catch (e) { return s; }
  }

  function loadCredits() {
    if (!accountId) return Promise.resolve();
    return window.AuraAPI.getAccountCredits(accountId)
      .then(function (data) {
        var credits = (data && data.remaining_credits) != null ? data.remaining_credits : 0;
        var hasActive = data && data.has_active_subscription;
        if (remainingCredits) remainingCredits.textContent = credits;
        if (creditsNote) {
          creditsNote.textContent = hasActive ? 'Bạn đang có gói đang hoạt động.' : 'Chưa có gói hoặc gói đã hết hạn. Mua gói để upload ảnh phân tích.';
        }
        return data;
      })
      .catch(function (err) {
        if (remainingCredits) remainingCredits.textContent = '-';
        if (creditsNote) creditsNote.textContent = '';
        showError(err.message || 'Không tải được số lượt còn lại.');
        throw err;
      });
  }

  function loadPackages() {
    return window.AuraAPI.getServicePackagesForPatient()
      .then(function (data) {
        var list = (data && data.packages) || [];
        if (!packagesList) return;
        if (!list.length) {
          packagesList.innerHTML = '<p class="text-muted">Không có gói nào (id 1-5).</p>';
          return;
        }
        packagesList.innerHTML = list.map(function (p) {
          var id = p.package_id || p.id;
          var name = p.name || 'Gói #' + id;
          var price = p.price != null ? p.price : 0;
          var limit = p.image_limit != null ? p.image_limit : 0;
          var days = p.duration_days != null ? p.duration_days : 0;
          return '<div class="col-md-6 col-lg-4">' +
            '<div class="card border-0 shadow-sm h-100">' +
            '<div class="card-body">' +
            '<h5 class="card-title">' + (name) + '</h5>' +
            '<p class="text-muted small mb-1">Số ảnh: ' + limit + ' | Thời hạn: ' + days + ' ngày</p>' +
            '<p class="fs-5 text-primary mb-3">' + formatMoney(price) + '</p>' +
            '<button type="button" class="btn btn-primary btn-sm btn-purchase" data-package-id="' + id + '" data-package-name="' + (name.replace(/"/g, '&quot;')) + '">Mua gói</button>' +
            '</div></div></div>';
        }).join('');
        packagesList.querySelectorAll('.btn-purchase').forEach(function (btn) {
          btn.addEventListener('click', function () {
            selectedPackageId = parseInt(btn.getAttribute('data-package-id'), 10);
            selectedPackageName = btn.getAttribute('data-package-name') || ('Gói #' + selectedPackageId);
            if (confirmPurchaseText) confirmPurchaseText.textContent = 'Bạn có chắc muốn mua gói "' + selectedPackageName + '"?';
            var modal = bootstrap.Modal.getOrCreateInstance(confirmPurchaseModal);
            modal.show();
          });
        });
      })
      .catch(function (err) {
        if (packagesList) packagesList.innerHTML = '<p class="text-danger">' + (err.message || 'Không tải được danh sách gói.') + '</p>';
      });
  }

  function loadPaymentHistory() {
    if (!accountId) {
      if (paymentHistoryList) paymentHistoryList.innerHTML = '<p class="text-muted mb-0">Chưa đăng nhập.</p>';
      return Promise.resolve();
    }
    return window.AuraAPI.getPaymentHistory(accountId, 20, 0)
      .then(function (data) {
        var payments = (data && data.payments) || [];
        if (!paymentHistoryList) return;
        if (!payments.length) {
          paymentHistoryList.innerHTML = '<p class="text-muted mb-0">Chưa có giao dịch nào.</p>';
          return;
        }
        paymentHistoryList.innerHTML = '<div class="table-responsive"><table class="table table-sm table-hover mb-0">' +
          '<thead><tr><th>Thời gian</th><th>Số tiền</th><th>PTTT</th><th>Trạng thái</th></tr></thead><tbody>' +
          payments.map(function (p) {
            var statusClass = (p.status === 'completed') ? 'success' : (p.status === 'failed') ? 'danger' : (p.status === 'pending') ? 'warning' : 'secondary';
            return '<tr>' +
              '<td>' + formatDate(p.payment_time) + '</td>' +
              '<td>' + formatMoney(p.amount) + '</td>' +
              '<td>' + (p.payment_method || '-') + '</td>' +
              '<td><span class="badge bg-' + statusClass + '">' + (p.status || '-') + '</span></td>' +
              '</tr>';
          }).join('') + '</tbody></table></div>';
      })
      .catch(function (err) {
        if (paymentHistoryList) paymentHistoryList.innerHTML = '<p class="text-danger">' + (err.message || 'Không tải được lịch sử thanh toán.') + '</p>';
      });
  }

  function doPurchase() {
    if (!accountId || !selectedPackageId) return;
    confirmPurchaseBtn.disabled = true;
    window.AuraAPI.purchasePackageDemo(accountId, selectedPackageId)
      .then(function () {
        var modal = bootstrap.Modal.getOrCreateInstance(confirmPurchaseModal);
        modal.hide();
        showError('');
        loadCredits();
        loadPaymentHistory();
      })
      .catch(function (err) {
        showError(err.message || 'Mua gói thất bại.');
      })
      .finally(function () {
        confirmPurchaseBtn.disabled = false;
      });
  }

  function load() {
    showError('');
    if (!accountId) {
      showError('Không tìm thấy thông tin tài khoản.');
      if (packagesList) packagesList.innerHTML = '';
      if (paymentHistoryList) paymentHistoryList.innerHTML = '';
      return;
    }
    loadCredits()
      .then(function () {
        return Promise.all([loadPackages(), loadPaymentHistory()]);
      })
      .catch(function () {});
  }

  if (confirmPurchaseBtn) confirmPurchaseBtn.addEventListener('click', doPurchase);
  if (confirmPurchaseModal) {
    confirmPurchaseModal.addEventListener('hidden.bs.modal', function () {
      selectedPackageId = null;
      selectedPackageName = null;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
