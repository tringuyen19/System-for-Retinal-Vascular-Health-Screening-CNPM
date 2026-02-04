/**
 * AURA - Doctor Patients list
 * Search patients (name, risk_level), table, view detail modal
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
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
  var myPatientsLoading = document.getElementById('myPatientsLoading');
  var myPatientsContent = document.getElementById('myPatientsContent');
  var myPatientsEmpty = document.getElementById('myPatientsEmpty');
  var myPatientsCount = document.getElementById('myPatientsCount');
  var myPatientsBody = document.getElementById('myPatientsBody');

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
    var patientIdEl = document.getElementById('searchPatientId');
    var patientId = patientIdEl ? patientIdEl.value.trim() : '';
    var name = document.getElementById('searchName').value.trim();
    var riskLevel = document.getElementById('searchRisk').value;
    showError('');
    patientsLoading.classList.remove('d-none');
    patientsContent.classList.add('d-none');
    patientsEmpty.classList.add('d-none');

    var params = {};
    var pidNum = patientId ? parseInt(patientId, 10) : NaN;
    if (!isNaN(pidNum) && pidNum > 0) params.patient_id = pidNum;
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
            '<td>' +
              '<button type="button" class="btn btn-sm btn-outline-primary view-patient me-1" data-id="' + (p.patient_id || p.id) + '">Xem</button>' +
              '<a class="btn btn-sm btn-outline-secondary" href="patient-history.html?patient_id=' + (p.patient_id || p.id) + '"><i class="bi bi-activity me-1"></i>Lịch sử & xu hướng</a>' +
            '</td>' +
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
    Promise.all([
      window.AuraAPI.getPatient(patientId),
      window.AuraAPI.getImagesByPatient(patientId).catch(function () { return { images: [] }; })
    ])
      .then(function (arr) {
        var p = arr[0];
        var imagesData = arr[1];
        var images = (imagesData && imagesData.images) || [];
        var dob = (p.date_of_birth) ? new Date(p.date_of_birth).toLocaleDateString('vi-VN') : '-';
        var gender = (p.gender === 'M' || p.gender === 'male') ? 'Nam' : ((p.gender === 'F' || p.gender === 'female') ? 'Nữ' : '-');
        var infoHtml =
          '<table class="table table-sm">' +
          '<tr><th class="text-muted" style="width:140px">ID</th><td>' + (p.patient_id || p.id) + '</td></tr>' +
          '<tr><th class="text-muted">Họ tên</th><td>' + (p.patient_name || p.full_name || '-') + '</td></tr>' +
          '<tr><th class="text-muted">Ngày sinh</th><td>' + dob + '</td></tr>' +
          '<tr><th class="text-muted">Giới tính</th><td>' + gender + '</td></tr>' +
          '<tr><th class="text-muted">Mức rủi ro</th><td>' + riskLabel(p.risk_level) + '</td></tr>' +
          '<tr><th class="text-muted">Tiền sử bệnh</th><td>' + (p.medical_history || '-') + '</td></tr>' +
          '</table>';
        var imagesHtml = '';
        if (images.length) {
          imagesHtml = '<div class="mt-3 pt-3 border-top"><h6 class="text-muted mb-2"><i class="bi bi-images me-1"></i>Ảnh bệnh nhân đã tải (' + images.length + ')</h6>' +
            '<div class="row g-2">';
          images.forEach(function (img) {
            var url = (img.image_url || img.full_url || '').trim();
            var label = (img.image_type || 'fundus') + ' - ' + (img.eye_side || '');
            var uploadDate = img.upload_time ? (typeof img.upload_time === 'string' ? img.upload_time.slice(0, 10) : img.upload_time) : '';
            if (!url) return;
            imagesHtml += '<div class="col-6 col-md-4">' +
              '<div class="card border shadow-sm">' +
              '<a href="' + url + '" target="_blank" rel="noopener" class="text-decoration-none">' +
              '<img src="' + url + '" alt="Ảnh" class="card-img-top" style="height:100px;object-fit:cover;" onerror="this.style.background=\'#eee\';this.alt=\'Không tải được ảnh\';">' +
              '</a>' +
              '<div class="card-body py-2 px-2">' +
              '<div class="small text-muted">' + label + (uploadDate ? ' • ' + uploadDate : '') + '</div>' +
              '<a href="' + url + '" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary mt-1">Xem ảnh</a>' +
              '</div></div></div>';
          });
          imagesHtml += '</div></div>';
        } else {
          imagesHtml = '<div class="mt-3 pt-3 border-top"><p class="text-muted small mb-0"><i class="bi bi-images me-1"></i>Chưa có ảnh nào được tải lên.</p></div>';
        }
        patientDetailBody.innerHTML = infoHtml + imagesHtml;
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
      var pid = document.getElementById('searchPatientId');
      if (pid) pid.value = '';
      document.getElementById('searchName').value = '';
      document.getElementById('searchRisk').value = '';
      doSearch();
    });
  }

  function loadMyPatients() {
    if (!accountId || !myPatientsLoading) return;
    myPatientsLoading.classList.remove('d-none');
    if (myPatientsContent) myPatientsContent.classList.add('d-none');
    if (myPatientsEmpty) myPatientsEmpty.classList.add('d-none');
    window.AuraAPI.getDoctorByAccount(accountId)
      .then(function (doctor) {
        if (!doctor || !doctor.doctor_id) {
          if (myPatientsLoading) myPatientsLoading.classList.add('d-none');
          if (myPatientsEmpty) { myPatientsEmpty.classList.remove('d-none'); myPatientsEmpty.textContent = 'Bạn chưa có hồ sơ bác sĩ.'; }
          return null;
        }
        return window.AuraAPI.getDoctorPatients(doctor.doctor_id);
      })
      .then(function (data) {
        if (!myPatientsLoading) return;
        myPatientsLoading.classList.add('d-none');
        if (!data) return;
        var list = (data.patients) || [];
        var count = (data.count != null) ? data.count : list.length;
        if (!list.length) {
          if (myPatientsEmpty) { myPatientsEmpty.classList.remove('d-none'); myPatientsEmpty.textContent = 'Bạn chưa duyệt kết quả AI của bệnh nhân nào.'; }
          return;
        }
        if (myPatientsEmpty) myPatientsEmpty.classList.add('d-none');
        if (myPatientsContent) myPatientsContent.classList.remove('d-none');
        if (myPatientsCount) myPatientsCount.textContent = count;
        if (!myPatientsBody) return;
        var html = '';
        list.forEach(function (p) {
          html += '<tr><td>' + (p.patient_id || '-') + '</td><td>' + (p.patient_name || '-') + '</td>' +
            '<td>' +
              '<button type="button" class="btn btn-sm btn-outline-primary view-patient me-1" data-id="' + (p.patient_id || '') + '">Xem</button>' +
              '<a class="btn btn-sm btn-outline-secondary" href="patient-history.html?patient_id=' + (p.patient_id || '') + '"><i class="bi bi-activity me-1"></i>Lịch sử & xu hướng</a>' +
            '</td></tr>';
        });
        myPatientsBody.innerHTML = html;
        myPatientsBody.querySelectorAll('.view-patient').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var id = btn.getAttribute('data-id');
            if (id) openPatientDetail(parseInt(id, 10));
          });
        });
      })
      .catch(function (err) {
        if (myPatientsLoading) myPatientsLoading.classList.add('d-none');
        if (myPatientsEmpty) {
          myPatientsEmpty.classList.remove('d-none');
          myPatientsEmpty.textContent = (err && err.message) ? err.message : 'Không tải được danh sách.';
        }
      });
  }

  function init() {
    loadMyPatients();
    doSearch();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
