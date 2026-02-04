/**
 * AURA - Bệnh nhân & Thành viên phòng khám (gộp patients + members)
 * GET /api/clinics/:id/members (bác sĩ), GET /api/patients/assigned/clinic/:id (bệnh nhân đầy đủ)
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var doctorsLoading = document.getElementById('doctorsLoading');
  var doctorsContent = document.getElementById('doctorsContent');
  var doctorsTbody = document.getElementById('doctorsTbody');
  var doctorsEmpty = document.getElementById('doctorsEmpty');
  var doctorCount = document.getElementById('doctorCount');
  var patientsLoading = document.getElementById('patientsLoading');
  var patientsContent = document.getElementById('patientsContent');
  var patientsTbody = document.getElementById('patientsTbody');
  var patientsEmpty = document.getElementById('patientsEmpty');
  var patientCount = document.getElementById('patientCount');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function genderLabel(g) {
    if (g === 'M' || g === 'male') return 'Nam';
    if (g === 'F' || g === 'female') return 'Nữ';
    return g || '-';
  }

  function loadDoctors() {
    if (!clinicId) return;
    doctorsLoading.classList.remove('d-none');
    doctorsContent.classList.add('d-none');
    doctorsEmpty.classList.add('d-none');
    doctorsTbody.innerHTML = '';
    window.AuraAPI.getClinicMembers(clinicId)
      .then(function (data) {
        doctorsLoading.classList.add('d-none');
        var doctors = (data && data.doctors) || [];
        var total = (data && data.total_doctors != null) ? data.total_doctors : doctors.length;
        if (doctorCount) doctorCount.textContent = total;
        if (!doctors.length) {
          doctorsEmpty.classList.remove('d-none');
          return;
        }
        doctorsContent.classList.remove('d-none');
        var html = doctors.map(function (d) {
          return '<tr>' +
            '<td>' + (d.doctor_name || '-') + '</td>' +
            '<td>' + (d.specialization || '-') + '</td>' +
            '<td>' + (d.license_number || '-') + '</td></tr>';
        }).join('');
        doctorsTbody.innerHTML = html;
      })
      .catch(function (err) {
        doctorsLoading.classList.add('d-none');
        doctorsEmpty.classList.remove('d-none');
        if (doctorsEmpty) doctorsEmpty.textContent = err.message || 'Không tải được danh sách bác sĩ.';
      });
  }

  function loadPatients() {
    if (!clinicId) return;
    patientsLoading.classList.remove('d-none');
    patientsContent.classList.add('d-none');
    patientsEmpty.classList.add('d-none');
    patientsTbody.innerHTML = '';
    window.AuraAPI.getAssignedPatients(clinicId)
      .then(function (data) {
        patientsLoading.classList.add('d-none');
        var list = (data && data.patients) || [];
        var total = (data && data.count != null) ? data.count : list.length;
        if (patientCount) patientCount.textContent = total;
        if (!list.length) {
          patientsEmpty.classList.remove('d-none');
          return;
        }
        patientsContent.classList.remove('d-none');
        var html = list.map(function (p) {
          var dob = p.date_of_birth ? new Date(p.date_of_birth).toLocaleDateString('vi-VN') : '-';
          var gender = genderLabel(p.gender);
          var history = (p.medical_history || '').trim();
          if (history.length > 80) history = history.substring(0, 77) + '...';
          return '<tr>' +
            '<td>' + (p.patient_name || '-') + '</td>' +
            '<td>' + dob + '</td>' +
            '<td>' + gender + '</td>' +
            '<td class="small">' + (history || '-') + '</td></tr>';
        }).join('');
        patientsTbody.innerHTML = html;
      })
      .catch(function (err) {
        patientsLoading.classList.add('d-none');
        patientsEmpty.classList.remove('d-none');
        if (patientsEmpty) patientsEmpty.textContent = err.message || 'Không tải được danh sách bệnh nhân.';
      });
  }

  function load() {
    if (!clinicId) {
      showError('Bạn chưa được gán phòng khám.');
      if (doctorsLoading) doctorsLoading.classList.add('d-none');
      if (patientsLoading) patientsLoading.classList.add('d-none');
      return;
    }
    showError('');
    loadDoctors();
    loadPatients();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
