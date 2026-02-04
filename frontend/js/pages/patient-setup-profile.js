/**
 * AURA - Patient Setup Profile
 * Trang nhập thông tin patient profile lần đầu sau khi đăng nhập Google
 */
(function () {
    'use strict';
  
    // Kiểm tra role Patient
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Patient')) {
      // Nếu không phải Patient, redirect về trang phù hợp
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
    var patientName = document.getElementById('patientName');
    var dateOfBirth = document.getElementById('dateOfBirth');
    var gender = document.getElementById('gender');
    var clinicId = document.getElementById('clinicId');
    var medicalHistory = document.getElementById('medicalHistory');
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
  
      window.AuraAPI.getPatientByAccount(accountId)
        .then(function (patient) {
          if (patient && patient.patient_id) {
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
  
        var name = patientName ? patientName.value.trim() : '';
        if (!name) {
          showError('Vui lòng nhập họ tên.');
          if (patientName) {
            patientName.classList.add('is-invalid');
            patientName.focus();
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
  
        if (patientName) patientName.classList.remove('is-invalid');
        if (clinicId) clinicId.classList.remove('is-invalid');
  
        setLoading(true);
  
        var payload = {
          account_id: accountId,
          patient_name: name,
          date_of_birth: dateOfBirth && dateOfBirth.value ? dateOfBirth.value : null,
          gender: gender && gender.value ? gender.value.trim() : null,
          medical_history: (medicalHistory && medicalHistory.value) ? medicalHistory.value.trim() : null
        };
  
        // Tạo patient profile trước
        window.AuraAPI.createPatient(payload)
          .then(function (result) {
            // Sau khi tạo patient profile thành công, cập nhật account.clinic_id
            return window.AuraAPI.updateAccountById(accountId, { clinic_id: selectedClinicId });
          })
          .then(function () {
            if (window.AuraUtils && window.AuraUtils.showToast) {
              window.AuraUtils.showToast('Đã tạo hồ sơ bệnh nhân thành công!', 'success');
            }
            // Cập nhật user object trong localStorage để có clinic_id mới
            var user = window.AuraAuth.getUser();
            if (user) {
              user.clinic_id = selectedClinicId;
              window.AuraAuth.setAuth(null, user, null);
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
  