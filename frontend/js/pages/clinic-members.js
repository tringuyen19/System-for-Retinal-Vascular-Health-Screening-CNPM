/**
 * AURA - Clinic Members
 * GET /api/clinics/:id/members -> doctors, patients
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var doctorsLoading = document.getElementById('doctorsLoading');
  var doctorsList = document.getElementById('doctorsList');
  var doctorCount = document.getElementById('doctorCount');
  var patientsLoading = document.getElementById('patientsLoading');
  var patientsList = document.getElementById('patientsList');
  var patientCount = document.getElementById('patientCount');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function load() {
    if (!clinicId) {
      showError('Bạn chưa được gán phòng khám.');
      return;
    }
    showError('');
    doctorsLoading.classList.remove('d-none');
    patientsLoading.classList.remove('d-none');
    doctorsList.innerHTML = '';
    patientsList.innerHTML = '';
    window.AuraAPI.getClinicMembers(clinicId)
      .then(function (data) {
        doctorsLoading.classList.add('d-none');
        patientsLoading.classList.add('d-none');
        var doctors = (data && data.doctors) || [];
        var patients = (data && data.patients) || [];
        if (doctorCount) doctorCount.textContent = (data && data.total_doctors != null) ? data.total_doctors : doctors.length;
        if (patientCount) patientCount.textContent = (data && data.total_patients != null) ? data.total_patients : patients.length;
        doctors.forEach(function (d) {
          var li = document.createElement('li');
          li.className = 'list-group-item';
          li.textContent = (d.doctor_name || '') + ' - ' + (d.specialization || '') + ' (' + (d.license_number || '') + ')';
          doctorsList.appendChild(li);
        });
        if (!doctors.length) doctorsList.innerHTML = '<li class="list-group-item text-muted">Chưa có bác sĩ.</li>';
        patients.forEach(function (p) {
          var li = document.createElement('li');
          li.className = 'list-group-item';
          li.textContent = (p.patient_name || '') + ' - ' + (p.date_of_birth ? new Date(p.date_of_birth).toLocaleDateString('vi-VN') : '');
          patientsList.appendChild(li);
        });
        if (!patients.length) patientsList.innerHTML = '<li class="list-group-item text-muted">Chưa có bệnh nhân.</li>';
      })
      .catch(function (err) {
        doctorsLoading.classList.add('d-none');
        patientsLoading.classList.add('d-none');
        showError(err.message || 'Không tải được thành viên.');
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
