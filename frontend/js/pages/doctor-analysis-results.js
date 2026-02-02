/**
 * AURA - Doctor: Xem kết quả phân tích và chú thích từ AI (FR-14)
 * Hiển thị danh sách trực tiếp từ entity [dbo].[ai_results] và [dbo].[ai_annotations].
 */
(function () {
    'use strict';
  
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;
  
    var resultsSection = document.getElementById('resultsSection');
    var annotationsSection = document.getElementById('annotationsSection');
    var loadingPlaceholder = document.getElementById('loadingPlaceholder');
    var pageError = document.getElementById('pageError');
    var filterRisk = document.getElementById('filterRisk');
    var filterAnalysisId = document.getElementById('filterAnalysisId');
  
    var resultsData = [];
    var annotationsData = [];
  
    function showError(msg) {
      if (!pageError) return;
      pageError.textContent = msg || '';
      pageError.classList.toggle('d-none', !msg);
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
      return (s + '').replace(/_/g, ' ');
    }
  
    function escapeHtml(str) {
      if (!str) return '';
      return (str + '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
  
    function confidenceDisplay(val) {
      if (val == null) return '-';
      var n = parseFloat(val);
      return isNaN(n) ? val : (n <= 1 ? (n * 100).toFixed(1) : n.toFixed(1)) + '%';
    }
  
    function filterResults() {
      var riskVal = (filterRisk && filterRisk.value || '').toLowerCase();
      var searchStr = (filterAnalysisId && filterAnalysisId.value || '').trim().toLowerCase();
      return resultsData.filter(function (r) {
        if (riskVal && (r.risk_level || '').toLowerCase() !== riskVal) return false;
        if (searchStr) {
          var nameMatch = (r.patient_name || '').toLowerCase().indexOf(searchStr) !== -1;
          var aidMatch = (r.analysis_id + '') === searchStr;
          if (!nameMatch && !aidMatch) return false;
        }
        return true;
      });
    }
  
    function filterAnnotations() {
      var searchStr = (filterAnalysisId && filterAnalysisId.value || '').trim().toLowerCase();
      return annotationsData.filter(function (a) {
        if (!searchStr) return true;
        var nameMatch = (a.patient_name || '').toLowerCase().indexOf(searchStr) !== -1;
        var aidMatch = (a.analysis_id + '') === searchStr;
        return nameMatch || aidMatch;
      });
    }
  
    function renderResults() {
      if (!resultsSection) return;
      var list = filterResults();
      var html =
        '<div class="card border-0 shadow-sm">' +
        '<div class="card-header bg-white"><h5 class="mb-0"><i class="bi bi-bar-chart-line me-1"></i>Kết quả phân tích AI</h5></div>' +
        '<div class="card-body">';
      if (!list.length) {
        html += '<p class="text-muted mb-0">Không có bản ghi nào' + (resultsData.length ? ' khớp bộ lọc.' : ' trong bảng ai_results.') + '</p>';
      } else {
        html += '<div class="table-responsive"><table class="table table-sm table-bordered table-hover mb-0">' +
          '<thead class="table-light">' +
          '<tr><th>Bệnh nhân</th><th>Bệnh lý</th><th>Mức rủi ro</th><th>Độ tin cậy</th><th>Thao tác</th></tr>' +
          '</thead><tbody>';
        list.forEach(function (r) {
          var riskClass = riskBadgeClass(r.risk_level);
          html += '<tr>' +
            '<td>' + escapeHtml(r.patient_name || '-') + '</td>' +
            '<td>' + escapeHtml(diseaseLabel(r.disease_type)) + '</td>' +
            '<td><span class="badge bg-' + riskClass + ' rounded-pill">' + riskLabel(r.risk_level) + '</span></td>' +
            '<td><strong>' + confidenceDisplay(r.confidence_score) + '</strong></td>' +
            '<td>' +
              (r.analysis_id
                ? '<a href="reviews.html?analysis_id=' + encodeURIComponent(r.analysis_id) + '" class="btn btn-sm btn-outline-primary">' +
                    '<i class="bi bi-clipboard-check me-1"></i>Xác nhận / chỉnh sửa' +
                  '</a>'
                : '<span class="text-muted small">-</span>') +
            '</td>' +
            '</tr>';
        });
      }
      html += '</div></div>';
      resultsSection.innerHTML = html;
    }
  
    function renderAnnotations() {
      if (!annotationsSection) return;
      var list = filterAnnotations();
      var html =
        '<div class="card border-0 shadow-sm">' +
        '<div class="card-header bg-white"><h5 class="mb-0"><i class="bi bi-pin-map me-1"></i>Chú thích từ AI</h5></div>' +
        '<div class="card-body">';
      if (!list.length) {
        html += '<p class="text-muted mb-0">Không có bản ghi nào' + (annotationsData.length ? ' khớp bộ lọc.' : ' trong bảng ai_annotations.') + '</p>';
      } else {
        html += '<div class="table-responsive"><table class="table table-sm table-bordered table-hover mb-0">' +
          '<thead class="table-light">' +
          '<tr><th>Bệnh nhân</th><th>Heatmap</th><th>Mô tả</th></tr>' +
          '</thead><tbody>';
        list.forEach(function (a) {
          var heatmapCell = (a.heatmap_url)
            ? '<a href="' + escapeHtml(a.heatmap_url) + '" target="_blank" rel="noopener">Xem ảnh</a>'
            : '-';
          html += '<tr>' +
            '<td>' + escapeHtml(a.patient_name || '-') + '</td>' +
            '<td>' + heatmapCell + '</td>' +
            '<td class="small">' + (a.description ? escapeHtml(a.description) : '-') + '</td>' +
            '</tr>';
        });
        html += '</tbody></table></div>';
      }
      html += '</div></div>';
      annotationsSection.innerHTML = html;
    }
  
    function render() {
      renderResults();
      renderAnnotations();
    }
  
    function load() {
      showError('');
      if (loadingPlaceholder) loadingPlaceholder.style.display = 'block';
      if (resultsSection) resultsSection.innerHTML = '';
      if (annotationsSection) annotationsSection.innerHTML = '';
  
      Promise.all([
        window.AuraAPI.getAllResults(),
        window.AuraAPI.getAllAnnotations()
      ])
        .then(function (arr) {
          var resData = arr[0];
          var annData = arr[1];
          resultsData = (resData && resData.results) || [];
          annotationsData = (annData && annData.annotations) || [];
          if (loadingPlaceholder) loadingPlaceholder.style.display = 'none';
          render();
          if (filterRisk) {
            filterRisk.addEventListener('change', render);
          }
          if (filterAnalysisId) {
            filterAnalysisId.addEventListener('input', render);
            filterAnalysisId.addEventListener('change', render);
          }
        })
        .catch(function (err) {
          showError(err.message || 'Không tải được danh sách từ ai_results / ai_annotations.');
          if (loadingPlaceholder) loadingPlaceholder.style.display = 'none';
          if (resultsSection) resultsSection.innerHTML = '';
          if (annotationsSection) annotationsSection.innerHTML = '';
        });
    }
  
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', load);
    } else {
      load();
    }
  })();
  