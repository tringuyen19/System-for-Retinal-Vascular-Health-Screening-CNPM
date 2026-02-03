/**
 * AURA - Doctor Create Report
 * Form: patient, analysis, medical_notes, diagnosis, treatment_recommendations -> POST /api/medical-reports
 */
(function () {
  'use strict';

  var user = window.AuraAuth && window.AuraAuth.getUser ? window.AuraAuth.getUser() : null;
  var accountId = user && user.account_id;
  var doctorId = null;

  var pageError = document.getElementById('pageError');
  var pageSuccess = document.getElementById('pageSuccess');
  var reportForm = document.getElementById('reportForm');
  var patientIdSelect = document.getElementById('patientId');
  var analysisIdSelect = document.getElementById('analysisId');
  var medicalNotesInput = document.getElementById('medicalNotes');
  var diagnosisInput = document.getElementById('diagnosis');
  var treatmentRecommendationsInput = document.getElementById('treatmentRecommendations');
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

  /** Chỉ dùng API bệnh nhân đã được bác sĩ duyệt (GET /api/doctors/:id/patients), không dùng searchPatients. */
  function loadPatients() {
    if (!doctorId) {
      showError('Không tìm thấy thông tin bác sĩ.');
      return Promise.reject(new Error('No doctor'));
    }
    return window.AuraAPI.getDoctorPatients(doctorId)
      .then(function (data) {
        var list = Array.isArray(data && data.patients) ? data.patients : [];
        patientIdSelect.innerHTML = '<option value="">-- Chọn bệnh nhân (đã được bác sĩ duyệt) --</option>';
        list.forEach(function (p) {
          var id = p.patient_id || p.id;
          var name = p.patient_name || p.full_name || 'Bệnh nhân #' + id;
          patientIdSelect.appendChild(new Option(name, id));
        });
        if (list.length === 0) {
          patientIdSelect.innerHTML = '<option value="">-- Chưa có bệnh nhân nào được bác sĩ duyệt --</option>';
        }
        var params = new URLSearchParams(window.location.search);
        var prePatient = params.get('patient_id');
        if (prePatient) {
          patientIdSelect.value = prePatient;
          onPatientChange();
        }
      })
      .catch(function (err) {
        showError(err.message || 'Không tải được danh sách bệnh nhân đã duyệt.');
        patientIdSelect.innerHTML = '<option value="">-- Lỗi tải danh sách --</option>';
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
          var label = 'Phân tích ' + id + (a.completed_at ? ' - ' + new Date(a.completed_at).toLocaleDateString('vi-VN') : '');
          analysisIdSelect.appendChild(new Option(label, id));
        });
      })
      .catch(function () {
        analysisIdSelect.innerHTML = '<option value="">Không tải được phân tích</option>';
      });
  }

  function submitForm(e) {
    if (e && e.preventDefault) e.preventDefault();
    showError('');
    showSuccess('');
    var patientId = patientIdSelect.value ? parseInt(patientIdSelect.value, 10) : null;
    var analysisId = analysisIdSelect.value ? parseInt(analysisIdSelect.value, 10) : null;
    var medicalNotes = medicalNotesInput && medicalNotesInput.value ? medicalNotesInput.value.trim() : '';
    var diagnosis = diagnosisInput && diagnosisInput.value ? diagnosisInput.value.trim() : '';
    var treatmentRecommendations = treatmentRecommendationsInput && treatmentRecommendationsInput.value ? treatmentRecommendationsInput.value.trim() : '';
    if (!patientId || !analysisId) {
      showError('Vui lòng chọn bệnh nhân và phân tích.');
      return;
    }
    if (!medicalNotes && !diagnosis && !treatmentRecommendations) {
      showError('Vui lòng nhập ít nhất một trong: ghi chú y khoa, chẩn đoán hoặc khuyến nghị điều trị.');
      return;
    }
    if (!doctorId) {
      showError('Không tìm thấy thông tin bác sĩ.');
      return;
    }
    if (!window.AuraAPI || typeof window.AuraAPI.createMedicalReport !== 'function') {
      showError('Lỗi: API chưa sẵn sàng. Tải lại trang.');
      return;
    }
    btnSubmit.disabled = true;
    window.AuraAPI.createMedicalReport({
      patient_id: patientId,
      analysis_id: analysisId,
      doctor_id: doctorId,
      report_url: '',
      medical_notes: medicalNotes,
      diagnosis: diagnosis,
      treatment_recommendations: treatmentRecommendations
    })
      .then(function () {
        showSuccess('Tạo báo cáo thành công. Bệnh nhân có thể xem và tải PDF tại trang Báo cáo (PDF do hệ thống tạo khi tải).');
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

  if (patientIdSelect) patientIdSelect.addEventListener('change', onPatientChange);
  if (btnSubmit) btnSubmit.addEventListener('click', submitForm);
  if (reportForm) reportForm.addEventListener('submit', function (e) { e.preventDefault(); submitForm(e); });

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;
  loadDoctor(function () {
    loadPatients();
  });
})();
