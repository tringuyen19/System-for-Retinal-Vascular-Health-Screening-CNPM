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
  var aiActiveModel = document.getElementById('aiActiveModel');
  var aiHighCritical = document.getElementById('aiHighCritical');

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
    setEl(aiActiveModel, '...');
    setEl(aiHighCritical, '...');

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
        if (ai.average_confidence != null) {
          var c = Number(ai.average_confidence);
          setEl(aiConfidence, (c <= 1 && c >= 0 ? (c * 100).toFixed(1) : c.toFixed(1)) + '%');
        } else {
          setEl(aiConfidence, '-');
        }
        if (usage.success_rate != null) {
          var sr = Number(usage.success_rate);
          setEl(aiSuccessRate, (sr <= 1 && sr >= 0 ? (sr * 100).toFixed(1) : sr.toFixed(1)) + '%');
        } else {
          setEl(aiSuccessRate, '-');
        }

        // Active model (if any)
        if (ai.active_model && (ai.active_model.model_name || ai.active_model.version)) {
          var name = ai.active_model.model_name || 'AI';
          var ver = ai.active_model.version ? (' v' + ai.active_model.version) : '';
          setEl(aiActiveModel, name + ver);
        } else {
          setEl(aiActiveModel, '-');
        }

        // High/Critical counts
        var rd = ai.risk_distribution || {};
        var high = Number(rd.high || 0);
        var critical = Number(rd.critical || 0);
        if (!isNaN(high) && !isNaN(critical)) {
          setEl(aiHighCritical, (high + critical).toLocaleString('vi-VN'));
        } else {
          setEl(aiHighCritical, '-');
        }
      })
      .catch(function (err) {
        showError(err.message || 'Tải dashboard thất bại.');
        setEl(statUsers, '-');
        setEl(statClinics, '-');
        setEl(statImages, '-');
        setEl(statRevenue, '-');
        setEl(aiConfidence, '-');
        setEl(aiSuccessRate, '-');
        setEl(aiActiveModel, '-');
        setEl(aiHighCritical, '-');
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
