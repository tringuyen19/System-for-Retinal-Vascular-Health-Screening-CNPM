/**
 * AURA - Patient Dashboard
 * Stats (images, analyses, reports), recent activities, quick actions
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Patient')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var patientId = null;

  var statImages = document.getElementById('statImages');
  var statAnalyses = document.getElementById('statAnalyses');
  var statReports = document.getElementById('statReports');
  var recentList = document.getElementById('recentList');
  var dashboardError = document.getElementById('dashboardError');

  function showError(msg) {
    if (!dashboardError) return;
    dashboardError.textContent = msg || '';
    dashboardError.classList.toggle('d-none', !msg);
  }

  function setStat(el, value) {
    if (el) el.textContent = value != null ? value : '-';
  }

  /** Định dạng thời gian: hh:mm yy-mm-dd */
  function formatDateTime(str) {
    if (!str) return '-';
    var d = new Date(str);
    if (isNaN(d.getTime())) return str;
    var h = d.getHours();
    var m = d.getMinutes();
    var yy = String(d.getFullYear()).slice(-2);
    var mm = String(d.getMonth() + 1).padStart(2, '0');
    var dd = String(d.getDate()).padStart(2, '0');
    var hh = String(h).padStart(2, '0');
    var min = String(m).padStart(2, '0');
    return hh + ':' + min + ' ' + yy + '-' + mm + '-' + dd;
  }

  function renderRecent(images, reports) {
    var items = [];
    if (images && images.length) {
      images.slice(0, 5).forEach(function (img) {
        var timeStr = formatDateTime(img.upload_time || img.created_at);
        items.push({ text: 'Ảnh ' + (img.image_id || img.id) + ' - ' + (img.image_type || '') + ' (' + timeStr + ')', url: 'my-images.html' });
      });
    }
    if (reports && reports.reports && reports.reports.length) {
      reports.reports.slice(0, 3).forEach(function (r) {
        var timeStr = formatDateTime(r.created_at);
        items.push({ text: 'Báo cáo ' + (r.report_id || r.id) + ' (' + timeStr + ')', url: 'reports.html' });
      });
    }
    if (!items.length) {
      recentList.innerHTML = '<p class="text-muted mb-0">Chưa có hoạt động. <a href="upload-image.html">Upload ảnh</a> để bắt đầu.</p>';
      return;
    }
    recentList.innerHTML = '<ul class="list-group list-group-flush">' + items.map(function (i) {
      return '<li class="list-group-item d-flex justify-content-between align-items-center">' +
        '<span>' + (i.text || '') + '</span>' +
        (i.url ? '<a href="' + i.url + '" class="btn btn-sm btn-outline-primary">Xem</a>' : '') + '</li>';
    }).join('') + '</ul>';
  }

  function load() {
    if (!accountId) { showError('Không tìm thấy thông tin tài khoản.'); return; }
    showError('');
    recentList.innerHTML = 'Đang tải...';

    window.AuraAPI.getPatientByAccount(accountId)
      .then(function (patient) {
        if (!patient || !patient.patient_id) {
          // Chưa có profile, redirect đến trang setup
          window.location.href = 'setup-profile.html';
          return;
        }
        patientId = patient.patient_id;
        return Promise.all([
          window.AuraAPI.getImagesByPatient(patientId),
          window.AuraAPI.getReportsByPatient(patientId, 10)
        ]);
      })
      .then(function (data) {
        if (!data) return;
        var imagesData = data[0];
        var reportsData = data[1];
        var images = (imagesData && imagesData.images) || [];
        var reports = (reportsData && reportsData.reports) || [];
        var totalImages = (imagesData && imagesData.count) != null ? imagesData.count : images.length;
        setStat(statImages, totalImages);
        setStat(statAnalyses, totalImages);
        setStat(statReports, reports.length);
        renderRecent(images, { reports: reports });
      })
      .catch(function (err) {
        showError(err.message || 'Tải dữ liệu thất bại.');
        setStat(statImages, '-');
        setStat(statAnalyses, '-');
        setStat(statReports, '-');
        recentList.innerHTML = '<p class="text-muted mb-0">Không tải được dữ liệu.</p>';
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
