/**
 * AURA - Patient Upload Image
 * Drag & drop, file input, preview, upload (image_url: data URL hoặc URL từ server)
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireLogin || !window.AuraAuth.requireLogin()) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var patientId = null;
  var selectedFileDataUrl = null;

  var dropZone = document.getElementById('dropZone');
  var fileInput = document.getElementById('fileInput');
  var btnSelectFile = document.getElementById('btnSelectFile');
  var previewWrap = document.getElementById('previewWrap');
  var previewImg = document.getElementById('previewImg');
  var imageType = document.getElementById('imageType');
  var eyeSide = document.getElementById('eyeSide');
  var progressBar = document.getElementById('progressBar');
  var btnUpload = document.getElementById('btnUpload');
  var uploadError = document.getElementById('uploadError');

  function showError(msg) {
    if (!uploadError) return;
    uploadError.textContent = msg || '';
    uploadError.classList.toggle('d-none', !msg);
  }

  function setProgress(pct) {
    if (!progressBar) return;
    progressBar.classList.toggle('d-none', pct == null);
    var bar = progressBar.querySelector('.progress-bar');
    if (bar) bar.style.width = (pct != null ? pct : 0) + '%';
  }

  function loadPatient() {
    if (!accountId) return Promise.reject(new Error('Không tìm thấy tài khoản.'));
    return window.AuraAPI.getPatientByAccount(accountId).then(function (p) {
      if (!p || !p.patient_id) return Promise.reject(new Error('Chưa có hồ sơ bệnh nhân. Vui lòng cập nhật Hồ sơ.'));
      patientId = p.patient_id;
    });
  }

  function readFileAsDataUrl(file) {
    return new Promise(function (resolve, reject) {
      var r = new FileReader();
      r.onload = function () { resolve(r.result); };
      r.onerror = reject;
      r.readAsDataURL(file);
    });
  }

  function onFileSelect(file) {
    if (!file || !file.type.match(/^image\//)) {
      showError('Vui lòng chọn file ảnh (jpg, png, ...).');
      return;
    }
    showError('');
    selectedFileDataUrl = null;
    readFileAsDataUrl(file).then(function (dataUrl) {
      selectedFileDataUrl = dataUrl;
      if (previewImg) previewImg.src = dataUrl;
      if (previewWrap) previewWrap.classList.remove('d-none');
      if (btnUpload) btnUpload.disabled = false;
    }).catch(function () {
      showError('Không đọc được file.');
    });
  }

  if (btnSelectFile) btnSelectFile.addEventListener('click', function () { fileInput && fileInput.click(); });
  if (fileInput) fileInput.addEventListener('change', function () {
    var f = fileInput.files && fileInput.files[0];
    if (f) onFileSelect(f);
  });

  if (dropZone) {
    dropZone.addEventListener('dragover', function (e) { e.preventDefault(); dropZone.classList.add('border-primary'); });
    dropZone.addEventListener('dragleave', function () { dropZone.classList.remove('border-primary'); });
    dropZone.addEventListener('drop', function (e) {
      e.preventDefault();
      dropZone.classList.remove('border-primary');
      var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (f) onFileSelect(f);
    });
    dropZone.addEventListener('click', function () { fileInput && fileInput.click(); });
  }

  if (btnUpload) {
    btnUpload.addEventListener('click', function () {
      if (!selectedFileDataUrl || !patientId) {
        showError('Vui lòng chọn ảnh và đảm bảo đã có hồ sơ bệnh nhân.');
        return;
      }
      showError('');
      btnUpload.disabled = true;
      setProgress(30);
      var payload = {
        patient_id: patientId,
        clinic_id: user.clinic_id || 1,
        uploaded_by: accountId,
        image_type: imageType ? imageType.value : 'fundus',
        eye_side: eyeSide ? eyeSide.value : 'left',
        image_url: selectedFileDataUrl
      };
      window.AuraAPI.uploadImage(payload)
        .then(function () {
          setProgress(100);
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Upload ảnh thành công.', 'success');
          selectedFileDataUrl = null;
          if (previewWrap) previewWrap.classList.add('d-none');
          if (fileInput) fileInput.value = '';
          btnUpload.disabled = true;
          setTimeout(function () { setProgress(null); window.location.href = 'my-images.html'; }, 800);
        })
        .catch(function (err) {
          setProgress(null);
          showError(err.message || 'Upload thất bại.');
          btnUpload.disabled = false;
        });
    });
  }

  loadPatient().catch(function (err) {
    showError(err.message || 'Không tải được hồ sơ bệnh nhân.');
    if (btnUpload) btnUpload.disabled = true;
  });
})();
