/**
 * AURA - Patient Analysis Results (FR-3, FR-6)
 * Hiển thị kết quả phân tích AI: chỉ số (bệnh lý, độ tin cậy) và mức độ rủi ro
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Patient')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var patientId = null;
  var listEl = document.getElementById('analysisList');

  function getPatient() {
    if (!accountId) return Promise.reject(new Error('Không tìm thấy tài khoản.'));
    return window.AuraAPI.getPatientByAccount(accountId).then(function (p) {
      if (!p || !p.patient_id) return Promise.reject(new Error('Chưa có hồ sơ bệnh nhân.'));
      patientId = p.patient_id;
      return patientId;
    });
  }

  function formatDate(str) {
    if (!str) return '-';
    var d = new Date(str);
    return isNaN(d.getTime()) ? str : d.toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' });
  }

  function statusLabel(s) {
    var map = { completed: 'Hoàn thành', processing: 'Đang xử lý', pending: 'Chờ xử lý', failed: 'Thất bại' };
    return map[s] || s || '-';
  }

  function riskLabel(s) {
    var map = { low: 'Thấp', medium: 'Trung bình', high: 'Cao', critical: 'Rất cao' };
    return map[(s || '').toLowerCase()] || s || '-';
  }

  function riskBadgeClass(s) {
    var map = { low: 'success', medium: 'info', high: 'warning', critical: 'danger' };
    return map[(s || '').toLowerCase()] || 'secondary';
  }

  function diseaseLabel(s) {
    if (!s) return '-';
    var map = {
      diabetic_retinopathy: 'Bệnh võng mạc đái tháo đường',
      amd: 'Thoái hóa hoàng điểm',
      glaucoma: 'Glaucoma',
      dr: 'Bệnh võng mạc đái tháo đường'
    };
    return map[s.toLowerCase()] || s;
  }

  function confidencePercent(val) {
    if (val == null) return '-';
    var n = parseFloat(val);
    return isNaN(n) ? val : (n <= 1 ? (n * 100).toFixed(1) : n.toFixed(1)) + '%';
  }

  getPatient()
    .then(function () { return window.AuraAPI.getPatientAnalyses(patientId, 50, 0); })
    .then(function (data) {
      var analyses = (data && data.analyses) || [];
      if (!listEl) return;
      if (!analyses.length) {
        listEl.innerHTML = '<div class="col-12"><div class="card border-0 shadow-sm"><div class="card-body text-center text-muted py-5">Chưa có kết quả phân tích. <a href="upload-image.html">Upload ảnh</a> để bắt đầu.</div></div></div>';
        return;
      }
      listEl.innerHTML = 'Đang tải chỉ số...';
      var promises = analyses.map(function (a) {
        return window.AuraAPI.getResultsByAnalysis(a.analysis_id).then(function (res) {
          return { analysis: a, results: (res && res.results) || [] };
        }).catch(function () {
          return { analysis: a, results: [] };
        });
      });
      return Promise.all(promises).then(function (items) {
        if (!listEl) return;
        listEl.innerHTML = items.map(function (item) {
          var a = item.analysis;
          var results = item.results;
          var dateStr = formatDate(a.analysis_time);
          var status = statusLabel(a.status);
          var statusClass = a.status === 'completed' ? 'success' : a.status === 'failed' ? 'danger' : 'secondary';
          var resultsHtml = '';
          if (results.length) {
            resultsHtml =
              '<div class="aura-analysis-metrics mt-3">' +
              '<div class="aura-metrics-title"><i class="bi bi-bar-chart-line me-1"></i>Chỉ số &amp; mức rủi ro</div>' +
              '<div class="aura-metrics-list">' +
              results.map(function (r) {
                var riskClass = riskBadgeClass(r.risk_level);
                var diseaseDisplay = (r.disease_type || '').replace(/_/g, ' ').toLowerCase();
                if (!diseaseDisplay) diseaseDisplay = '-';
                return (
                  '<div class="aura-metric-item">' +
                  '<div class="aura-metric-line"><span class="aura-metric-label">Bệnh:</span> <span class="aura-metric-value">' + diseaseDisplay + '</span></div>' +
                  '<div class="aura-metric-line"><span class="aura-metric-label">Mức rủi ro:</span> <span class="badge aura-risk-badge bg-' + riskClass + ' rounded-pill">' + riskLabel(r.risk_level) + '</span></div>' +
                  '<div class="aura-metric-line"><span class="aura-metric-label">Độ tin cậy:</span> <strong>' + confidencePercent(r.confidence_score) + '</strong></div>' +
                  '</div>'
                );
              }).join('') +
              '</div></div>';
          } else {
            resultsHtml = '<div class="aura-analysis-metrics mt-3"><p class="small text-muted mb-0">Chưa có chỉ số chi tiết.</p></div>';
          }
          return (
            '<div class="col-md-6 col-lg-4">' +
            '<div class="card aura-analysis-card border-0 shadow-sm h-100">' +
            '<div class="card-body">' +
            '<div class="d-flex justify-content-between align-items-start mb-2">' +
            '<h6 class="card-title mb-0"><i class="bi bi-graph-up-arrow text-primary me-1"></i>Phân tích #' + (a.analysis_id || '-') + '</h6>' +
            '<span class="badge bg-' + statusClass + ' rounded-pill">' + status + '</span>' +
            '</div>' +
            '<p class="card-text small text-muted mb-0"><i class="bi bi-image me-1"></i>Ảnh #' + (a.image_id || '-') + '</p>' +
            '<p class="card-text small text-muted mb-0"><i class="bi bi-clock me-1"></i>' + dateStr + '</p>' +
            resultsHtml +
            '<a href="reports.html" class="btn btn-outline-primary btn-sm mt-3 w-100"><i class="bi bi-file-earmark-text me-1"></i>Xem báo cáo</a>' +
            '</div></div></div>'
          );
        }).join('');
      });
    })
    .catch(function (err) {
      if (listEl) listEl.innerHTML = '<div class="col-12"><div class="alert alert-warning">' + (err.message || 'Không tải được dữ liệu.') + '</div></div>';
    });
})();
