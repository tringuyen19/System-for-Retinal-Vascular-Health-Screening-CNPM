/**
 * AURA - FR-26: Tạo báo cáo sàng lọc cho các chiến dịch y tế
 * Form: campaign name, date range -> Generate -> Full report display + Print
 * Các báo cáo đã tạo: lưu metadata trong localStorage, hiển thị danh sách, Xem / Xuất PDF.
 */
(function () {
    'use strict';
  
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;
  
    var user = window.AuraAuth.getUser();
    var clinicId = user && user.clinic_id;
  
    var STORAGE_KEY_PREFIX = 'aura_screening_reports_';
  
    var pageError = document.getElementById('pageError');
    var campaignName = document.getElementById('campaignName');
    var startDate = document.getElementById('startDate');
    var endDate = document.getElementById('endDate');
    var btnGenerate = document.getElementById('btnGenerate');
    var reportCard = document.getElementById('reportCard');
    var reportPlaceholder = document.getElementById('reportPlaceholder');
    var reportContent = document.getElementById('reportContent');
    var btnExportPdf = document.getElementById('btnExportPdf');
    var savedReportsLoading = document.getElementById('savedReportsLoading');
    var savedReportsContent = document.getElementById('savedReportsContent');
    var savedReportsTbody = document.getElementById('savedReportsTbody');
    var savedReportsSummary = document.getElementById('savedReportsSummary');
    var savedReportsEmpty = document.getElementById('savedReportsEmpty');
  
    function showError(msg) {
      if (!pageError) return;
      pageError.textContent = msg || '';
      pageError.classList.toggle('d-none', !msg);
    }
  
    function getStorageKey() {
      return STORAGE_KEY_PREFIX + (clinicId || '0');
    }
  
    function getSavedReports() {
      try {
        var raw = localStorage.getItem(getStorageKey());
        var list = raw ? JSON.parse(raw) : [];
        return Array.isArray(list) ? list : [];
      } catch (e) {
        return [];
      }
    }
  
    function saveReportMeta(meta) {
      var list = getSavedReports();
      list.unshift(meta);
      if (list.length > 50) list = list.slice(0, 50);
      try {
        localStorage.setItem(getStorageKey(), JSON.stringify(list));
      } catch (e) {}
    }
  
    function loadSavedReportsUI() {
      if (!savedReportsLoading || !savedReportsContent || !savedReportsTbody || !savedReportsEmpty) return;
      savedReportsLoading.classList.add('d-none');
      var list = getSavedReports();
      if (!list.length) {
        savedReportsEmpty.classList.remove('d-none');
        savedReportsContent.classList.add('d-none');
        return;
      }
      savedReportsEmpty.classList.add('d-none');
      savedReportsContent.classList.remove('d-none');
      if (savedReportsSummary) savedReportsSummary.textContent = 'Tổng ' + list.length + ' báo cáo (lưu trên trình duyệt).';
      var html = list.map(function (r, i) {
        var periodStr = (r.start_date || '—') + ' → ' + (r.end_date || '—');
        var createdStr = r.generated_at ? new Date(r.generated_at).toLocaleString('vi-VN') : '—';
        var name = (r.campaign_name || 'Chiến dịch').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return '<tr><td>' + name + '</td><td class="small">' + periodStr + '</td><td class="small">' + createdStr + '</td><td class="text-end">' +
          '<button type="button" class="btn btn-sm btn-outline-primary me-1 btn-view-report" data-index="' + i + '"><i class="bi bi-eye me-1"></i>Xem</button>' +
          '<button type="button" class="btn btn-sm btn-outline-secondary btn-export-pdf-report" data-index="' + i + '"><i class="bi bi-file-pdf me-1"></i>Xuất PDF</button></td></tr>';
      }).join('');
      savedReportsTbody.innerHTML = html;
      savedReportsTbody.querySelectorAll('.btn-view-report').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var idx = parseInt(btn.getAttribute('data-index'), 10);
          var list = getSavedReports();
          var r = list[idx];
          if (r) viewReport({ campaign_name: r.campaign_name || '', start_date: r.start_date || '', end_date: r.end_date || '' });
        });
      });
      savedReportsTbody.querySelectorAll('.btn-export-pdf-report').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var idx = parseInt(btn.getAttribute('data-index'), 10);
          var list = getSavedReports();
          var r = list[idx];
          if (r) exportPdfReport({ campaign_name: r.campaign_name || '', start_date: r.start_date || '', end_date: r.end_date || '' });
        });
      });
    }
  
    function exportReportToPdf() {
      if (!reportContent || reportContent.classList.contains('d-none')) {
        showError('Chưa có nội dung báo cáo để xuất. Vui lòng tạo hoặc xem báo cáo trước.');
        return;
      }
      var opt = {
        margin: 12,
        filename: 'bao-cao-sang-loc-' + (new Date().toISOString().slice(0, 10)) + '.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      if (typeof html2pdf !== 'undefined') {
        html2pdf().set(opt).from(reportContent).save().catch(function (err) {
          showError(err.message || 'Xuất PDF thất bại.');
        });
      } else {
        showError('Công cụ xuất PDF chưa sẵn sàng.');
      }
    }
  
    function exportPdfReport(params) {
      if (!clinicId) return;
      var p = params || {};
      window.AuraAPI.getClinicScreeningReport(clinicId, (p.campaign_name || p.start_date || p.end_date) ? p : null)
        .then(function (data) {
          renderReport(data);
          setTimeout(exportReportToPdf, 400);
        })
        .catch(function (err) {
          showError(err.message || 'Không tải được báo cáo.');
        });
    }
  
    function viewReport(params) {
      if (!clinicId) return;
      var p = params || {};
      window.AuraAPI.getClinicScreeningReport(clinicId, (p.campaign_name || p.start_date || p.end_date) ? p : null)
        .then(function (data) {
          renderReport(data);
          if (reportCard) reportCard.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(function (err) {
          showError(err.message || 'Không tải được báo cáo.');
        });
    }
  
    function renderReport(data) {
      if (!data || !reportContent) return;
  
      var overview = data.campaign_overview || {};
      var period = data.period || {};
      var sum = data.summary || {};
      var distPatients = data.risk_distribution_patients || {};
      var pct = data.risk_percentages || {};
      var recCounts = data.recommendation_counts || {};
      var usage = data.usage_statistics || {};
      var recs = data.recommendations || [];
  
      var periodStr = (period.start_date || 'Không giới hạn') + ' → ' + (period.end_date || 'Hiện tại');
      var genAt = period.generated_at ? new Date(period.generated_at).toLocaleString('vi-VN') : '-';
  
      // 1. Thông tin tổng quan chiến dịch (chỉ đầu mục in đậm, nội dung bình thường)
      var overviewHtml =
        '<p class="mb-1">Tên chiến dịch sàng lọc: ' + (overview.campaign_name || data.campaign_name || '-') + '</p>' +
        '<p class="mb-1">Thời gian thực hiện: ' + periodStr + '</p>' +
        '<p class="mb-1">Địa điểm / Phòng khám: ' + (overview.location || '-') + '</p>' +
        '<p class="mb-1">Đơn vị tổ chức: ' + (overview.organizing_unit || '-') + '</p>' +
        '<p class="mb-0">Mục đích: ' + (overview.purpose || 'Quản lý & báo cáo hành chính.') + '</p>';
  
      // 2. Quy mô & mức độ tham gia
      var scaleHtml =
        '<p class="mb-1">Tổng số người được sàng lọc: ' + (sum.total_patients_screened != null ? sum.total_patients_screened : '-') + '</p>' +
        '<p class="mb-0">Số ảnh võng mạc đã phân tích: ' + (sum.total_images_analyzed != null ? sum.total_images_analyzed : '-') + '</p>';
  
      // 3. Phân bố mức độ nguy cơ (tỷ lệ % người)
      var lowN = distPatients.low != null ? distPatients.low : 0;
      var medN = distPatients.medium != null ? distPatients.medium : 0;
      var highN = distPatients.high != null ? distPatients.high : 0;
      var riskDistHtml =
        '<ul class="list-unstyled mb-0">' +
        '<li>Nguy cơ thấp: ' + lowN + ' người (' + (pct.low != null ? pct.low : 0) + '%)</li>' +
        '<li>Nguy cơ trung bình: ' + medN + ' người (' + (pct.medium != null ? pct.medium : 0) + '%)</li>' +
        '<li>Nguy cơ cao: ' + highN + ' người (' + (pct.high != null ? pct.high : 0) + '%)</li>' +
        '</ul>';
  
      // 4. Kết quả khuyến nghị sau sàng lọc
      var specN = recCounts.recommend_specialist != null ? recCounts.recommend_specialist : 0;
      var bpN = recCounts.recommend_bp_diabetes_check != null ? recCounts.recommend_bp_diabetes_check : 0;
      var followN = recCounts.recommend_follow_up != null ? recCounts.recommend_follow_up : 0;
      var recSectionHtml =
        '<ul class="list-unstyled mb-0">' +
        '<li>Khám chuyên khoa: ' + specN + ' người</li>' +
        '<li>Kiểm tra huyết áp / tiểu đường: ' + bpN + ' người</li>' +
        '<li>Theo dõi định kỳ: ' + followN + ' người</li>' +
        '</ul>';
  
      var recsText = recs.length ? '<ul class="mb-0 mt-2">' + recs.map(function (r) { return '<li>' + r + '</li>'; }).join('') + '</ul>' : '';
  
      reportContent.innerHTML =
        '<div class="report-pdf-content">' +
        '<h5 class="mb-3 fw-bold">Kết quả báo cáo sàng lọc</h5>' +
        '<div class="mb-4">' +
        '<h6 class="text-muted border-bottom pb-2 fw-bold">1. Thông tin tổng quan chiến dịch</h6>' +
        overviewHtml +
        '<p class="mb-0 mt-2 small text-muted">Thời gian tạo báo cáo: ' + genAt + '</p>' +
        '</div>' +
  
        '<div class="mb-4">' +
        '<h6 class="text-muted border-bottom pb-2 fw-bold">2. Quy mô & mức độ tham gia</h6>' +
        scaleHtml +
        '</div>' +
  
        '<div class="mb-4">' +
        '<h6 class="text-muted border-bottom pb-2 fw-bold">3. Phân bố mức độ nguy cơ sức khỏe (tỷ lệ người)</h6>' +
        riskDistHtml +
        '</div>' +
  
        '<div class="mb-4">' +
        '<h6 class="text-muted border-bottom pb-2 fw-bold">4. Kết quả khuyến nghị sau sàng lọc</h6>' +
        '<p class="text-muted small mb-2">Số người được khuyến nghị (tổng hợp, ẩn danh):</p>' +
        recSectionHtml +
        (recsText ? '<div class="mt-3">Gợi ý theo dõi:' + recsText + '</div>' : '') +
        '</div></div>';
  
      reportPlaceholder.classList.add('d-none');
      reportContent.classList.remove('d-none');
      reportCard.classList.remove('d-none');
    }
  
    function generate() {
      if (!clinicId) {
        showError('Bạn chưa được gán phòng khám.');
        return;
      }
      var sd = startDate && startDate.value ? startDate.value : null;
      var ed = endDate && endDate.value ? endDate.value : null;
      if (sd && ed && ed < sd) {
        showError('Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.');
        return;
      }
      showError('');
      if (btnGenerate) btnGenerate.disabled = true;
  
      var params = {};
      if (campaignName && campaignName.value.trim()) params.campaign_name = campaignName.value.trim();
      if (startDate && startDate.value) params.start_date = startDate.value;
      if (endDate && endDate.value) params.end_date = endDate.value;
  
      window.AuraAPI.getClinicScreeningReport(clinicId, Object.keys(params).length ? params : null)
        .then(function (data) {
          renderReport(data);
          var period = (data && data.period) || {};
          saveReportMeta({
            campaign_name: (data && data.campaign_name) || (campaignName && campaignName.value.trim()) || '',
            start_date: period.start_date || (startDate && startDate.value) || null,
            end_date: period.end_date || (endDate && endDate.value) || null,
            generated_at: period.generated_at || new Date().toISOString()
          });
          loadSavedReportsUI();
          if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Tạo báo cáo thành công.', 'success');
        })
        .catch(function (err) {
          showError(err.message || 'Không tạo được báo cáo.');
          if (reportContent) { reportContent.classList.add('d-none'); reportPlaceholder.classList.remove('d-none'); reportPlaceholder.textContent = 'Tạo báo cáo thất bại. Vui lòng thử lại.'; }
        })
        .finally(function () {
          if (btnGenerate) btnGenerate.disabled = false;
        });
    }
  
    /** Gợi ý khoảng ngày: đầu tháng hiện tại -> hôm nay (không ghi đè nếu user đã chọn) */
    function setDefaultDateRange() {
      var now = new Date();
      var firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
      var y = firstDay.getFullYear(), m = String(firstDay.getMonth() + 1).padStart(2, '0'), d = String(firstDay.getDate()).padStart(2, '0');
      var endY = now.getFullYear(), endM = String(now.getMonth() + 1).padStart(2, '0'), endD = String(now.getDate()).padStart(2, '0');
      if (startDate && !startDate.value) startDate.value = y + '-' + m + '-' + d;
      if (endDate && !endDate.value) endDate.value = endY + '-' + endM + '-' + endD;
    }
  
    if (btnGenerate) btnGenerate.addEventListener('click', generate);
    if (btnExportPdf) btnExportPdf.addEventListener('click', exportReportToPdf);
  
    setDefaultDateRange();
    loadSavedReportsUI();
  })();
  