/**
 * AURA - Doctor Patients list
 * Search patients (name, risk_level), table, view detail modal
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;

  var pageError = document.getElementById('pageError');
  var patientsLoading = document.getElementById('patientsLoading');
  var patientsContent = document.getElementById('patientsContent');
  var patientsEmpty = document.getElementById('patientsEmpty');
  var patientsBody = document.getElementById('patientsBody');
  var patientsSummary = document.getElementById('patientsSummary');
  var searchForm = document.getElementById('searchForm');
  var btnReset = document.getElementById('btnReset');
  var patientDetailModal = document.getElementById('patientDetailModal');
  var patientDetailBody = document.getElementById('patientDetailBody');
  var linkCreateReport = document.getElementById('linkCreateReport');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function riskLabel(level) {
    var map = { low: 'Thấp', medium: 'Trung bình', high: 'Cao', critical: 'Nghiêm trọng' };
    return map[level] || level || '-';
  }

  function doSearch() {
    var name = document.getElementById('searchName').value.trim();
    var riskLevel = document.getElementById('searchRisk').value;
    showError('');
    patientsLoading.classList.remove('d-none');
    patientsContent.classList.add('d-none');
    patientsEmpty.classList.add('d-none');

    var params = {};
    if (name) params.name = name;
    if (riskLevel) params.risk_level = riskLevel;

    window.AuraAPI.searchPatients(params)
      .then(function (data) {
        patientsLoading.classList.add('d-none');
        var list = (data && data.patients) || [];
        var count = (data && data.count != null) ? data.count : list.length;
        if (!list.length) {
          patientsEmpty.classList.remove('d-none');
          patientsSummary.textContent = 'Không có bệnh nhân nào phù hợp.';
          return;
        }
        patientsContent.classList.remove('d-none');
        patientsEmpty.classList.add('d-none');
        patientsSummary.textContent = 'Tổng: ' + count + ' bệnh nhân.';
        var html = '';
        list.forEach(function (p) {
          var dob = (p.date_of_birth) ? new Date(p.date_of_birth).toLocaleDateString('vi-VN') : '-';
          var gender = (p.gender === 'M' || p.gender === 'male') ? 'Nam' : ((p.gender === 'F' || p.gender === 'female') ? 'Nữ' : '-');
          html += '<tr>' +
            '<td>' + (p.patient_id || p.id || '-') + '</td>' +
            '<td>' + (p.patient_name || p.full_name || '-') + '</td>' +
            '<td>' + dob + '</td>' +
            '<td>' + gender + '</td>' +
            '<td><span class="badge bg-' + (p.risk_level === 'high' || p.risk_level === 'critical' ? 'danger' : p.risk_level === 'medium' ? 'warning' : 'secondary') + '">' + riskLabel(p.risk_level) + '</span></td>' +
            '<td><button type="button" class="btn btn-sm btn-outline-primary view-patient" data-id="' + (p.patient_id || p.id) + '">Xem</button></td>' +
            '</tr>';
        });
        patientsBody.innerHTML = html;
        patientsBody.querySelectorAll('.view-patient').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var id = btn.getAttribute('data-id');
            if (id) openPatientDetail(parseInt(id, 10));
          });
        });
      })
      .catch(function (err) {
        patientsLoading.classList.add('d-none');
        patientsContent.classList.add('d-none');
        patientsEmpty.classList.remove('d-none');
        patientsEmpty.textContent = err.message || 'Tải danh sách thất bại.';
        showError(err.message || 'Tải danh sách thất bại.');
      });
  }

  function openPatientDetail(patientId) {
    if (!patientId) return;
    patientDetailBody.innerHTML = 'Đang tải...';
    linkCreateReport.setAttribute('href', 'create-report.html?patient_id=' + patientId);
    var modal = bootstrap.Modal.getOrCreateInstance(patientDetailModal);
    modal.show();
    window.AuraAPI.getPatient(patientId)
      .then(function (p) {
        var dob = (p.date_of_birth) ? new Date(p.date_of_birth).toLocaleDateString('vi-VN') : '-';
        var gender = (p.gender === 'M' || p.gender === 'male') ? 'Nam' : ((p.gender === 'F' || p.gender === 'female') ? 'Nữ' : '-');
        patientDetailBody.innerHTML =
          '<table class="table table-sm">' +
          '<tr><th class="text-muted" style="width:140px">ID</th><td>' + (p.patient_id || p.id) + '</td></tr>' +
          '<tr><th class="text-muted">Họ tên</th><td>' + (p.patient_name || p.full_name || '-') + '</td></tr>' +
          '<tr><th class="text-muted">Ngày sinh</th><td>' + dob + '</td></tr>' +
          '<tr><th class="text-muted">Giới tính</th><td>' + gender + '</td></tr>' +
          '<tr><th class="text-muted">Mức rủi ro</th><td>' + riskLabel(p.risk_level) + '</td></tr>' +
          '<tr><th class="text-muted">Tiền sử bệnh</th><td>' + (p.medical_history || '-') + '</td></tr>' +
          '</table>';
      })
      .catch(function (err) {
        patientDetailBody.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được thông tin.') + '</p>';
      });
  }

  if (searchForm) {
    searchForm.addEventListener('submit', function (e) {
      e.preventDefault();
      doSearch();
    });
  }
  if (btnReset) {
    btnReset.addEventListener('click', function () {
      document.getElementById('searchName').value = '';
      document.getElementById('searchRisk').value = '';
      doSearch();
    });
  }

  function init() {
    doSearch();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
