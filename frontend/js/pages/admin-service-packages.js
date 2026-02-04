// AURA - Admin Service Packages Management (FR-34)
(function () {
  'use strict';
  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var pageError = document.getElementById('pageError');
  var packagesTableBody = document.getElementById('packagesTableBody');
  var btnCreatePackage = document.getElementById('btnCreatePackage');
  var modalPackage = new bootstrap.Modal(document.getElementById('modalPackage'));
  var modalPackageTitle = document.getElementById('modalPackageTitle');
  var packageId = document.getElementById('packageId');
  var packageName = document.getElementById('packageName');
  var packagePrice = document.getElementById('packagePrice');
  var packagePaymentModel = document.getElementById('packagePaymentModel');
  var packageStatus = document.getElementById('packageStatus');
  var btnSavePackage = document.getElementById('btnSavePackage');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function renderTable(list) {
    if (!packagesTableBody) return;
    if (!list || list.length === 0) {
      packagesTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Không có gói dịch vụ</td></tr>';
      return;
    }
    var html = '';
    list.forEach(function (pkg) {
      html += '<tr>';
      html += '<td>' + pkg.id + '</td>';
      html += '<td>' + pkg.name + '</td>';
      html += '<td>' + new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(pkg.price) + '</td>';
      html += '<td>' + paymentModelLabel(pkg.payment_model) + '</td>';
      html += '<td>' + (pkg.status === 'active' ? '<span class="badge bg-success">Kích hoạt</span>' : '<span class="badge bg-secondary">Tạm ngưng</span>') + '</td>';
      html += '<td>';
      html += '<button class="btn btn-sm btn-primary me-1" onclick="window.editPackage(' + pkg.id + ')"><i class="bi bi-pencil"></i></button>';
      html += '<button class="btn btn-sm btn-danger" onclick="window.deletePackage(' + pkg.id + ')"><i class="bi bi-trash"></i></button>';
      html += '</td>';
      html += '</tr>';
    });
    packagesTableBody.innerHTML = html;
  }

  function paymentModelLabel(model) {
    switch (model) {
      case 'per_use': return 'Theo lượt';
      case 'monthly': return 'Theo tháng';
      case 'yearly': return 'Theo năm';
      default: return model;
    }
  }

  function loadPackages() {
    showError('');
    packagesTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Đang tải...</td></tr>';
    window.AuraAPI.getServicePackages()
      .then(function (res) {
        renderTable(res && res.packages ? res.packages : []);
      })
      .catch(function (e) {
        showError('Lỗi tải gói dịch vụ');
        packagesTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Lỗi tải dữ liệu</td></tr>';
      });
  }

  window.editPackage = function (id) {
    showError('');
    window.AuraAPI.getServicePackageById(id)
      .then(function (pkg) {
        packageId.value = pkg.id;
        packageName.value = pkg.name;
        packagePrice.value = pkg.price;
        packagePaymentModel.value = pkg.payment_model;
        packageStatus.value = pkg.status;
        modalPackageTitle.textContent = 'Sửa gói dịch vụ';
        modalPackage.show();
      })
      .catch(function () {
        showError('Không tìm thấy gói dịch vụ');
      });
  };

  window.deletePackage = function (id) {
    if (!confirm('Bạn có chắc muốn xóa gói dịch vụ này?')) return;
    window.AuraAPI.deleteServicePackage(id)
      .then(function () {
        loadPackages();
      })
      .catch(function () {
        showError('Xóa thất bại');
      });
  };

  btnCreatePackage && btnCreatePackage.addEventListener('click', function () {
    showError('');
    packageId.value = '';
    packageName.value = '';
    packagePrice.value = '';
    packagePaymentModel.value = 'per_use';
    packageStatus.value = 'active';
    modalPackageTitle.textContent = 'Thêm gói dịch vụ';
    modalPackage.show();
  });

  btnSavePackage && btnSavePackage.addEventListener('click', function () {
    showError('');
    var data = {
      id: packageId.value,
      name: packageName.value.trim(),
      price: parseInt(packagePrice.value, 10) || 0,
      payment_model: packagePaymentModel.value,
      status: packageStatus.value
    };
    if (!data.name || data.price <= 0) {
      showError('Tên gói và giá phải hợp lệ!');
      return;
    }
    var apiCall = data.id ? window.AuraAPI.updateServicePackage(data) : window.AuraAPI.createServicePackage(data);
    apiCall.then(function () {
      modalPackage.hide();
      loadPackages();
    }).catch(function () {
      showError('Lưu thất bại');
    });
  });

  loadPackages();
})();
