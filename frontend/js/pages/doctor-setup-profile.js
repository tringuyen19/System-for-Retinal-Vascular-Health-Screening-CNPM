/**
 * AURA - Doctor Setup Profile
 * Trang nhập thông tin doctor profile lần đầu sau khi đăng ký
 */
(function () {
    'use strict';
  
    // Kiểm tra role Doctor
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) {
      // Nếu không phải Doctor, redirect về trang phù hợp
      if (window.AuraAuth && window.AuraAuth.redirectByRole) {
        window.AuraAuth.redirectByRole();
      } else {
        window.location.href = '../login.html';
      }
      return;
    }
  
    var user = window.AuraAuth.getUser();
    var accountId = user && user.account_id;
  
    var form = document.getElementById('setupForm');
    var doctorName = document.getElementById('doctorName');
    var specialization = document.getElementById('specialization');
    var licenseNumber = document.getElementById('licenseNumber');
    var clinicId = document.getElementById('clinicId');
    var btnSubmit = document.getElementById('btnSubmit');
    var setupError = document.getElementById('setupError');
  
    function showError(msg) {
      if (!setupError) return;
      setupError.textContent = msg || '';
      setupError.classList.toggle('d-none', !msg);
    }
  
    function setLoading(loading) {
      if (btnSubmit) {
        btnSubmit.disabled = loading;
        btnSubmit.innerHTML = loading 
          ? '<span class="spinner-border spinner-border-sm me-2"></span>Đang xử lý...'
          : '<i class="bi bi-check-circle me-2"></i>Hoàn tất thiết lập';
      }
    }
  
    // Load danh sách phòng khám đã được duyệt
    function loadClinics() {
      if (!clinicId) return;
      
      clinicId.innerHTML = '<option value="">-- Đang tải danh sách phòng khám --</option>';
      clinicId.disabled = true;
  
      window.AuraAPI.getVerifiedClinics()
        .then(function (res) {
          var clinics = (res && res.clinics) ? res.clinics : [];
          if (clinics.length === 0) {
            clinicId.innerHTML = '<option value="">-- Không có phòng khám nào được duyệt --</option>';
            showError('Hiện tại không có phòng khám nào được duyệt. Vui lòng liên hệ quản trị viên.');
            return;
          }
  
          clinicId.innerHTML = '<option value="">-- Chọn phòng khám --</option>';
          clinics.forEach(function (clinic) {
            var option = document.createElement('option');
            option.value = clinic.clinic_id;
            option.textContent = clinic.name + (clinic.address ? ' - ' + clinic.address : '');
            // Nếu account đã có clinic_id, tự động chọn
            if (user && user.clinic_id && user.clinic_id === clinic.clinic_id) {
              option.selected = true;
            }
            clinicId.appendChild(option);
          });
          clinicId.disabled = false;
        })
        .catch(function (err) {
          console.error('Lỗi khi tải danh sách phòng khám:', err);
          clinicId.innerHTML = '<option value="">-- Lỗi khi tải danh sách --</option>';
          showError('Không thể tải danh sách phòng khám. Vui lòng thử lại sau.');
        });
    }
  
    // Kiểm tra xem đã có profile chưa
    function checkExistingProfile() {
      if (!accountId) {
        showError('Không tìm thấy thông tin tài khoản. Vui lòng đăng nhập lại.');
        return;
      }
  
      window.AuraAPI.getDoctorByAccount(accountId)
        .then(function (doctor) {
          if (doctor && doctor.doctor_id) {
            // Đã có profile rồi, redirect đến dashboard
            window.location.href = 'dashboard.html';
          } else {
            // Chưa có profile, load danh sách clinic
            loadClinics();
          }
        })
        .catch(function (err) {
          // Nếu lỗi 404 hoặc không tìm thấy, đó là bình thường (chưa có profile)
          // Load danh sách clinic để hiển thị form
          console.log('Chưa có profile, hiển thị form setup');
          loadClinics();
        });
    }
  
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        showError('');
  
        var name = doctorName ? doctorName.value.trim() : '';
        if (!name) {
          showError('Vui lòng nhập họ tên bác sĩ.');
          if (doctorName) {
            doctorName.classList.add('is-invalid');
            doctorName.focus();
          }
          return;
        }
  
        var spec = specialization ? specialization.value.trim() : '';
        if (!spec) {
          showError('Vui lòng nhập chuyên khoa.');
          if (specialization) {
            specialization.classList.add('is-invalid');
            specialization.focus();
          }
          return;
        }
  
        var license = licenseNumber ? licenseNumber.value.trim() : '';
        if (!license) {
          showError('Vui lòng nhập số chứng chỉ hành nghề.');
          if (licenseNumber) {
            licenseNumber.classList.add('is-invalid');
            licenseNumber.focus();
          }
          return;
        }
  
        var selectedClinicId = clinicId && clinicId.value ? parseInt(clinicId.value, 10) : null;
        if (!selectedClinicId) {
          showError('Vui lòng chọn phòng khám.');
          if (clinicId) {
            clinicId.classList.add('is-invalid');
            clinicId.focus();
          }
          return;
        }
  
        // Xóa các class invalid
        if (doctorName) doctorName.classList.remove('is-invalid');
        if (specialization) specialization.classList.remove('is-invalid');
        if (licenseNumber) licenseNumber.classList.remove('is-invalid');
        if (clinicId) clinicId.classList.remove('is-invalid');
  
        setLoading(true);
  
        var payload = {
          account_id: accountId,
          doctor_name: name,
          specialization: spec,
          license_number: license
        };
  
        // Tạo doctor profile trước
        window.AuraAPI.createDoctor(payload)
          .then(function (result) {
            // Sau khi tạo doctor profile thành công, cập nhật account.clinic_id nếu chưa có
            if (!user.clinic_id || user.clinic_id !== selectedClinicId) {
              return window.AuraAPI.updateAccountById(accountId, { clinic_id: selectedClinicId });
            }
            return Promise.resolve();
          })
          .then(function () {
            if (window.AuraUtils && window.AuraUtils.showToast) {
              window.AuraUtils.showToast('Đã tạo hồ sơ bác sĩ thành công!', 'success');
            }
            // Cập nhật user object trong localStorage để có clinic_id mới
            var updatedUser = window.AuraAuth.getUser();
            if (updatedUser) {
              updatedUser.clinic_id = selectedClinicId;
              window.AuraAuth.setAuth(null, updatedUser, null);
            }
            // Redirect đến dashboard sau khi tạo thành công
            setTimeout(function () {
              window.location.href = 'dashboard.html';
            }, 500);
          })
          .catch(function (err) {
            var msg = err && err.message ? err.message : 'Tạo hồ sơ thất bại. Vui lòng thử lại.';
            showError(msg);
            setLoading(false);
          });
      });
    }
  
    // Kiểm tra profile khi load trang
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', checkExistingProfile);
    } else {
      checkExistingProfile();
    }
  })();
  