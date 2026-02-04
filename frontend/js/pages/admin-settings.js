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
  var policiesTable = document.getElementById('policiesTable');
  var templatesTable = document.getElementById('templatesTable');

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

  function policyLabel(key) {
    var map = {
      ai_result_ready: 'Kết quả AI sẵn sàng',
      clinic_approved: 'Phòng khám được duyệt',
      payment_success: 'Thanh toán thành công',
      high_risk_alert: 'Cảnh báo nguy cơ cao'
    };
    return map[key] || key;
  }

  function renderPolicies(policies) {
    if (!policiesTable) return;
    var keys = Object.keys(policies || {});
    if (!keys.length) {
      policiesTable.innerHTML = '<div class="text-muted small">Chưa có chính sách nào.</div>';
      return;
    }
    keys.sort();
    var html = '<div class="table-responsive"><table class="table table-sm align-middle mb-0"><thead>' +
      '<tr><th>Loại sự kiện</th><th>Bật</th><th>Kênh gửi</th><th>Người nhận</th><th>Ưu tiên</th><th>Giới hạn/ngày</th><th></th></tr>' +
      '</thead><tbody>';
    keys.forEach(function (k) {
      var p = policies[k] || {};
      var enabled = !!p.enabled;
      var channels = p.channels || [];
      var recipients = p.recipients || [];
      var freq = p.frequency_limit != null ? p.frequency_limit : '';
      var priority = p.priority || 'normal';
      function cChecked(val) { return channels.indexOf(val) !== -1 ? 'checked' : ''; }
      function rChecked(val) { return recipients.indexOf(val) !== -1 ? 'checked' : ''; }
      html += '<tr data-policy-type="' + k + '">' +
        '<td><div class="fw-semibold">' + policyLabel(k) + '</div><div class="text-muted small">' + k + '</div></td>' +
        '<td><input type="checkbox" class="form-check-input" data-field="enabled" ' + (enabled ? 'checked' : '') + '></td>' +
        '<td>' +
          '<div class="form-check form-check-inline small"><input class="form-check-input" type="checkbox" value="in_app" data-field="channel" ' + cChecked('in_app') + '><label class="form-check-label">In-app</label></div>' +
          '<div class="form-check form-check-inline small"><input class="form-check-input" type="checkbox" value="email" data-field="channel" ' + cChecked('email') + '><label class="form-check-label">Email</label></div>' +
          '<div class="form-check form-check-inline small"><input class="form-check-input" type="checkbox" value="sms" data-field="channel" ' + cChecked('sms') + '><label class="form-check-label">SMS</label></div>' +
        '</td>' +
        '<td>' +
          '<div class="form-check form-check-inline small"><input class="form-check-input" type="checkbox" value="patient" data-field="recipient" ' + rChecked('patient') + '><label class="form-check-label">Bệnh nhân</label></div>' +
          '<div class="form-check form-check-inline small"><input class="form-check-input" type="checkbox" value="doctor" data-field="recipient" ' + rChecked('doctor') + '><label class="form-check-label">Bác sĩ</label></div>' +
          '<div class="form-check form-check-inline small"><input class="form-check-input" type="checkbox" value="clinic_manager" data-field="recipient" ' + rChecked('clinic_manager') + '><label class="form-check-label">Quản lý PK</label></div>' +
          '<div class="form-check form-check-inline small"><input class="form-check-input" type="checkbox" value="admin" data-field="recipient" ' + rChecked('admin') + '><label class="form-check-label">Admin</label></div>' +
        '</td>' +
        '<td><select class="form-select form-select-sm" data-field="priority">' +
          ['low','normal','high','urgent'].map(function (opt) {
            return '<option value="' + opt + '"' + (opt === priority ? ' selected' : '') + '>' +
              (opt === 'low' ? 'Thấp' : opt === 'normal' ? 'Bình thường' : opt === 'high' ? 'Cao' : 'Khẩn cấp') +
              '</option>';
          }).join('') +
        '</select></td>' +
        '<td><input type="number" class="form-control form-control-sm" min="0" data-field="frequency_limit" value="' + (freq === '' ? '' : freq) + '" placeholder="Không giới hạn"></td>' +
        '<td class="text-end"><button type="button" class="btn btn-outline-primary btn-sm btn-save-policy" data-policy-type="' + k + '">Lưu</button></td>' +
        '</tr>';
    });
    html += '</tbody></table></div>';
    policiesTable.innerHTML = html;
  }

  function loadPolicies() {
    if (!policiesTable) return;
    policiesTable.innerHTML = '<div class="text-muted small">Đang tải...</div>';
    window.AuraAPI.getAdminCommunicationPolicies()
      .then(function (data) {
        var policies = data && data.policies ? data.policies : data;
        renderPolicies(policies || {});
      })
      .catch(function (err) {
        policiesTable.innerHTML = '<div class="text-danger small">Lỗi: ' + (err.message || 'Tải thất bại.') + '</div>';
      });
  }

  function loadTemplates() {
    if (!templatesTable) return;
    templatesTable.innerHTML = '<div class="text-muted small">Đang tải...</div>';
    window.AuraAPI.adminListNotificationTemplates(true)
      .then(function (data) {
        var list = (data && data.templates) || [];
        if (!list.length) {
          templatesTable.innerHTML = '<div class="text-muted small">Chưa có mẫu thông báo.</div>';
          return;
        }
        list.sort(function (a, b) {
          if (a.template_type === b.template_type) return a.template_id - b.template_id;
          return String(a.template_type).localeCompare(String(b.template_type));
        });
        var html = '<div class="table-responsive"><table class="table table-sm align-middle mb-0"><thead>' +
          '<tr><th>Loại</th><th>Tên mẫu</th><th>Tiêu đề</th><th>Trạng thái</th><th></th></tr></thead><tbody>';
        list.forEach(function (t) {
          html += '<tr data-template-id="' + t.template_id + '">' +
            '<td><div class="fw-semibold">' + (t.template_type || '-') + '</div></td>' +
            '<td>' + (t.template_name || '-') + '</td>' +
            '<td class="small text-muted">' + (t.subject || '-') + '</td>' +
            '<td>' + (t.is_active ? '<span class="badge bg-success">Đang dùng</span>' : '<span class="badge bg-secondary">Không dùng</span>') + '</td>' +
            '<td class="text-end">' +
              (t.is_active
                ? '<button type="button" class="btn btn-outline-secondary btn-sm btn-deactivate-template" data-template-id="' + t.template_id + '">Tắt</button>'
                : '<button type="button" class="btn btn-outline-primary btn-sm btn-activate-template" data-template-id="' + t.template_id + '">Kích hoạt</button>') +
            '</td>' +
            '</tr>';
        });
        html += '</tbody></table></div>';
        templatesTable.innerHTML = html;
      })
      .catch(function (err) {
        templatesTable.innerHTML = '<div class="text-danger small">Lỗi: ' + (err.message || 'Tải thất bại.') + '</div>';
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
  loadTemplates();

  if (policiesTable) {
    policiesTable.addEventListener('click', function (e) {
      var btn = e.target.closest('.btn-save-policy');
      if (!btn) return;
      var type = btn.getAttribute('data-policy-type');
      var row = policiesTable.querySelector('tr[data-policy-type=\"' + type + '\"]');
      if (!row) return;
      var enabled = !!row.querySelector('input[data-field=\"enabled\"]').checked;
      var channels = [];
      row.querySelectorAll('input[data-field=\"channel\"]:checked').forEach(function (el) { channels.push(el.value); });
      var recipients = [];
      row.querySelectorAll('input[data-field=\"recipient\"]:checked').forEach(function (el) { recipients.push(el.value); });
      var priorityEl = row.querySelector('select[data-field=\"priority\"]');
      var priority = priorityEl ? priorityEl.value : 'normal';
      var freqEl = row.querySelector('input[data-field=\"frequency_limit\"]');
      var freqVal = freqEl && freqEl.value !== '' ? parseInt(freqEl.value, 10) : null;
      var payload = {
        enabled: enabled,
        channels: channels,
        recipients: recipients,
        priority: priority
      };
      if (freqVal != null && !isNaN(freqVal) && freqVal > 0) payload.frequency_limit = freqVal;
      window.AuraAPI.updateAdminCommunicationPolicy(type, payload)
        .then(function () {
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã lưu chính sách ' + type + '.', 'success');
        })
        .catch(function (err) {
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(err.message || 'Lỗi lưu chính sách.', 'danger');
        });
    });
  }

  if (templatesTable) {
    templatesTable.addEventListener('click', function (e) {
      var activateBtn = e.target.closest('.btn-activate-template');
      var deactivateBtn = e.target.closest('.btn-deactivate-template');
      if (!activateBtn && !deactivateBtn) return;
      var id = (activateBtn || deactivateBtn).getAttribute('data-template-id');
      if (!id) return;
      var action = activateBtn ? 'activate' : 'deactivate';
      var fn = activateBtn ? window.AuraAPI.adminActivateNotificationTemplate : window.AuraAPI.adminDeactivateNotificationTemplate;
      fn(id)
        .then(function () {
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast((action === 'activate' ? 'Đã kích hoạt mẫu.' : 'Đã tắt mẫu.'), 'success');
          loadTemplates();
        })
        .catch(function (err) {
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast(err.message || 'Lỗi khi cập nhật mẫu.', 'danger');
        });
    });
  }
})();
