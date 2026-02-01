/**
 * AURA - Admin Settings
 * Cài đặt bảo mật, cấu hình AI, chính sách thông báo
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Admin')) return;

  var pageError = document.getElementById('pageError');
  var btnSavePrivacy = document.getElementById('btnSavePrivacy');
  var btnSaveAiConfig = document.getElementById('btnSaveAiConfig');
  var policiesJson = document.getElementById('policiesJson');

  var privacyIds = [
    'privacyDataRetentionDays',
    'privacyAutoAnonymizeDays',
    'privacyRequireConsentAi',
    'privacyAllowDataSharing',
    'privacyAnonymizePatient',
    'privacyEncryptSensitive',
    'privacyAuditAccess',
    'privacyGdprMode'
  ];
  var aiIds = ['aiThresholdConfig', 'aiRetrainingPolicy'];

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function loadPrivacy() {
    window.AuraAPI.getAdminPrivacySettings()
      .then(function (data) {
        setEl('privacyDataRetentionDays', data.data_retention_days);
        setEl('privacyAutoAnonymizeDays', data.auto_anonymize_after_days);
        setCheck('privacyRequireConsentAi', data.require_consent_for_ai_training);
        setCheck('privacyAllowDataSharing', data.allow_data_sharing);
        setCheck('privacyAnonymizePatient', data.anonymize_patient_data);
        setCheck('privacyEncryptSensitive', data.encrypt_sensitive_data);
        setCheck('privacyAuditAccess', data.audit_data_access);
        setCheck('privacyGdprMode', data.gdpr_compliance_mode);
      })
      .catch(function (err) {
        showError(err.message || 'Tải cài đặt bảo mật thất bại.');
      });
  }

  function setEl(id, value) {
    var el = document.getElementById(id);
    if (!el) return;
    if (el.type === 'checkbox') el.checked = !!value;
    else el.value = value != null ? value : '';
  }

  function setCheck(id, value) {
    var el = document.getElementById(id);
    if (el) el.checked = !!value;
  }

  function getEl(id) {
    var el = document.getElementById(id);
    if (!el) return undefined;
    if (el.type === 'checkbox') return el.checked;
    var v = el.value ? el.value.trim() : '';
    if (el.type === 'number') return v === '' ? undefined : parseInt(v, 10);
    return v || undefined;
  }

  function loadAiConfig() {
    window.AuraAPI.getAdminAiConfig()
      .then(function (data) {
        var threshold = data.threshold_config;
        if (typeof threshold === 'object') threshold = JSON.stringify(threshold, null, 2);
        setEl('aiThresholdConfig', threshold || '');
        var policy = data.retraining_policy;
        if (typeof policy === 'object') policy = JSON.stringify(policy, null, 2);
        setEl('aiRetrainingPolicy', policy || '');
      })
      .catch(function (err) {
        showError(err.message || 'Tải cấu hình AI thất bại.');
      });
  }

  function loadPolicies() {
    window.AuraAPI.getAdminCommunicationPolicies()
      .then(function (data) {
        if (policiesJson) {
          try {
            policiesJson.textContent = typeof data === 'object' ? JSON.stringify(data, null, 2) : String(data);
          } catch (e) {
            policiesJson.textContent = String(data);
          }
        }
      })
      .catch(function (err) {
        if (policiesJson) policiesJson.textContent = 'Lỗi: ' + (err.message || 'Tải thất bại.');
      });
  }

  function savePrivacy() {
    var payload = {
      data_retention_days: getEl('privacyDataRetentionDays'),
      auto_anonymize_after_days: getEl('privacyAutoAnonymizeDays'),
      require_consent_for_ai_training: getEl('privacyRequireConsentAi'),
      allow_data_sharing: getEl('privacyAllowDataSharing'),
      anonymize_patient_data: getEl('privacyAnonymizePatient'),
      encrypt_sensitive_data: getEl('privacyEncryptSensitive'),
      audit_data_access: getEl('privacyAuditAccess'),
      gdpr_compliance_mode: getEl('privacyGdprMode')
    };
    window.AuraAPI.updateAdminPrivacySettings(payload)
      .then(function () {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã lưu cài đặt bảo mật.', 'success');
      })
      .catch(function (e) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
      });
  }

  function saveAiConfig() {
    var thresholdRaw = getEl('aiThresholdConfig');
    var policyRaw = getEl('aiRetrainingPolicy');
    var threshold = thresholdRaw;
    var policy = policyRaw;
    try {
      if (thresholdRaw) threshold = JSON.parse(thresholdRaw);
    } catch (e) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Threshold không phải JSON hợp lệ.', 'warning');
      return;
    }
    try {
      if (policyRaw) policy = JSON.parse(policyRaw);
    } catch (e) {
      if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Chính sách huấn luyện không phải JSON hợp lệ.', 'warning');
      return;
    }
    var payload = {};
    if (threshold !== undefined) payload.threshold_config = typeof threshold === 'string' ? threshold : JSON.stringify(threshold);
    if (policy !== undefined) payload.retraining_policy = policy;
    window.AuraAPI.updateAdminAiConfig(payload)
      .then(function () {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã lưu cấu hình AI.', 'success');
      })
      .catch(function (e) {
        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(e.message || 'Lỗi', 'danger');
      });
  }

  if (btnSavePrivacy) btnSavePrivacy.addEventListener('click', savePrivacy);
  if (btnSaveAiConfig) btnSaveAiConfig.addEventListener('click', saveAiConfig);

  loadPrivacy();
  loadAiConfig();
  loadPolicies();
})();