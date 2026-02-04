/**
 * AURA - Admin Billing (FR-34)
 * Quản lý gói dịch vụ (giá, giới hạn, thời hạn, loại, active) + quản lý thanh toán.
 */
(function () {
    'use strict';
  
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;
  
    var pageError = document.getElementById('pageError');
  
    // Packages
    var packagesTbody = document.getElementById('packagesTbody');
    var packagesCount = document.getElementById('packagesCount');
    var filterPackageType = document.getElementById('filterPackageType');
    var filterPackageActive = document.getElementById('filterPackageActive');
    var btnReloadPackages = document.getElementById('btnReloadPackages');
    var btnNewPackage = document.getElementById('btnNewPackage');
  
    // Package modal
    var packageModal = document.getElementById('packageModal');
    var packageModalTitle = document.getElementById('packageModalTitle');
    var packageModalError = document.getElementById('packageModalError');
    var packageId = document.getElementById('packageId');
    var packageName = document.getElementById('packageName');
    var packageType = document.getElementById('packageType');
    var packageActive = document.getElementById('packageActive');
    var packagePrice = document.getElementById('packagePrice');
    var packageImageLimit = document.getElementById('packageImageLimit');
    var packageDurationDays = document.getElementById('packageDurationDays');
    var btnSavePackage = document.getElementById('btnSavePackage');
  
    // Payments
    var paymentsTbody = document.getElementById('paymentsTbody');
    var paymentsCount = document.getElementById('paymentsCount');
    var filterPaymentStatus = document.getElementById('filterPaymentStatus');
    var btnReloadPayments = document.getElementById('btnReloadPayments');
  
    function toast(msg, type) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(msg, type || 'success');
    }
  
    function showError(msg) {
      if (!pageError) return;
      pageError.textContent = msg || '';
      pageError.classList.toggle('d-none', !msg);
    }
  
    function showModalError(msg) {
      if (!packageModalError) return;
      packageModalError.textContent = msg || '';
      packageModalError.classList.toggle('d-none', !msg);
    }
  
    function formatMoney(n) {
      if (n == null || isNaN(n)) return '-';
      return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(Number(n));
    }
  
    function formatDate(s) {
      if (!s) return '-';
      try {
        var d = new Date(s);
        return isNaN(d.getTime()) ? s : d.toLocaleString('vi-VN');
      } catch (e) {
        return s;
      }
    }
  
    // -------- Packages --------
    var packagesCache = []; // last loaded list
  
    function getPackageFilters() {
      var type = filterPackageType ? (filterPackageType.value || '').trim() : '';
      var activeRaw = filterPackageActive ? (filterPackageActive.value || '').trim() : '';
      var active = activeRaw === '' ? null : (activeRaw === '1');
      return { type: type || undefined, active: active };
    }
  
    function renderPackages(list) {
      packagesCache = Array.isArray(list) ? list : [];
      if (packagesCount) packagesCount.textContent = String(packagesCache.length);
      if (!packagesTbody) return;
  
      if (!packagesCache.length) {
        packagesTbody.innerHTML = '<tr><td colspan="8" class="text-muted">Không có gói.</td></tr>';
        return;
      }
  
      packagesTbody.innerHTML = packagesCache.map(function (p) {
        var id = p.package_id;
        var type = (p.package_type || '').toLowerCase() || '-';
        var active = (p.is_active !== false);
        var badge = active ? '<span class="badge bg-success">Đang bán</span>' : '<span class="badge bg-secondary">Tạm ngưng</span>';
        var typeBadge = type === 'clinic'
          ? '<span class="badge bg-primary-subtle text-primary border border-primary-subtle">Phòng khám</span>'
          : '<span class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle">Bệnh nhân</span>';
        var iconToggle = active
          ? '<button class="btn btn-outline-secondary btn-sm btn-toggle" data-id="' + id + '" data-active="1" title="Tạm ngưng"><i class="bi bi-pause-circle"></i></button>'
          : '<button class="btn btn-outline-success btn-sm btn-toggle" data-id="' + id + '" data-active="0" title="Bật bán"><i class="bi bi-play-circle"></i></button>';
  
        return '<tr>' +
          '<td>' + id + '</td>' +
          '<td><div class="fw-semibold">' + (p.name || '-') + '</div></td>' +
          '<td>' + typeBadge + '</td>' +
          '<td class="text-end">' + formatMoney(p.price) + '</td>' +
          '<td class="text-end">' + (p.image_limit != null ? Number(p.image_limit).toLocaleString('vi-VN') : '-') + '</td>' +
          '<td class="text-end">' + (p.duration_days != null ? (p.duration_days + ' ngày') : '-') + '</td>' +
          '<td>' + badge + '</td>' +
          '<td class="text-end aura-table-actions">' +
            '<div class="btn-group btn-group-sm" role="group" aria-label="Thao tác gói">' +
              '<button class="btn btn-outline-primary btn-edit" data-id="' + id + '" title="Sửa"><i class="bi bi-pencil-square"></i></button>' +
              iconToggle +
              '<button class="btn btn-outline-danger btn-delete" data-id="' + id + '" title="Xóa"><i class="bi bi-trash"></i></button>' +
            '</div>' +
          '</td>' +
        '</tr>';
      }).join('');
  
      packagesTbody.querySelectorAll('.btn-edit').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var id = parseInt(btn.getAttribute('data-id'), 10);
          var pkg = packagesCache.find(function (x) { return x.package_id === id; });
          openEditPackage(pkg);
        });
      });
      packagesTbody.querySelectorAll('.btn-toggle').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var id = parseInt(btn.getAttribute('data-id'), 10);
          var active = btn.getAttribute('data-active') === '1';
          togglePackageActive(id, active);
        });
      });
      packagesTbody.querySelectorAll('.btn-delete').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var id = parseInt(btn.getAttribute('data-id'), 10);
          deletePackage(id);
        });
      });
    }
  
    function loadPackages() {
      showError('');
      if (packagesTbody) packagesTbody.innerHTML = '<tr><td colspan="8" class="text-muted">Đang tải...</td></tr>';
      var f = getPackageFilters();
      return window.AuraAPI.adminListServicePackages(f)
        .then(function (data) {
          renderPackages((data && data.packages) || []);
        })
        .catch(function (e) {
          if (packagesTbody) packagesTbody.innerHTML = '<tr><td colspan="8" class="text-danger">' + (e.message || 'Lỗi tải gói') + '</td></tr>';
          showError(e.message || 'Không tải được gói dịch vụ.');
        });
    }
  
    function openCreatePackage() {
      showModalError('');
      if (packageModalTitle) packageModalTitle.textContent = 'Tạo gói';
      if (packageId) packageId.value = '';
      if (packageName) packageName.value = '';
      if (packageType) packageType.value = 'patient';
      if (packageActive) packageActive.checked = true;
      if (packagePrice) packagePrice.value = '';
      if (packageImageLimit) packageImageLimit.value = '';
      if (packageDurationDays) packageDurationDays.value = '';
      bootstrap.Modal.getOrCreateInstance(packageModal).show();
    }
  
    function openEditPackage(pkg) {
      if (!pkg) return;
      showModalError('');
      if (packageModalTitle) packageModalTitle.textContent = 'Cập nhật gói #' + pkg.package_id;
      if (packageId) packageId.value = String(pkg.package_id);
      if (packageName) packageName.value = pkg.name || '';
      if (packageType) packageType.value = (pkg.package_type || 'patient');
      if (packageActive) packageActive.checked = (pkg.is_active !== false);
      if (packagePrice) packagePrice.value = (pkg.price != null ? Number(pkg.price) : '');
      if (packageImageLimit) packageImageLimit.value = (pkg.image_limit != null ? Number(pkg.image_limit) : '');
      if (packageDurationDays) packageDurationDays.value = (pkg.duration_days != null ? Number(pkg.duration_days) : '');
      bootstrap.Modal.getOrCreateInstance(packageModal).show();
    }
  
    function buildPackagePayload() {
      var id = packageId && packageId.value ? parseInt(packageId.value, 10) : null;
      var name = packageName && packageName.value ? packageName.value.trim() : '';
      var type = packageType && packageType.value ? packageType.value.trim() : '';
      var isActive = packageActive ? !!packageActive.checked : true;
      var price = packagePrice && packagePrice.value !== '' ? Number(packagePrice.value) : NaN;
      var limit = packageImageLimit && packageImageLimit.value !== '' ? parseInt(packageImageLimit.value, 10) : NaN;
      var days = packageDurationDays && packageDurationDays.value !== '' ? parseInt(packageDurationDays.value, 10) : NaN;
  
      if (!name) return { error: 'Tên gói là bắt buộc.' };
      if (!type || (type !== 'patient' && type !== 'clinic')) return { error: 'Loại gói không hợp lệ.' };
      if (!isFinite(price) || price < 0) return { error: 'Giá không hợp lệ.' };
      if (!isFinite(limit) || limit < 0) return { error: 'Lượt ảnh không hợp lệ.' };
      if (!isFinite(days) || days < 1) return { error: 'Thời hạn (ngày) không hợp lệ.' };
  
      return {
        id: id,
        payload: {
          name: name,
          package_type: type,
          is_active: isActive,
          price: price,
          image_limit: limit,
          duration_days: days
        }
      };
    }
  
    function savePackage() {
      showModalError('');
      var built = buildPackagePayload();
      if (built.error) {
        showModalError(built.error);
        return;
      }
      var id = built.id;
      var payload = built.payload;
  
      var p = id
        ? window.AuraAPI.adminUpdateServicePackage(id, payload)
        : window.AuraAPI.adminCreateServicePackage(payload);
  
      p.then(function () {
        toast(id ? 'Đã cập nhật gói.' : 'Đã tạo gói.', 'success');
        bootstrap.Modal.getOrCreateInstance(packageModal).hide();
        loadPackages();
      }).catch(function (e) {
        showModalError(e.message || 'Lưu thất bại.');
      });
    }
  
    function togglePackageActive(id, currentlyActive) {
      var next = !currentlyActive;
      window.AuraAPI.adminUpdateServicePackage(id, { is_active: next })
        .then(function () {
          toast(next ? 'Đã bật gói.' : 'Đã tạm ngưng gói.', 'success');
          loadPackages();
        })
        .catch(function (e) {
          toast(e.message || 'Cập nhật thất bại.', 'danger');
        });
    }
  
    function deletePackage(id) {
      if (!confirm('Xóa gói #' + id + '? Hành động này không thể hoàn tác.')) return;
      window.AuraAPI.adminDeleteServicePackage(id)
        .then(function () {
          toast('Đã xóa gói.', 'success');
          loadPackages();
        })
        .catch(function (e) {
          toast(e.message || 'Xóa thất bại.', 'danger');
        });
    }
  
    // -------- Payments --------
    var paymentsCache = [];
  
    function getPaymentFilters() {
      var status = filterPaymentStatus ? (filterPaymentStatus.value || '').trim() : '';
      return { status: status || undefined };
    }
  
    function renderPayments(list) {
      paymentsCache = Array.isArray(list) ? list : [];
      if (paymentsCount) paymentsCount.textContent = String(paymentsCache.length);
      if (!paymentsTbody) return;
  
      if (!paymentsCache.length) {
        paymentsTbody.innerHTML = '<tr><td colspan="7" class="text-muted">Không có thanh toán.</td></tr>';
        return;
      }
  
      paymentsTbody.innerHTML = paymentsCache.map(function (p) {
        var status = (p.status || '').toLowerCase() || '-';
        var badge = status === 'completed' ? 'bg-success' :
          status === 'pending' ? 'bg-warning text-dark' :
          status === 'failed' ? 'bg-danger' :
          status === 'refunded' ? 'bg-secondary' : 'bg-light text-dark';
  
        var actions = '';
        if (status === 'pending') {
          actions =
            '<div class="btn-group btn-group-sm" role="group" aria-label="Duyệt payment">' +
              '<button class="btn btn-outline-success btn-pay-complete" data-id="' + p.payment_id + '" title="Complete"><i class="bi bi-check2-circle"></i></button>' +
              '<button class="btn btn-outline-danger btn-pay-fail" data-id="' + p.payment_id + '" title="Fail"><i class="bi bi-x-circle"></i></button>' +
            '</div>';
        } else if (status === 'completed') {
          actions =
            '<div class="btn-group btn-group-sm" role="group" aria-label="Refund payment">' +
              '<button class="btn btn-outline-secondary btn-pay-refund" data-id="' + p.payment_id + '" title="Refund"><i class="bi bi-arrow-counterclockwise"></i></button>' +
            '</div>';
        } else {
          actions = '<span class="text-muted small">-</span>';
        }
  
        return '<tr>' +
          '<td>#' + (p.payment_id != null ? p.payment_id : '-') + '</td>' +
          '<td>#' + (p.subscription_id != null ? p.subscription_id : '-') + '</td>' +
          '<td>' + (p.payment_method || '-') + '</td>' +
          '<td>' + formatDate(p.payment_time) + '</td>' +
          '<td class="text-end">' + formatMoney(p.amount) + '</td>' +
          '<td><span class="badge ' + badge + '">' + status + '</span></td>' +
          '<td class="text-end aura-table-actions">' + actions + '</td>' +
        '</tr>';
      }).join('');
  
      paymentsTbody.querySelectorAll('.btn-pay-complete').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var id = parseInt(btn.getAttribute('data-id'), 10);
          if (!confirm('Đánh dấu payment #' + id + ' là completed?')) return;
          window.AuraAPI.adminCompletePayment(id)
            .then(function () { toast('Đã complete payment.', 'success'); loadPayments(); })
            .catch(function (e) { toast(e.message || 'Lỗi', 'danger'); });
        });
      });
      paymentsTbody.querySelectorAll('.btn-pay-fail').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var id = parseInt(btn.getAttribute('data-id'), 10);
          if (!confirm('Đánh dấu payment #' + id + ' là failed?')) return;
          window.AuraAPI.adminFailPayment(id)
            .then(function () { toast('Đã fail payment.', 'warning'); loadPayments(); })
            .catch(function (e) { toast(e.message || 'Lỗi', 'danger'); });
        });
      });
      paymentsTbody.querySelectorAll('.btn-pay-refund').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var id = parseInt(btn.getAttribute('data-id'), 10);
          if (!confirm('Refund payment #' + id + '?')) return;
          window.AuraAPI.adminRefundPayment(id)
            .then(function () { toast('Đã refund payment.', 'success'); loadPayments(); })
            .catch(function (e) { toast(e.message || 'Lỗi', 'danger'); });
        });
      });
    }
  
    function loadPayments() {
      showError('');
      if (paymentsTbody) paymentsTbody.innerHTML = '<tr><td colspan="7" class="text-muted">Đang tải...</td></tr>';
      var f = getPaymentFilters();
      return window.AuraAPI.adminListPayments(f)
        .then(function (data) {
          renderPayments((data && data.payments) || []);
        })
        .catch(function (e) {
          if (paymentsTbody) paymentsTbody.innerHTML = '<tr><td colspan="7" class="text-danger">' + (e.message || 'Lỗi tải thanh toán') + '</td></tr>';
          showError(e.message || 'Không tải được danh sách thanh toán.');
        });
    }
  
    // Events
    if (btnReloadPackages) btnReloadPackages.addEventListener('click', loadPackages);
    if (filterPackageType) filterPackageType.addEventListener('change', loadPackages);
    if (filterPackageActive) filterPackageActive.addEventListener('change', loadPackages);
    if (btnNewPackage) btnNewPackage.addEventListener('click', openCreatePackage);
    if (btnSavePackage) btnSavePackage.addEventListener('click', savePackage);
  
    if (btnReloadPayments) btnReloadPayments.addEventListener('click', loadPayments);
    if (filterPaymentStatus) filterPaymentStatus.addEventListener('change', loadPayments);
  
    // Init
    loadPackages();
    loadPayments();
  })();
  
  