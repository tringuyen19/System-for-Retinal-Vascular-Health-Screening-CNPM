/**
 * AURA - Clinic Registration Page (FR-22)
 * Form validation and submission for clinic registration with manager account
 */

(function () {
  'use strict';

  const form = document.getElementById('clinicRegisterForm');
  const btnSubmit = document.getElementById('btnSubmit');
  const registerErrorEl = document.getElementById('registerError');
  
  // Logo upload elements
  const logoDropZone = document.getElementById('logoDropZone');
  const logoFileInput = document.getElementById('logoFileInput');
  const btnSelectLogo = document.getElementById('btnSelectLogo');
  const logoPreviewWrap = document.getElementById('logoPreviewWrap');
  const logoPreviewImg = document.getElementById('logoPreviewImg');
  const logoFileName = document.getElementById('logoFileName');
  const btnRemoveLogo = document.getElementById('btnRemoveLogo');
  const clinicLogoInput = document.getElementById('clinicLogo');
  
  let selectedLogoFile = null;
  let logoUploadedUrl = null;

  function showError(msg) {
    if (!registerErrorEl) return;
    registerErrorEl.textContent = msg || 'Đăng ký thất bại.';
    registerErrorEl.classList.remove('d-none');
  }

  function hideError() {
    if (registerErrorEl) registerErrorEl.classList.add('d-none');
  }

  function setLoading(loading) {
    if (btnSubmit) {
      btnSubmit.disabled = loading;
      btnSubmit.innerHTML = loading 
        ? '<span class="spinner-border spinner-border-sm me-2"></span>Đang xử lý...' 
        : '<i class="bi bi-check-circle me-2"></i>Đăng ký phòng khám';
    }
  }

  function validateForm() {
    let valid = true;
    const clinicName = document.getElementById('clinicName');
    const clinicPhone = document.getElementById('clinicPhone');
    const clinicAddress = document.getElementById('clinicAddress');
    const clinicLogo = document.getElementById('clinicLogo');
    const managerEmail = document.getElementById('managerEmail');
    const managerPassword = document.getElementById('managerPassword');
    const managerConfirmPassword = document.getElementById('managerConfirmPassword');

    // Reset validation
    [clinicName, clinicPhone, clinicAddress, managerEmail, managerPassword, managerConfirmPassword].forEach(el => {
      if (el) el.classList.remove('is-invalid');
    });

    // Validate clinic name
    if (!clinicName || !clinicName.value.trim()) {
      if (clinicName) {
        clinicName.classList.add('is-invalid');
        document.getElementById('clinicNameError').textContent = 'Vui lòng nhập tên phòng khám.';
      }
      valid = false;
    }

    // Validate phone
    if (!clinicPhone || !clinicPhone.value.trim()) {
      if (clinicPhone) {
        clinicPhone.classList.add('is-invalid');
        document.getElementById('clinicPhoneError').textContent = 'Vui lòng nhập số điện thoại.';
      }
      valid = false;
    }

    // Validate address
    if (!clinicAddress || !clinicAddress.value.trim()) {
      if (clinicAddress) {
        clinicAddress.classList.add('is-invalid');
        document.getElementById('clinicAddressError').textContent = 'Vui lòng nhập địa chỉ.';
      }
      valid = false;
    }

    // Logo is optional - no validation needed (already validated when uploaded)

    // Validate manager email
    if (!managerEmail || !managerEmail.value.trim()) {
      if (managerEmail) {
        managerEmail.classList.add('is-invalid');
        document.getElementById('managerEmailError').textContent = 'Vui lòng nhập email.';
      }
      valid = false;
    } else if (managerEmail) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(managerEmail.value.trim())) {
        managerEmail.classList.add('is-invalid');
        document.getElementById('managerEmailError').textContent = 'Email không hợp lệ.';
        valid = false;
      }
    }

    // Validate password
    if (!managerPassword || managerPassword.value.length < 6) {
      if (managerPassword) {
        managerPassword.classList.add('is-invalid');
        document.getElementById('managerPasswordError').textContent = 'Mật khẩu tối thiểu 6 ký tự.';
      }
      valid = false;
    }

    // Validate confirm password
    if (!managerConfirmPassword || !managerPassword) {
      if (managerConfirmPassword) {
        managerConfirmPassword.classList.add('is-invalid');
        document.getElementById('managerConfirmPasswordError').textContent = 'Vui lòng xác nhận mật khẩu.';
      }
      valid = false;
    } else if (managerPassword.value !== managerConfirmPassword.value) {
      managerConfirmPassword.classList.add('is-invalid');
      document.getElementById('managerConfirmPasswordError').textContent = 'Mật khẩu không khớp.';
      valid = false;
    }

    return valid;
  }

  function parseDocuments(docText) {
    if (!docText || !docText.trim()) return null;
    const lines = docText.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    if (lines.length === 0) return null;
    // Validate URLs
    const validUrls = [];
    for (const line of lines) {
      try {
        new URL(line);
        validUrls.push(line);
      } catch (e) {
        console.warn('Invalid document URL:', line);
      }
    }
    return validUrls.length > 0 ? validUrls : null;
  }

  if (form) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      hideError();

      if (!validateForm()) {
        showError('Vui lòng kiểm tra lại các trường đã nhập.');
        return;
      }

      setLoading(true);

      try {
        // Collect form data
        const clinicName = document.getElementById('clinicName').value.trim();
        const clinicPhone = document.getElementById('clinicPhone').value.trim();
        const clinicAddress = document.getElementById('clinicAddress').value.trim();
        const licenseNumber = document.getElementById('licenseNumber').value.trim() || null;
        const taxId = document.getElementById('taxId').value.trim() || null;
        const verificationDocumentsText = document.getElementById('verificationDocuments').value.trim();
        const managerEmail = document.getElementById('managerEmail').value.trim();
        const managerPassword = document.getElementById('managerPassword').value;

        // Parse documents
        const verificationDocuments = parseDocuments(verificationDocumentsText);

        // Build payload
        const payload = {
          name: clinicName,
          address: clinicAddress,
          phone: clinicPhone,
          manager_email: managerEmail,
          manager_password: managerPassword
        };

        // Add optional fields
        // Use logoUploadedUrl if available, otherwise use hidden input value
        const logoUrl = logoUploadedUrl || (clinicLogoInput ? clinicLogoInput.value.trim() : null);
        if (logoUrl) payload.logo_url = logoUrl;
        if (licenseNumber) payload.license_number = licenseNumber;
        if (taxId) payload.tax_id = taxId;
        if (verificationDocuments) payload.verification_documents = verificationDocuments;

        // Call API
        const res = await window.AuraAPI.registerClinic(payload);

        // Success
        if (window.AuraUtils && window.AuraUtils.showToast) {
          window.AuraUtils.showToast('Đăng ký phòng khám thành công! Đang chờ xác minh.', 'success');
        }

        // Show success message and redirect
        setTimeout(() => {
          alert('Đăng ký phòng khám thành công!\n\nPhòng khám của bạn đang ở trạng thái "Chờ xác minh". ' +
                'Quản trị viên sẽ xem xét và thông báo kết quả qua email.\n\n' +
                'Bạn chỉ có thể đăng nhập sau khi phòng khám được quản trị viên duyệt.');
          window.location.href = 'login.html';
        }, 500);

      } catch (err) {
        let msg = err && err.message ? err.message : 'Đăng ký thất bại. Vui lòng thử lại.';
        
        // Handle specific error cases
        if (msg.indexOf('Failed to fetch') !== -1 || msg.indexOf('NetworkError') !== -1 || msg.indexOf('Load failed') !== -1) {
          msg = 'Không thể kết nối máy chủ. Kiểm tra backend đã chạy tại http://localhost:9999 chưa.';
        } else if (msg.indexOf('already exists') !== -1 || msg.indexOf('đã được đăng ký') !== -1) {
          msg = 'Email này đã được sử dụng. Vui lòng chọn email khác.';
        } else if (msg.indexOf('validation') !== -1 || msg.indexOf('không hợp lệ') !== -1) {
          msg = 'Dữ liệu không hợp lệ. Vui lòng kiểm tra lại các trường đã nhập.';
        }

        showError(msg);
        
        // Scroll to error
        if (registerErrorEl) {
          registerErrorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      } finally {
        setLoading(false);
      }
    });
  }

  // ========== Logo Upload Functions ==========
  
  function readFileAsDataUrl(file) {
    return new Promise(function (resolve, reject) {
      const reader = new FileReader();
      reader.onload = function () { resolve(reader.result); };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  function onLogoFileSelect(file) {
    if (!file || !file.type.match(/^image\//)) {
      showError('Vui lòng chọn file ảnh (JPG, PNG, GIF, WebP).');
      return;
    }
    
    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      showError('File quá lớn. Vui lòng chọn file nhỏ hơn 5MB.');
      return;
    }
    
    selectedLogoFile = file;
    logoUploadedUrl = null;
    
    // Preview image
    readFileAsDataUrl(file).then(function (dataUrl) {
      if (logoPreviewImg) logoPreviewImg.src = dataUrl;
      if (logoFileName) logoFileName.textContent = file.name;
      if (logoPreviewWrap) logoPreviewWrap.classList.remove('d-none');
      if (logoDropZone) logoDropZone.classList.add('border-success');
      
      // Auto upload
      uploadLogoFile(file);
    }).catch(function () {
      showError('Không đọc được file.');
    });
  }

  function uploadLogoFile(file) {
    if (!file) return;
    
    // Show loading state
    if (logoDropZone) {
      logoDropZone.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div><p class="mt-2 mb-0 small">Đang upload...</p>';
    }
    
    // Upload file with category='clinic' (no auth required)
    window.AuraAPI.uploadFile(file, 'clinic')
      .then(function (uploaded) {
        // uploaded: { url, full_url, ... }
        const imageUrl = (uploaded && (uploaded.full_url || uploaded.url)) || null;
        if (!imageUrl) {
          throw new Error('Upload file thành công nhưng không nhận được URL.');
        }
        
        logoUploadedUrl = imageUrl;
        if (clinicLogoInput) clinicLogoInput.value = imageUrl;
        
        // Update UI
        if (logoDropZone) {
          logoDropZone.innerHTML = '<i class="bi bi-check-circle-fill text-success display-6"></i><p class="mt-2 mb-0 small text-success">Upload thành công!</p>';
        }
        
        hideError();
      })
      .catch(function (err) {
        showError(err.message || 'Upload logo thất bại. Vui lòng thử lại.');
        selectedLogoFile = null;
        if (logoPreviewWrap) logoPreviewWrap.classList.add('d-none');
        if (logoFileInput) logoFileInput.value = '';
        resetLogoDropZone();
      });
  }

  function resetLogoDropZone() {
    if (logoDropZone) {
      logoDropZone.innerHTML = '<i class="bi bi-image display-6 text-muted"></i><p class="mt-2 mb-1 small">Kéo thả logo vào đây hoặc bấm để chọn file</p><input type="file" id="logoFileInput" accept="image/*" class="d-none"><button type="button" class="btn btn-outline-primary btn-sm mt-2" id="btnSelectLogo">Chọn file</button>';
      logoDropZone.classList.remove('border-success', 'border-primary');
      // Re-attach event listeners
      const newFileInput = document.getElementById('logoFileInput');
      const newBtnSelect = document.getElementById('btnSelectLogo');
      if (newFileInput) newFileInput.addEventListener('change', handleLogoFileChange);
      if (newBtnSelect) newBtnSelect.addEventListener('click', function() { newFileInput && newFileInput.click(); });
    }
  }

  function handleLogoFileChange(e) {
    const file = e.target.files && e.target.files[0];
    if (file) onLogoFileSelect(file);
  }

  // Logo upload event listeners
  if (btnSelectLogo) {
    btnSelectLogo.addEventListener('click', function () {
      logoFileInput && logoFileInput.click();
    });
  }
  
  if (logoFileInput) {
    logoFileInput.addEventListener('change', handleLogoFileChange);
  }

  if (logoDropZone) {
    logoDropZone.addEventListener('dragover', function (e) {
      e.preventDefault();
      logoDropZone.classList.add('border-primary');
    });
    
    logoDropZone.addEventListener('dragleave', function () {
      logoDropZone.classList.remove('border-primary');
    });
    
    logoDropZone.addEventListener('drop', function (e) {
      e.preventDefault();
      logoDropZone.classList.remove('border-primary');
      const file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (file) onLogoFileSelect(file);
    });
    
    logoDropZone.addEventListener('click', function () {
      logoFileInput && logoFileInput.click();
    });
  }

  if (btnRemoveLogo) {
    btnRemoveLogo.addEventListener('click', function () {
      selectedLogoFile = null;
      logoUploadedUrl = null;
      if (clinicLogoInput) clinicLogoInput.value = '';
      if (logoPreviewWrap) logoPreviewWrap.classList.add('d-none');
      if (logoFileInput) logoFileInput.value = '';
      resetLogoDropZone();
    });
  }

  // ========== Form Validation ==========
  
  // Real-time validation
  const inputs = ['clinicName', 'clinicPhone', 'clinicAddress', 'managerEmail', 'managerPassword', 'managerConfirmPassword'];
  inputs.forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener('blur', function() {
        if (this.value.trim()) {
          validateForm();
        }
      });
    }
  });

  // Password confirmation validation
  const managerPassword = document.getElementById('managerPassword');
  const managerConfirmPassword = document.getElementById('managerConfirmPassword');
  if (managerPassword && managerConfirmPassword) {
    managerConfirmPassword.addEventListener('input', function() {
      if (this.value && managerPassword.value !== this.value) {
        this.classList.add('is-invalid');
        document.getElementById('managerConfirmPasswordError').textContent = 'Mật khẩu không khớp.';
      } else {
        this.classList.remove('is-invalid');
      }
    });
  }
})();
