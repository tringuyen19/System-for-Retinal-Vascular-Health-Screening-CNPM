/**
 * AURA - Clinic Dashboard
 * Stats: patients, images, reports, alerts; clinic_id from user.clinic_id
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var clinicNameEl = document.getElementById('clinicName');
  var statPatients = document.getElementById('statPatients');
  var statImages = document.getElementById('statImages');
  var statReports = document.getElementById('statReports');
  var statAlerts = document.getElementById('statAlerts');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }
  function setStat(el, value) {
    if (el) el.textContent = value != null ? value : '-';
  }

  function load() {
    if (!clinicId) {
      showError('Bạn chưa được gán phòng khám. Liên hệ quản trị viên.');
      setStat(statPatients, '-');
      setStat(statImages, '-');
      setStat(statReports, '-');
      setStat(statAlerts, '-');
      return;
    }
    showError('');
    if (clinicNameEl) clinicNameEl.textContent = 'Đang tải...';
    Promise.all([
      window.AuraAPI.getClinic(clinicId),
      window.AuraAPI.getClinicMembers(clinicId),
      window.AuraAPI.getClinicUsage(clinicId),
      window.AuraAPI.getClinicReportsSummary(clinicId),
      window.AuraAPI.getHighRiskAlerts(clinicId, 'high')
    ])
      .then(function (results) {
        var clinic = results[0];
        var members = results[1];
        var usage = results[2];
        var reportsSummary = results[3];
        var alertsData = results[4];
        if (clinicNameEl) clinicNameEl.textContent = clinic && clinic.name ? clinic.name : '';
        var totalPatients = (members && (members.total_patients != null ? members.total_patients : (members.patients && members.patients.length))) || 0;
        setStat(statPatients, totalPatients);
        setStat(statImages, (usage && usage.total_images_uploaded) != null ? usage.total_images_uploaded : '-');
        setStat(statReports, (reportsSummary && reportsSummary.total_reports) != null ? reportsSummary.total_reports : '-');
        var alertCount = (alertsData && (alertsData.count != null ? alertsData.count : (alertsData.alerts && alertsData.alerts.length))) || 0;
        setStat(statAlerts, alertCount);
      })
      .catch(function (err) {
        showError(err.message || 'Tải dữ liệu thất bại.');
        if (clinicNameEl) clinicNameEl.textContent = '';
        setStat(statPatients, '-');
        setStat(statImages, '-');
        setStat(statReports, '-');
        setStat(statAlerts, '-');
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
