/**
 * AURA - Doctor Create Report
 * Form: patient, analysis (by patient), report_url; submit POST /api/medical-reports
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var doctorId = null;

  var pageError = document.getElementById('pageError');
  var pageSuccess = document.getElementById('pageSuccess');
  var reportForm = document.getElementById('reportForm');
  var patientIdSelect = document.getElementById('patientId');
  var analysisIdSelect = document.getElementById('analysisId');
  var reportUrlInput = document.getElementById('reportUrl');
  var btnSubmit = document.getElementById('btnSubmit');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }
  function showSuccess(msg) {
    if (!pageSuccess) return;
    pageSuccess.textContent = msg || '';
    pageSuccess.classList.toggle('d-none', !msg);
  }

  function loadDoctor(cb) {
    if (doctorId) {
      if (cb) cb();
      return Promise.resolve();
    }
    if (!accountId) {
      showError('Không tìm thấy tài khoản.');
      return Promise.reject(new Error('No account'));
    }
    return window.AuraAPI.getDoctorByAccount(accountId)
      .then(function (doctor) {
        if (!doctor || !doctor.doctor_id) {
          showError('Bạn chưa có hồ sơ bác sĩ. Vui lòng cập nhật Hồ sơ.');
          return Promise.reject(new Error('No doctor profile'));
        }
        doctorId = doctor.doctor_id;
        if (cb) cb();
      });
  }

  function loadPatients() {
    return window.AuraAPI.searchPatients({})
      .then(function (data) {
        var list = (data && data.patients) || [];
        patientIdSelect.innerHTML = '<option value="">-- Chọn bệnh nhân --</option>';
        list.forEach(function (p) {
          var id = p.patient_id || p.id;
          var name = p.patient_name || p.full_name || 'Bệnh nhân #' + id;
          patientIdSelect.appendChild(new Option(name, id));
        });
        var params = new URLSearchParams(window.location.search);
        var prePatient = params.get('patient_id');
        if (prePatient) {
          patientIdSelect.value = prePatient;
          onPatientChange();
        }
      })
      .catch(function (err) {
        showError(err.message || 'Không tải được danh sách bệnh nhân.');
      });
  }

  function onPatientChange() {
    var pid = patientIdSelect.value ? parseInt(patientIdSelect.value, 10) : null;
    analysisIdSelect.innerHTML = '<option value="">-- Chọn phân tích --</option>';
    analysisIdSelect.disabled = !pid;
    if (!pid) return;
    window.AuraAPI.getPatientAnalyses(pid, 50, 0)
      .then(function (data) {
        var list = (data && data.analyses) || [];
        analysisIdSelect.innerHTML = '<option value="">-- Chọn phân tích --</option>';
        list.forEach(function (a) {
          var id = a.analysis_id || a.id;
          var label = 'Phân tích #' + id + (a.completed_at ? ' - ' + new Date(a.completed_at).toLocaleDateString('vi-VN') : '');
          analysisIdSelect.appendChild(new Option(label, id));
        });
      })
      .catch(function () {
        analysisIdSelect.innerHTML = '<option value="">Không tải được phân tích</option>';
      });
  }

  function submitForm(e) {
    e.preventDefault();
    showError('');
    showSuccess('');
    var patientId = patientIdSelect.value ? parseInt(patientIdSelect.value, 10) : null;
    var analysisId = analysisIdSelect.value ? parseInt(analysisIdSelect.value, 10) : null;
    var reportUrl = reportUrlInput.value ? reportUrlInput.value.trim() : '';
    if (!patientId || !analysisId || !reportUrl) {
      showError('Vui lòng chọn bệnh nhân, phân tích và nhập đường dẫn báo cáo.');
      return;
    }
    if (!doctorId) {
      showError('Không tìm thấy thông tin bác sĩ.');
      return;
    }
    btnSubmit.disabled = true;
    window.AuraAPI.createMedicalReport({
      patient_id: patientId,
      analysis_id: analysisId,
      doctor_id: doctorId,
      report_url: reportUrl
    })
      .then(function () {
        showSuccess('Tạo báo cáo thành công.');
        if (window.AuraAlert && window.AuraAlert.toast) {
          window.AuraAlert.toast('Tạo báo cáo thành công.', 'success');
        }
        reportForm.reset();
        analysisIdSelect.innerHTML = '<option value="">-- Chọn bệnh nhân trước --</option>';
        analysisIdSelect.disabled = true;
      })
      .catch(function (err) {
        showError(err.message || 'Tạo báo cáo thất bại.');
      })
      .finally(function () {
        btnSubmit.disabled = false;
      });
  }

  patientIdSelect.addEventListener('change', onPatientChange);
  reportForm.addEventListener('submit', submitForm);

  loadDoctor(function () {
    loadPatients();
  });
})();
