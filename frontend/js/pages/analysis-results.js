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
        var resultsPromise = window.AuraAPI.getResultsByAnalysis(a.analysis_id).then(function (res) {
          return (res && res.results) || [];
        }).catch(function () { return []; });
        var annotationPromise = window.AuraAPI.getAnnotationByAnalysis(a.analysis_id).then(function (res) {
          return (res && (res.heatmap_url !== undefined || res.annotation_id !== undefined)) ? res : null;
        }).catch(function () { return null; });
        return Promise.all([resultsPromise, annotationPromise]).then(function (arr) {
          return { analysis: a, results: arr[0], annotation: arr[1] };
        });
      });
      return Promise.all(promises).then(function (items) {
        if (!listEl) return;
        listEl.innerHTML = items.map(function (item) {
          var a = item.analysis;
          var results = item.results;
          var annotation = item.annotation;
          var heatmapUrl = (annotation && annotation.heatmap_url) ? (annotation.heatmap_url + '').trim() : '';
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
          var annotationHtml = '';
          var modalId = 'aura-annotation-modal-' + (a.analysis_id || '');
          annotationHtml =
            '<div class="aura-annotation-section mt-3 rounded border bg-light">' +
            '<div class="aura-metrics-title px-2 pt-2"><i class="bi bi-image-fill me-1"></i>Ảnh chú thích AI (heatmap)</div>';
          if (heatmapUrl) {
            var safeUrl = heatmapUrl.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
            annotationHtml +=
              '<div class="px-2 pb-2">' +
              '<a href="' + safeUrl + '" target="_blank" rel="noopener" class="d-block rounded overflow-hidden border bg-white mt-2" style="max-height: 160px;">' +
              '<img src="' + safeUrl + '" alt="Chú thích AI" class="img-fluid w-100" style="object-fit: contain; max-height: 160px;" loading="lazy">' +
              '</a>' +
              '<button type="button" class="btn btn-outline-primary btn-sm mt-2 w-100" data-bs-toggle="modal" data-bs-target="#' + modalId + '">' +
              '<i class="bi bi-zoom-in me-1"></i>Xem phóng to' +
              '</button>' +
              '</div>';
            annotationHtml +=
              '<div class="modal fade" id="' + modalId + '" tabindex="-1">' +
              '<div class="modal-dialog modal-lg modal-dialog-centered">' +
              '<div class="modal-content"><div class="modal-header"><h6 class="modal-title">Ảnh chú thích AI – Phân tích ' + (a.analysis_id || '') + '</h6><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>' +
              '<div class="modal-body text-center p-0">' +
              '<img src="' + safeUrl + '" alt="Chú thích AI" class="img-fluid" style="max-width: 100%;">' +
              '</div></div></div></div>';
          } else {
            annotationHtml +=
              '<div class="px-2 pb-3 pt-1 text-center">' +
              '<i class="bi bi-image text-muted" style="font-size: 2rem;"></i>' +
              '<p class="small text-muted mb-0 mt-2">Chưa có ảnh heatmap. Ảnh chú thích sẽ hiển thị tại đây khi có dữ liệu.</p>' +
              '</div>';
          }
          annotationHtml += '</div>';
          return (
            '<div class="col-md-6 col-lg-4">' +
            '<div class="card aura-analysis-card border-0 shadow-sm h-100">' +
            '<div class="card-body">' +
            '<div class="d-flex justify-content-between align-items-start mb-2">' +
            '<h6 class="card-title mb-0"><i class="bi bi-graph-up-arrow text-primary me-1"></i>Phân tích ' + (a.analysis_id || '-') + '</h6>' +
            '<span class="badge bg-' + statusClass + ' rounded-pill">' + status + '</span>' +
            '</div>' +
            '<p class="card-text small text-muted mb-0"><i class="bi bi-image me-1"></i>Ảnh ' + (a.image_id || '-') + '</p>' +
            '<p class="card-text small text-muted mb-0"><i class="bi bi-clock me-1"></i>' + dateStr + '</p>' +
            resultsHtml +
            annotationHtml +
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
