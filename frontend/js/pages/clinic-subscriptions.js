/**
 * AURA - FR-28: Mua hoặc gia hạn gói dịch vụ cấp phòng khám
 * Clinic packages 6-8: mua mới + gia hạn
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var CLINIC_PACKAGE_IDS = [6, 7, 8];

  var pageError = document.getElementById('pageError');
  var loading = document.getElementById('loading');
  var content = document.getElementById('content');
  var activeSummary = document.getElementById('activeSummary');
  var tbody = document.getElementById('tbody');
  var listSummary = document.getElementById('listSummary');
  var empty = document.getElementById('empty');
  var clinicPackagesLoading = document.getElementById('clinicPackagesLoading');
  var clinicPackagesRow = document.getElementById('clinicPackagesRow');
  var purchaseConfirmModal = document.getElementById('purchaseConfirmModal');
  var confirmPurchaseText = document.getElementById('confirmPurchaseText');
  var btnConfirmPurchase = document.getElementById('btnConfirmPurchase');
  var renewModal = document.getElementById('renewModal');
  var renewSubscriptionId = document.getElementById('renewSubscriptionId');
  var renewPackageId = document.getElementById('renewPackageId');
  var renewConfirmText = document.getElementById('renewConfirmText');
  var btnConfirmRenew = document.getElementById('btnConfirmRenew');

  var clinicPackagesMap = {}; // package_id -> { name, image_limit, duration_days, price }
  var pendingPurchasePackageId = null;

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function toast(msg, type) {
    if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(msg, type || 'success');
  }

  function loadClinicPackages() {
    if (!clinicPackagesLoading || !clinicPackagesRow) return;
    clinicPackagesLoading.classList.remove('d-none');
    clinicPackagesRow.classList.add('d-none');
    clinicPackagesRow.innerHTML = '';
    window.AuraAPI.getServicePackagesForClinic()
      .then(function (data) {
        clinicPackagesLoading.classList.add('d-none');
        var packages = (data && data.packages) || [];
        if (!packages.length) {
          clinicPackagesRow.classList.remove('d-none');
          clinicPackagesRow.innerHTML = '<div class="col-12 text-muted">Không có gói cấp phòng khám (6–8).</div>';
          return;
        }
        packages.forEach(function (p) {
          clinicPackagesMap[p.package_id] = p;
          var priceStr = (p.price != null) ? Number(p.price).toLocaleString('vi-VN') + ' đ' : '-';
          var card = '<div class="col-md-4">' +
            '<div class="card h-100 border">' +
            '<div class="card-body">' +
            '<h6 class="card-title">' + (p.name || 'Gói #' + p.package_id) + '</h6>' +
            '<p class="small mb-1">Lượt tải ảnh: <strong>' + (p.image_limit != null ? p.image_limit.toLocaleString('vi-VN') : '-') + '</strong></p>' +
            '<p class="small mb-1">Thời hạn: <strong>' + (p.duration_days != null ? p.duration_days + ' ngày' : '-') + '</strong></p>' +
            '<p class="small mb-3">Giá: ' + priceStr + '</p>' +
            '<button type="button" class="btn btn-primary btn-sm w-100 btn-purchase-clinic" data-package-id="' + p.package_id + '"><i class="bi bi-cart-plus me-1"></i>Mua gói</button>' +
            '</div></div></div>';
          clinicPackagesRow.insertAdjacentHTML('beforeend', card);
        });
        clinicPackagesRow.classList.remove('d-none');
        clinicPackagesRow.querySelectorAll('.btn-purchase-clinic').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var pkgId = parseInt(btn.getAttribute('data-package-id'), 10);
            openPurchaseConfirmModal(pkgId);
          });
        });
        load(); // refresh table to show package names
      })
      .catch(function (err) {
        clinicPackagesLoading.classList.add('d-none');
        clinicPackagesRow.classList.remove('d-none');
        clinicPackagesRow.innerHTML = '<div class="col-12 text-danger">' + (err.message || 'Không tải được gói.') + '</div>';
      });
  }

  function openPurchaseConfirmModal(packageId) {
    var p = clinicPackagesMap[packageId];
    if (!p) { toast('Không tìm thấy thông tin gói.', 'danger'); return; }
    pendingPurchasePackageId = packageId;
    var name = p.name || ('Gói #' + packageId);
    if (confirmPurchaseText) confirmPurchaseText.textContent = 'Bạn có chắc muốn mua gói "' + name + '"?';
    if (purchaseConfirmModal && window.bootstrap) {
      var m = new bootstrap.Modal(purchaseConfirmModal);
      m.show();
    }
  }

  function confirmPurchase() {
    if (pendingPurchasePackageId == null) { toast('Chưa chọn gói.', 'danger'); return; }
    if (!accountId) { showError('Không tìm thấy tài khoản.'); return; }
    showError('');
    if (btnConfirmPurchase) btnConfirmPurchase.disabled = true;
    var pkgId = pendingPurchasePackageId;
    var btn = clinicPackagesRow && clinicPackagesRow.querySelector('.btn-purchase-clinic[data-package-id="' + pkgId + '"]');
    if (btn) btn.disabled = true;
    window.AuraAPI.purchaseClinicPackageDemo(accountId, pkgId)
      .then(function () {
        toast('Mua gói thành công.');
        if (purchaseConfirmModal && window.bootstrap) {
          var inst = bootstrap.Modal.getInstance(purchaseConfirmModal);
          if (inst) inst.hide();
        }
        pendingPurchasePackageId = null;
        load();
      })
      .catch(function (err) {
        showError(err.message || 'Mua gói thất bại.');
        if (btn) btn.disabled = false;
      })
      .finally(function () {
        if (btnConfirmPurchase) btnConfirmPurchase.disabled = false;
      });
  }

  function purchaseClinicPackage(packageId) {
    openPurchaseConfirmModal(packageId);
  }

  function openRenewModal(subscriptionId, packageId) {
    if (renewSubscriptionId) renewSubscriptionId.value = subscriptionId || '';
    if (renewPackageId) renewPackageId.value = packageId != null ? packageId : '';
    var p = packageId != null ? clinicPackagesMap[packageId] : null;
    if (renewConfirmText) {
      var name = p.name || ('Gói #' + packageId);
      renewConfirmText.textContent = 'Gia hạn gói "' + name + '"';
    }
    if (renewModal && window.bootstrap) {
      var m = new bootstrap.Modal(renewModal);
      m.show();
    }
  }

  function confirmRenew() {
    var subId = renewSubscriptionId && renewSubscriptionId.value ? renewSubscriptionId.value.trim() : '';
    var pkgId = renewPackageId && renewPackageId.value ? parseInt(renewPackageId.value, 10) : null;
    var p = (pkgId != null && clinicPackagesMap[pkgId]) ? clinicPackagesMap[pkgId] : null;
    var days = (p && p.duration_days != null) ? p.duration_days : 365;
    var credits = (p && p.image_limit != null) ? p.image_limit : 0;
    if (!subId) { toast('Thiếu subscription.', 'danger'); return; }
    if (btnConfirmRenew) btnConfirmRenew.disabled = true;
    window.AuraAPI.renewSubscription(subId, days, credits)
      .then(function () {
        toast('Gia hạn thành công.');
        if (renewModal && window.bootstrap) bootstrap.Modal.getInstance(renewModal).hide();
        load();
      })
      .catch(function (err) {
        toast(err.message || 'Gia hạn thất bại.', 'danger');
      })
      .finally(function () {
        if (btnConfirmRenew) btnConfirmRenew.disabled = false;
      });
  }

  function load() {
    if (!accountId) {
      showError('Không tìm thấy tài khoản.');
      if (loading) loading.classList.add('d-none');
      empty.classList.remove('d-none');
      empty.textContent = 'Không tìm thấy tài khoản.';
      return;
    }
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
          empty.textContent = 'Chưa có gói đăng ký nào. Mua gói ở trên.';
          return;
        }
        content.classList.remove('d-none');
        activeSummary.textContent = '';
        listSummary.textContent = 'Tổng: ' + count + ' gói.';
        var html = '';
        list.forEach(function (s) {
          var start = s.start_date ? new Date(s.start_date).toLocaleDateString('vi-VN') : '-';
          var end = s.end_date ? new Date(s.end_date).toLocaleDateString('vi-VN') : '-';
          var pkgName = (clinicPackagesMap[s.package_id] && clinicPackagesMap[s.package_id].name) || ('Gói #' + (s.package_id || '-'));
          var isClinic = s.package_id && CLINIC_PACKAGE_IDS.indexOf(s.package_id) !== -1;
          var renewBtn = isClinic && s.status === 'active'
            ? '<button type="button" class="btn btn-sm btn-outline-primary btn-renew" data-sub-id="' + (s.subscription_id || s.id) + '" data-package-id="' + (s.package_id != null ? s.package_id : '') + '">Gia hạn</button>'
            : '';
          html += '<tr>' +
            '<td>' + pkgName + '</td>' +
            '<td><span class="badge bg-' + (s.status === 'active' ? 'success' : 'secondary') + '">' + (s.status || '-') + '</span></td>' +
            '<td>' + (s.remaining_credits != null ? s.remaining_credits.toLocaleString('vi-VN') : '-') + '</td>' +
            '<td>' + start + '</td>' +
            '<td>' + end + '</td>' +
            '<td>' + renewBtn + '</td></tr>';
        });
        tbody.innerHTML = html;
        tbody.querySelectorAll('.btn-renew').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var subId = btn.getAttribute('data-sub-id');
            var pkgId = btn.getAttribute('data-package-id');
            openRenewModal(subId, pkgId ? parseInt(pkgId, 10) : null);
          });
        });
      })
      .catch(function (err) {
        loading.classList.add('d-none');
        empty.classList.remove('d-none');
        empty.textContent = err.message || 'Không tải được danh sách.';
        showError(err.message || 'Tải thất bại.');
      });
  }

  if (btnConfirmRenew) btnConfirmRenew.addEventListener('click', confirmRenew);
  if (btnConfirmPurchase) btnConfirmPurchase.addEventListener('click', confirmPurchase);

  loadClinicPackages();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
