/**
 * AURA - Doctor Bulk Upload Images (FR-24)
 * Upload multiple retinal images in batch with progress tracking
 */
(function () {
    'use strict';
  
    // Check role: Doctor, Admin, or ClinicManager
    if (!window.AuraAuth || !window.AuraAuth.getRole) {
      console.error('AuraAuth not available');
      return;
    }
    var allowedRoles = ['Doctor', 'Admin', 'ClinicManager'];
    var userRole = window.AuraAuth.getRole(); // Get role from localStorage
    if (!allowedRoles.includes(userRole)) {
      console.error('Unauthorized role:', userRole);
      return;
    }
  
    var user = window.AuraAuth.getUser();
    var accountId = user && user.account_id;
    var clinicId = user && user.clinic_id; // Get clinic_id from user object
  
    // DOM elements
    var patientSelect = document.getElementById('patientSelect');
    var clinicSelect = document.getElementById('clinicSelect');
    var globalImageType = document.getElementById('globalImageType');
    var globalEyeSide = document.getElementById('globalEyeSide');
    var btnApplyGlobal = document.getElementById('btnApplyGlobal');
    var dropZone = document.getElementById('dropZone');
    var fileInput = document.getElementById('fileInput');
    var btnSelectFiles = document.getElementById('btnSelectFiles');
    var filesList = document.getElementById('filesList');
    var fileCount = document.getElementById('fileCount');
    var btnClearAll = document.getElementById('btnClearAll');
    var btnUploadBulk = document.getElementById('btnUploadBulk');
    var uploadProgressCard = document.getElementById('uploadProgressCard');
    var overallProgress = document.getElementById('overallProgress');
    var uploadStatus = document.getElementById('uploadStatus');
    var resultsCard = document.getElementById('resultsCard');
    var resultsSummary = document.getElementById('resultsSummary');
    var resultsDetails = document.getElementById('resultsDetails');
    var pageError = document.getElementById('pageError');
    var pageSuccess = document.getElementById('pageSuccess');
  
    // State
    var selectedFiles = []; // Array of { file, preview, imageType, eyeSide, uploadedUrl, status }
    var isUploading = false;
  
    function showError(msg) {
      if (!pageError) return;
      pageError.textContent = msg || '';
      pageError.classList.toggle('d-none', !msg);
      if (pageSuccess) pageSuccess.classList.add('d-none');
    }
  
    function showSuccess(msg) {
      if (!pageSuccess) return;
      pageSuccess.textContent = msg || '';
      pageSuccess.classList.toggle('d-none', !msg);
      if (pageError) pageError.classList.add('d-none');
    }
  
    function hideMessages() {
      if (pageError) pageError.classList.add('d-none');
      if (pageSuccess) pageSuccess.classList.add('d-none');
    }
  
    // Load patients list
    function loadPatients() {
      if (!accountId) {
        showError('Không tìm thấy tài khoản.');
        return Promise.reject(new Error('No account'));
      }
  
      // For Doctor: get patients from getDoctorPatients
      // For Admin/ClinicManager: use searchPatients or getAssignedPatients
      var doctorId = user.doctor_id;
      if (userRole === 'Doctor' && doctorId) {
        return window.AuraAPI.getDoctorPatients(doctorId)
          .then(function (data) {
            var list = Array.isArray(data && data.patients) ? data.patients : [];
            patientSelect.innerHTML = '<option value="">-- Chọn bệnh nhân --</option>';
            list.forEach(function (p) {
              var id = p.patient_id || p.id;
              var name = p.patient_name || p.full_name || 'Bệnh nhân #' + id;
              patientSelect.appendChild(new Option(name, id));
            });
            if (list.length === 0) {
              patientSelect.innerHTML = '<option value="">-- Chưa có bệnh nhân --</option>';
            }
          })
          .catch(function (err) {
            showError('Không tải được danh sách bệnh nhân: ' + (err.message || 'Lỗi không xác định'));
            patientSelect.innerHTML = '<option value="">-- Lỗi tải danh sách --</option>';
          });
      } else if (clinicId) {
        // Admin or ClinicManager: get assigned patients
        return window.AuraAPI.getAssignedPatients(clinicId)
          .then(function (data) {
            // Parse response: API returns { clinic_id, count, patients: [...] }
            var list = Array.isArray(data && data.patients) ? data.patients : 
                       (Array.isArray(data) ? data : []);
            patientSelect.innerHTML = '<option value="">-- Chọn bệnh nhân --</option>';
            list.forEach(function (p) {
              var id = p.patient_id || p.id;
              var name = p.patient_name || p.full_name || 'Bệnh nhân #' + id;
              patientSelect.appendChild(new Option(name, id));
            });
            if (list.length === 0) {
              patientSelect.innerHTML = '<option value="">-- Chưa có bệnh nhân trong phòng khám --</option>';
            }
          })
          .catch(function (err) {
            console.error('Error loading patients:', err);
            showError('Không tải được danh sách bệnh nhân: ' + (err.message || 'Lỗi không xác định'));
            patientSelect.innerHTML = '<option value="">-- Lỗi tải danh sách --</option>';
          });
      } else {
        showError('Không tìm thấy thông tin phòng khám hoặc bác sĩ.');
        return Promise.reject(new Error('No clinic or doctor'));
      }
    }
  
    // Load clinics list
    function loadClinics() {
      if (clinicId) {
        // If user has clinic_id, set it directly
        // Try to get clinic name if available
        window.AuraAPI.getClinic(clinicId)
          .then(function (clinic) {
            var clinicName = (clinic && clinic.name) ? clinic.name : ('Phòng khám #' + clinicId);
            clinicSelect.innerHTML = '<option value="' + clinicId + '">' + clinicName + '</option>';
            clinicSelect.value = clinicId.toString();
            clinicSelect.disabled = true;
          })
          .catch(function (err) {
            console.warn('Could not load clinic details:', err);
            // Fallback: just use clinic ID
            clinicSelect.innerHTML = '<option value="' + clinicId + '">Phòng khám #' + clinicId + '</option>';
            clinicSelect.value = clinicId.toString();
            clinicSelect.disabled = true;
          });
      } else {
        // For Admin: could load all clinics, but for now just use default
        clinicSelect.innerHTML = '<option value="1">Phòng khám mặc định</option>';
        clinicSelect.value = '1';
      }
    }
  
    // Read file as data URL for preview
    function readFileAsDataUrl(file) {
      return new Promise(function (resolve, reject) {
        var reader = new FileReader();
        reader.onload = function () { resolve(reader.result); };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    }
  
    // Add file to list
    function addFile(file) {
      if (!file || !file.type.match(/^image\//)) {
        showError('File không phải là ảnh: ' + (file ? file.name : 'unknown'));
        return;
      }
  
      if (file.size > 5 * 1024 * 1024) {
        showError('File quá lớn (tối đa 5MB): ' + file.name);
        return;
      }
  
      var fileItem = {
        file: file,
        preview: null,
        imageType: globalImageType ? globalImageType.value : 'fundus',
        eyeSide: globalEyeSide ? globalEyeSide.value : 'left',
        uploadedUrl: null,
        status: 'pending' // pending, uploading, success, error
      };
  
      selectedFiles.push(fileItem);
  
      readFileAsDataUrl(file).then(function (dataUrl) {
        fileItem.preview = dataUrl;
        renderFilesList();
        updateFileCount();
        checkUploadButton();
      }).catch(function () {
        showError('Không đọc được file: ' + file.name);
      });
    }
  
    // Remove file from list
    function removeFile(index) {
      if (index >= 0 && index < selectedFiles.length) {
        selectedFiles.splice(index, 1);
        renderFilesList();
        updateFileCount();
        checkUploadButton();
      }
    }
  
    // Render files list
    function renderFilesList() {
      if (!filesList) return;
      filesList.innerHTML = '';
  
      selectedFiles.forEach(function (item, index) {
        var div = document.createElement('div');
        div.className = 'file-item ' + item.status;
        div.innerHTML = '<div class="d-flex align-items-center">' +
          '<div class="me-3">' +
          (item.preview ? '<img src="' + item.preview + '" class="file-preview" alt="Preview">' : '<div class="file-preview bg-light d-flex align-items-center justify-content-center"><i class="bi bi-image"></i></div>') +
          '</div>' +
          '<div class="flex-grow-1">' +
          '<div class="fw-bold">' + item.file.name + '</div>' +
          '<div class="small text-muted">' + formatFileSize(item.file.size) + '</div>' +
          '<div class="row g-2 mt-2">' +
          '<div class="col-md-6">' +
          '<label class="form-label small mb-0">Loại ảnh</label>' +
          '<select class="form-select form-select-sm file-image-type" data-index="' + index + '">' +
          '<option value="fundus"' + (item.imageType === 'fundus' ? ' selected' : '') + '>Fundus</option>' +
          '<option value="oct"' + (item.imageType === 'oct' ? ' selected' : '') + '>OCT</option>' +
          '<option value="fluorescein"' + (item.imageType === 'fluorescein' ? ' selected' : '') + '>Fluorescein</option>' +
          '</select>' +
          '</div>' +
          '<div class="col-md-6">' +
          '<label class="form-label small mb-0">Bên mắt</label>' +
          '<select class="form-select form-select-sm file-eye-side" data-index="' + index + '">' +
          '<option value="left"' + (item.eyeSide === 'left' ? ' selected' : '') + '>Trái</option>' +
          '<option value="right"' + (item.eyeSide === 'right' ? ' selected' : '') + '>Phải</option>' +
          '<option value="both"' + (item.eyeSide === 'both' ? ' selected' : '') + '>Cả hai</option>' +
          '</select>' +
          '</div>' +
          '</div>' +
          '</div>' +
          '<div class="ms-2">' +
          '<button type="button" class="btn btn-sm btn-outline-danger" data-index="' + index + '" onclick="window.bulkUploadPage.removeFile(' + index + ')"><i class="bi bi-x"></i></button>' +
          '</div>' +
          '</div>';
        filesList.appendChild(div);
      });
  
      // Attach event listeners
      filesList.querySelectorAll('.file-image-type').forEach(function (select) {
        select.addEventListener('change', function () {
          var idx = parseInt(this.getAttribute('data-index'));
          if (idx >= 0 && idx < selectedFiles.length) {
            selectedFiles[idx].imageType = this.value;
          }
        });
      });
  
      filesList.querySelectorAll('.file-eye-side').forEach(function (select) {
        select.addEventListener('change', function () {
          var idx = parseInt(this.getAttribute('data-index'));
          if (idx >= 0 && idx < selectedFiles.length) {
            selectedFiles[idx].eyeSide = this.value;
          }
        });
      });
    }
  
    // Format file size
    function formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
  
    // Update file count
    function updateFileCount() {
      if (fileCount) fileCount.textContent = selectedFiles.length;
    }
  
    // Check if upload button should be enabled
    function checkUploadButton() {
      if (!btnUploadBulk) return;
      var patientId = patientSelect ? patientSelect.value : '';
      var clinicIdVal = clinicSelect ? clinicSelect.value : '';
      var hasFiles = selectedFiles.length > 0;
      var isValid = patientId && clinicIdVal && hasFiles && !isUploading;
      btnUploadBulk.disabled = !isValid;
    }
  
    // Apply global settings to all files
    if (btnApplyGlobal) {
      btnApplyGlobal.addEventListener('click', function () {
        var imageType = globalImageType ? globalImageType.value : 'fundus';
        var eyeSide = globalEyeSide ? globalEyeSide.value : 'left';
        selectedFiles.forEach(function (item) {
          item.imageType = imageType;
          item.eyeSide = eyeSide;
        });
        renderFilesList();
        if (window.AuraAlert && window.AuraAlert.toast) {
          window.AuraAlert.toast('Đã áp dụng cài đặt cho tất cả ảnh.', 'success');
        }
      });
    }
  
    // File input change
    if (fileInput) {
      fileInput.addEventListener('change', function () {
        var files = Array.from(this.files || []);
        files.forEach(addFile);
        this.value = ''; // Reset input
      });
    }
  
    // Select files button
    if (btnSelectFiles) {
      btnSelectFiles.addEventListener('click', function () {
        if (fileInput) fileInput.click();
      });
    }
  
    // Drop zone
    if (dropZone) {
      dropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        dropZone.classList.add('drop-zone-active');
      });
      dropZone.addEventListener('dragleave', function () {
        dropZone.classList.remove('drop-zone-active');
      });
      dropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        dropZone.classList.remove('drop-zone-active');
        var files = Array.from(e.dataTransfer.files || []);
        files.forEach(addFile);
      });
      dropZone.addEventListener('click', function () {
        if (fileInput) fileInput.click();
      });
    }
  
    // Clear all
    if (btnClearAll) {
      btnClearAll.addEventListener('click', function () {
        if (isUploading) {
          showError('Đang upload, không thể xóa.');
          return;
        }
        selectedFiles = [];
        renderFilesList();
        updateFileCount();
        checkUploadButton();
        hideMessages();
        if (resultsCard) resultsCard.classList.add('d-none');
      });
    }
  
    // Patient/Clinic select change
    if (patientSelect) {
      patientSelect.addEventListener('change', checkUploadButton);
    }
    if (clinicSelect) {
      clinicSelect.addEventListener('change', checkUploadButton);
    }
  
    // Upload bulk
    if (btnUploadBulk) {
      btnUploadBulk.addEventListener('click', function () {
        if (isUploading) return;
        if (!patientSelect || !patientSelect.value) {
          showError('Vui lòng chọn bệnh nhân.');
          return;
        }
        if (!clinicSelect || !clinicSelect.value) {
          showError('Vui lòng chọn phòng khám.');
          return;
        }
        if (selectedFiles.length === 0) {
          showError('Vui lòng chọn ít nhất một ảnh.');
          return;
        }
  
        hideMessages();
        isUploading = true;
        btnUploadBulk.disabled = true;
        if (uploadProgressCard) uploadProgressCard.classList.remove('d-none');
        if (resultsCard) resultsCard.classList.add('d-none');
  
        var patientId = parseInt(patientSelect.value);
        var clinicIdVal = parseInt(clinicSelect.value);
        var totalFiles = selectedFiles.length;
        var uploadedCount = 0;
        var failedCount = 0;
        var uploadPromises = [];
  
        // Update status
        selectedFiles.forEach(function (item) {
          item.status = 'uploading';
        });
        renderFilesList();
  
        // Upload files sequentially (to avoid overwhelming server)
        function uploadNext(index) {
          if (index >= selectedFiles.length) {
            // All files uploaded, now create bulk records
            createBulkRecords();
            return;
          }
  
          var item = selectedFiles[index];
          var progress = ((index / totalFiles) * 50).toFixed(0); // 50% for file uploads
          if (overallProgress) overallProgress.style.width = progress + '%';
          if (overallProgress) overallProgress.textContent = progress + '%';
          if (uploadStatus) uploadStatus.textContent = 'Đang upload file ' + (index + 1) + '/' + totalFiles + ': ' + item.file.name;
  
          window.AuraAPI.uploadFile(item.file, 'retinal')
            .then(function (uploaded) {
              var imageUrl = (uploaded && (uploaded.full_url || uploaded.url)) || null;
              if (!imageUrl) {
                throw new Error('Upload file thành công nhưng không nhận được URL.');
              }
              item.uploadedUrl = imageUrl;
              item.status = 'success';
              uploadedCount++;
              renderFilesList();
              uploadNext(index + 1);
            })
            .catch(function (err) {
              item.status = 'error';
              item.error = err.message || 'Upload thất bại';
              failedCount++;
              renderFilesList();
              uploadNext(index + 1);
            });
        }
  
        function createBulkRecords() {
          // Filter successful uploads
          var successfulItems = selectedFiles.filter(function (item) {
            return item.status === 'success' && item.uploadedUrl;
          });
  
          if (successfulItems.length === 0) {
            finishUpload(0, failedCount);
            return;
          }
  
          if (overallProgress) overallProgress.style.width = '60%';
          if (overallProgress) overallProgress.textContent = '60%';
          if (uploadStatus) uploadStatus.textContent = 'Đang tạo bản ghi...';
  
          // Prepare bulk payload
          var images = successfulItems.map(function (item) {
            return {
              patient_id: patientId,
              clinic_id: clinicIdVal,
              uploaded_by: accountId,
              image_type: item.imageType,
              eye_side: item.eyeSide,
              image_url: item.uploadedUrl
            };
          });
  
          window.AuraAPI.uploadBulkImages({ images: images })
            .then(function (result) {
              if (overallProgress) overallProgress.style.width = '100%';
              if (overallProgress) overallProgress.textContent = '100%';
              if (uploadStatus) uploadStatus.textContent = 'Hoàn thành!';
  
              var successCount = result.success_count || successfulItems.length;
              var errorCount = result.error_count || 0;
              var batchId = result.batch_id || '';
  
              finishUpload(successCount, errorCount + failedCount, batchId, result);
            })
            .catch(function (err) {
              finishUpload(0, failedCount + successfulItems.length, null, null, err.message);
            });
        }
  
        function finishUpload(success, failed, batchId, result, errorMsg) {
          isUploading = false;
          btnUploadBulk.disabled = false;
          checkUploadButton();
  
          if (uploadProgressCard) uploadProgressCard.classList.add('d-none');
  
          if (resultsCard) resultsCard.classList.remove('d-none');
  
          var summaryHtml = '<div class="alert alert-info">' +
            '<h6><i class="bi bi-info-circle me-1"></i>Kết quả upload</h6>' +
            '<p class="mb-0">Thành công: <strong>' + success + '</strong> | Thất bại: <strong>' + failed + '</strong></p>';
          if (batchId) summaryHtml += '<p class="mb-0 small">Batch ID: <code>' + batchId + '</code></p>';
          if (result && result.analysis_created) {
            summaryHtml += '<p class="mb-0 small text-success"><i class="bi bi-check-circle me-1"></i>' + result.analysis_created + ' yêu cầu phân tích AI đã được tạo tự động.</p>';
          }
          summaryHtml += '</div>';
  
          if (resultsSummary) resultsSummary.innerHTML = summaryHtml;
  
          if (result && result.errors && result.errors.length > 0) {
            var errorsHtml = '<div class="mt-3"><h6>Chi tiết lỗi:</h6><ul class="list-unstyled">';
            result.errors.forEach(function (err) {
              errorsHtml += '<li class="text-danger small"><i class="bi bi-x-circle me-1"></i>' + (err.image_url || 'Unknown') + ': ' + (err.error || 'Lỗi không xác định') + '</li>';
            });
            errorsHtml += '</ul></div>';
            if (resultsDetails) resultsDetails.innerHTML = errorsHtml;
          } else {
            if (resultsDetails) resultsDetails.innerHTML = '';
          }
  
          if (success > 0) {
            showSuccess('Upload thành công ' + success + ' ảnh.');
            setTimeout(function () {
              // Redirect based on role: ClinicManager -> clinic/patients.html, Doctor -> doctor/patients.html
              if (userRole === 'ClinicManager') {
                window.location.href = '../clinic/patients.html';
              } else {
                window.location.href = 'patients.html';
              }
            }, 3000);
          } else {
            showError(errorMsg || 'Upload thất bại. Vui lòng thử lại.');
          }
        }
  
        // Start upload
        uploadNext(0);
      });
    }
  
    // Expose removeFile for onclick handlers
    window.bulkUploadPage = {
      removeFile: removeFile
    };
  
    // Initialize
    console.log('Bulk upload page initialized:', {
      userRole: userRole,
      accountId: accountId,
      clinicId: clinicId,
      user: user
    });
    
    // Debug: Check if clinicId is available
    if (!clinicId && userRole === 'ClinicManager') {
      console.warn('ClinicManager but no clinic_id found in user object:', user);
      showError('Không tìm thấy thông tin phòng khám. Vui lòng đăng nhập lại.');
    }
    
    loadPatients();
    loadClinics();
    checkUploadButton();
  })();
  