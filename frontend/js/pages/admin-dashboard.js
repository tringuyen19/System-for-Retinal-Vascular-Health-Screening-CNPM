/**
 * AURA - Admin Dashboard
 * Tổng quan: users, clinics, images, revenue, AI performance
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var pageError = document.getElementById('pageError');
  var statUsers = document.getElementById('statUsers');
  var statClinics = document.getElementById('statClinics');
  var statImages = document.getElementById('statImages');
  var statRevenue = document.getElementById('statRevenue');
  var aiConfidence = document.getElementById('aiConfidence');
  var aiSuccessRate = document.getElementById('aiSuccessRate');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }
  function setEl(el, value) {
    if (el) el.textContent = value != null && value !== '' ? value : '-';
  }

  function load() {
    showError('');
    setEl(statUsers, '...');
    setEl(statClinics, '...');
    setEl(statImages, '...');
    setEl(statRevenue, '...');
    setEl(aiConfidence, '...');
    setEl(aiSuccessRate, '...');

    window.AuraAPI.getAdminDashboard()
      .then(function (d) {
        var users = d.users || {};
        var usage = d.usage || {};
        var revenue = d.revenue || {};
        var ai = d.ai_performance || {};
        setEl(statUsers, (users.total_users != null ? users.total_users : '-'));
        setEl(statClinics, (users.total_clinics != null ? users.total_clinics : '-'));
        var imgText = (usage.total_images != null && usage.total_analyses != null)
          ? usage.total_images + ' / ' + usage.total_analyses
          : (usage.total_images != null ? usage.total_images : (usage.total_analyses != null ? usage.total_analyses : '-'));
        setEl(statImages, imgText);
        var rev = revenue.total_revenue;
        setEl(statRevenue, rev != null ? (typeof rev === 'number' ? rev.toLocaleString('vi-VN') : rev) : '-');
        setEl(aiConfidence, ai.average_confidence != null ? (Number(ai.average_confidence) * 100).toFixed(1) + '%' : '-');
        setEl(aiSuccessRate, usage.success_rate != null ? (Number(usage.success_rate) * 100).toFixed(1) + '%' : '-');
      })
      .catch(function (err) {
        showError(err.message || 'Tải dashboard thất bại.');
        setEl(statUsers, '-');
        setEl(statClinics, '-');
        setEl(statImages, '-');
        setEl(statRevenue, '-');
        setEl(aiConfidence, '-');
        setEl(aiSuccessRate, '-');
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();