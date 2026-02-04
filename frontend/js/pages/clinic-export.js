/**
 * AURA - Clinic Export (FR-30)
 * Xuất thống kê tổng hợp phục vụ nghiên cứu hoặc quản lý
 * GET /api/clinics/:id/export-statistics?format=json|csv_data&start_date=&end_date=
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('ClinicManager')) return;

  var user = window.AuraAuth.getUser();
  var clinicId = user && user.clinic_id;

  var pageError = document.getElementById('pageError');
  var exportFormat = document.getElementById('exportFormat');
  var startDateEl = document.getElementById('startDate');
  var endDateEl = document.getElementById('endDate');
  var btnExport = document.getElementById('btnExport');
  var previewContent = document.getElementById('previewContent');
  var summaryCardsCard = document.getElementById('summaryCardsCard');
  var summaryCards = document.getElementById('summaryCards');
  var previewTitle = document.getElementById('previewTitle');
  var btnToggleRaw = document.getElementById('btnToggleRaw');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function buildSummaryCards(data) {
    if (!data || !summaryCards) return '';
    var info = data.clinic_info || {};
    var risk = data.risk_statistics || {};
    var usage = data.usage_statistics || {};
    var reports = data.reports_statistics || {};
    var html = '<div class="row g-2">' +
      '<div class="col-6 col-md-3"><div class="border rounded p-2 text-center"><div class="small text-muted">Bác sĩ</div><strong>' + (info.total_doctors || 0) + '</strong></div></div>' +
      '<div class="col-6 col-md-3"><div class="border rounded p-2 text-center"><div class="small text-muted">Bệnh nhân</div><strong>' + (info.total_patients || 0) + '</strong></div></div>' +
      '<div class="col-6 col-md-3"><div class="border rounded p-2 text-center"><div class="small text-muted">Phân tích AI</div><strong>' + (risk.total_analyses || 0) + '</strong></div></div>' +
      '<div class="col-6 col-md-3"><div class="border rounded p-2 text-center"><div class="small text-muted">Ảnh đã tải</div><strong>' + (usage.total_images_uploaded || 0) + '</strong></div></div>' +
      '<div class="col-6 col-md-3"><div class="border rounded p-2 text-center"><div class="small text-muted">Báo cáo</div><strong>' + (reports.total_reports || 0) + '</strong></div></div>' +
      '<div class="col-6 col-md-3"><div class="border rounded p-2 text-center"><div class="small text-muted">Nguy cơ cao</div><strong>' + (risk.high_risk_patients_count || 0) + '</strong></div></div>' +
      '<div class="col-6 col-md-3"><div class="border rounded p-2 text-center"><div class="small text-muted">Credits còn</div><strong>' + (usage.remaining_credits ?? '-') + '</strong></div></div>' +
      '</div>';
    return html;
  }

  function downloadFile(content, filename, mimeType) {
    var blob = new Blob([content], { type: mimeType });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function generatePdf(data) {
    if (!window.jspdf || !window.jspdf.jsPDF) return null;
    var jsPDF = window.jspdf.jsPDF;
    var doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    var y = 15;
    var lineH = 7;
    var pageW = doc.internal.pageSize.getWidth();

    function addText(str, fontSize, isBold) {
      doc.setFontSize(fontSize || 10);
      doc.setFont('helvetica', isBold ? 'bold' : 'normal');
      doc.text(str, 14, y);
      y += lineH;
    }
    function addTableRow(label, value) {
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      doc.text(String(label), 14, y);
      doc.text(String(value), 100, y);
      y += lineH;
    }

    addText('AURA - Thong ke phong kham', 14, true);
    addText((data.clinic_name || 'Clinic #' + data.clinic_id) + '  (ID: ' + data.clinic_id + ')', 11, false);
    y += 2;
    addText('Ngay xuat: ' + (data.export_date || '').replace(/T.*/, ''), 9, false);
    if (data.date_range && (data.date_range.start_date || data.date_range.end_date)) {
      addText('Khoang thoi gian: ' + (data.date_range.start_date || '') + ' - ' + (data.date_range.end_date || ''), 9, false);
    }
    y += 4;

    var info = data.clinic_info || {};
    addText('Thong tin phong kham', 11, true);
    addTableRow('Tong bac si', info.total_doctors ?? 0);
    addTableRow('Tong benh nhan', info.total_patients ?? 0);
    y += 3;

    var risk = data.risk_statistics || {};
    addText('Thong ke rui ro', 11, true);
    addTableRow('Tong phan tich AI', risk.total_analyses ?? 0);
    addTableRow('Thap', risk.risk_distribution && risk.risk_distribution.low !== undefined ? risk.risk_distribution.low : 0);
    addTableRow('Trung binh', risk.risk_distribution && risk.risk_distribution.medium !== undefined ? risk.risk_distribution.medium : 0);
    addTableRow('Cao', risk.risk_distribution && risk.risk_distribution.high !== undefined ? risk.risk_distribution.high : 0);
    addTableRow('Nghiem trong', risk.risk_distribution && risk.risk_distribution.critical !== undefined ? risk.risk_distribution.critical : 0);
    addTableRow('So benh nhan nguy co cao', risk.high_risk_patients_count ?? 0);
    y += 3;

    var usage = data.usage_statistics || {};
    addText('Su dung', 11, true);
    addTableRow('Tong anh tai len', usage.total_images_uploaded ?? 0);
    addTableRow('Tong phan tich', usage.total_analyses ?? 0);
    addTableRow('Goi dang ky hoat dong', usage.active_subscriptions ?? 0);
    addTableRow('Credits da dung', usage.credits_used ?? 0);
    addTableRow('Credits con lai', usage.remaining_credits ?? '-');
    y += 3;

    var reports = data.reports_statistics || {};
    addText('Bao cao', 11, true);
    addTableRow('Tong bao cao', reports.total_reports ?? 0);
    addTableRow('Benh nhan co bao cao', reports.unique_patients ?? 0);
    addTableRow('Bac si lap bao cao', reports.unique_doctors ?? 0);

    if (y > 270) doc.addPage();
    y += 5;
    doc.setFontSize(8);
    doc.text('Generated by AURA - Export thong ke', 14, y);
    return doc;
  }

  function load() {
    if (!clinicId) { showError('Bạn chưa được gán phòng khám.'); return; }
    showError('');
    var format = (exportFormat && exportFormat.value) || 'json';
    var startDate = startDateEl && startDateEl.value ? startDateEl.value : '';
    var endDate = endDateEl && endDateEl.value ? endDateEl.value : '';
    var options = { start_date: startDate || undefined, end_date: endDate || undefined };
    if (startDate && endDate && startDate > endDate) {
      showError('Từ ngày phải trước hoặc bằng Đến ngày.');
      return;
    }
    btnExport.disabled = true;
    previewContent.innerHTML = '<span class="text-muted">Đang tải...</span>';
    if (summaryCardsCard) summaryCardsCard.style.display = 'none';
    if (btnToggleRaw) btnToggleRaw.style.display = 'none';

    var apiFormat = format === 'pdf' ? 'json' : format;
    window.AuraAPI.exportClinicStatistics(clinicId, apiFormat, options)
      .then(function (data) {
        btnExport.disabled = false;
        var rawJson = typeof data === 'object' ? JSON.stringify(data, null, 2) : String(data);

        // Summary cards
        if (summaryCardsCard && summaryCards) {
          summaryCards.innerHTML = buildSummaryCards(data);
          summaryCardsCard.style.display = 'block';
        }
        if (previewTitle && data && data.clinic_name) previewTitle.textContent = 'Dữ liệu xuất: ' + data.clinic_name;

        // Preview: summary + collapsible raw
        var rawId = 'export-raw-' + Date.now();
        var rawPreview = (format === 'csv_data' && data.csv_format)
          ? data.csv_format.map(function (row) { return row.join(', '); }).join('\n')
          : rawJson;
        var rawBlock = '<div class="mt-3"><button type="button" class="btn btn-sm btn-outline-secondary mb-2" data-bs-toggle="collapse" data-bs-target="#' + rawId + '">Xem dữ liệu thô</button>' +
          '<div class="collapse" id="' + rawId + '"><pre class="mb-0 small bg-light p-2 rounded" style="max-height: 400px; overflow: auto;">' + rawPreview + '</pre></div></div>';
        previewContent.innerHTML = '<p class="text-success mb-2"><i class="bi bi-check-circle me-1"></i>Đã tải thống kê. File đã được tải xuống (hoặc sắp tải).</p>' + rawBlock;
        if (btnToggleRaw) {
          btnToggleRaw.style.display = 'inline-block';
          btnToggleRaw.onclick = function () {
            var col = document.getElementById(rawId);
            if (col) col.classList.toggle('show');
          };
        }

        // Trigger file download
        var baseName = 'thong-ke-phong-kham-' + clinicId + '-' + (data.export_date || new Date().toISOString().slice(0, 10)).replace(/[:T].*/, '');
        if (format === 'pdf') {
          var pdfDoc = generatePdf(data);
          if (pdfDoc) pdfDoc.save(baseName + '.pdf');
          else downloadFile(rawJson, baseName + '.json', 'application/json');
        } else if (format === 'csv_data' && data.csv_format && data.csv_format.length) {
          var csvLines = data.csv_format.map(function (row) {
            return row.map(function (cell) {
              var s = String(cell == null ? '' : cell);
              if (/[",\n\r]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
              return s;
            }).join(',');
          }).join('\r\n');
          var bom = '\uFEFF';
          downloadFile(bom + csvLines, baseName + '.csv', 'text/csv; charset=utf-8');
        } else {
          downloadFile(rawJson, baseName + '.json', 'application/json');
        }

        if (window.AuraAlert && window.AuraAlert.toast) window.AuraAlert.toast('Đã tải thống kê và tải file.', 'success');
      })
      .catch(function (err) {
        btnExport.disabled = false;
        previewContent.innerHTML = '<p class="text-danger mb-0">' + (err.message || 'Không tải được.') + '</p>';
        showError(err.message || 'Xuất thất bại.');
        if (summaryCardsCard) summaryCardsCard.style.display = 'none';
      });
  }

  if (btnExport) btnExport.addEventListener('click', load);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () {
    if (!clinicId) showError('Bạn chưa được gán phòng khám.');
  });
})();
