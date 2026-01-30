/**
 * AURA - Clinic Patients
 * GET /api/patients/assigned/clinic/:id
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var loading = document.getElementById('loading');
  var content = document.getElementById('content');
  var tbody = document.getElementById('tbody');
  var summary = document.getElementById('summary');
  var empty = document.getElementById('empty');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }
  function riskLabel(level) {
    var map = { low: 'Thấp', medium: 'Trung bình', high: 'Cao', critical: 'Nghiêm trọng' };
    return map[level] || level || '-';
  }

  function load() {
    if (!clinicId) { showError('Bạn chưa được gán phòng khám.'); return; }
    showError('');
    loading.classList.remove('d-none');
    content.classList.add('d-none');
    empty.classList.add('d-none');
    window.AuraAPI.getAssignedPatients(clinicId)
      .then(function (data) {
        loading.classList.add('d-none');
        var list = (data && data.patients) || [];
        var count = (data && data.count != null) ? data.count : list.length;
        if (!list.length) {
          empty.classList.remove('d-none');
          return;
        }
        content.classList.remove('d-none');
        summary.textContent = 'Tổng: ' + count + ' bệnh nhân.';
        var html = '';
        list.forEach(function (p) {
          var dob = p.date_of_birth ? new Date(p.date_of_birth).toLocaleDateString('vi-VN') : '-';
          var gender = (p.gender === 'M' || p.gender === 'male') ? 'Nam' : ((p.gender === 'F' || p.gender === 'female') ? 'Nữ' : '-');
          html += '<tr><td>' + (p.patient_id || p.id || '-') + '</td><td>' + (p.patient_name || p.full_name || '-') + '</td><td>' + dob + '</td><td>' + gender + '</td><td><span class="badge bg-' + (p.risk_level === 'high' || p.risk_level === 'critical' ? 'danger' : p.risk_level === 'medium' ? 'warning' : 'secondary') + '">' + riskLabel(p.risk_level) + '</span></td></tr>';
        });
        tbody.innerHTML = html;
      })
      .catch(function (err) {
        loading.classList.add('d-none');
        empty.classList.remove('d-none');
        empty.textContent = err.message || 'Không tải được danh sách.';
        showError(err.message || 'Tải thất bại.');
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
