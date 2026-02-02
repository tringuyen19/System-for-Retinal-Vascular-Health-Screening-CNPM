/**
 * AURA - Doctor Performance & AI report (FR-21)
 * Uses:
 * - GET /api/doctors/:id/performance
 * - GET /api/doctor-reviews/doctor/:id
 * - GET /api/medical-reports/doctor/:id
 * - GET /api/ai-results (filtered by doctor on backend)
 */
(function () {
    'use strict';
  
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;
  
    var user = window.AuraAuth.getUser();
    var accountId = user && user.account_id;
  
    var pageError = document.getElementById('pageError');
    var perfScore = document.getElementById('perfScore');
    var statPatients = document.getElementById('statPatients');
    var statReviews = document.getElementById('statReviews');
    var statApprovalRate = document.getElementById('statApprovalRate');
    var statReports = document.getElementById('statReports');
    var reviewDistribution = document.getElementById('reviewDistribution');
    var aiReport = document.getElementById('aiReport');
    var recentReviews = document.getElementById('recentReviews');
    var recentReports = document.getElementById('recentReports');
  
    function showError(msg) {
      if (!pageError) return;
      pageError.textContent = msg || '';
      pageError.classList.toggle('d-none', !msg);
    }
  
    function setText(el, value) {
      if (el) el.textContent = (value != null ? value : '-');
    }
  
    function pct(val) {
      var n = parseFloat(val);
      return isNaN(n) ? '-' : n.toFixed(2) + '%';
    }
  
    function riskLabel(s) {
      var map = { low: 'Thấp', medium: 'Trung bình', high: 'Cao', critical: 'Rất cao' };
      return map[(s || '').toLowerCase()] || s || '-';
    }
  
    function badgeClassByRisk(s) {
      var map = { low: 'success', medium: 'info', high: 'warning', critical: 'danger' };
      return map[(s || '').toLowerCase()] || 'secondary';
    }
  
    function renderReviewDistribution(perf) {
      if (!reviewDistribution) return;
      var total = perf && perf.total_reviews != null ? perf.total_reviews : 0;
      var parts = [
        { key: 'approved_reviews', label: 'Đã duyệt', cls: 'success' },
        { key: 'rejected_reviews', label: 'Từ chối', cls: 'danger' },
        { key: 'needs_revision_reviews', label: 'Cần chỉnh sửa', cls: 'warning' },
        { key: 'pending_reviews', label: 'Chờ xử lý', cls: 'secondary' }
      ];
      if (!total) {
        reviewDistribution.innerHTML = '<p class="text-muted mb-0">Chưa có review nào.</p>';
        return;
      }
      var html = '';
      parts.forEach(function (p) {
        var v = (perf && perf[p.key]) || 0;
        var percent = total ? Math.round((v / total) * 100) : 0;
        html +=
          '<div class="mb-2">' +
          '<div class="d-flex justify-content-between small"><span>' + p.label + '</span><span>' + v + ' (' + percent + '%)</span></div>' +
          '<div class="progress" style="height:8px;"><div class="progress-bar bg-' + p.cls + '" style="width:' + percent + '%"></div></div>' +
          '</div>';
      });
      reviewDistribution.innerHTML = html;
    }
  
    function renderAiReport(resultsData) {
      if (!aiReport) return;
      var results = (resultsData && resultsData.results) || [];
      if (!results.length) {
        aiReport.innerHTML = '<p class="text-muted mb-0">Chưa có dữ liệu ai_results.</p>';
        return;
      }
      // Risk distribution + top diseases
      var riskCount = { low: 0, medium: 0, high: 0, critical: 0 };
      var diseaseCount = {};
      results.forEach(function (r) {
        var rl = (r.risk_level || '').toLowerCase();
        if (riskCount[rl] != null) riskCount[rl] += 1;
        var d = (r.disease_type || '').toLowerCase();
        if (d) diseaseCount[d] = (diseaseCount[d] || 0) + 1;
      });
      var total = results.length;
      var topDiseases = Object.keys(diseaseCount)
        .sort(function (a, b) { return diseaseCount[b] - diseaseCount[a]; })
        .slice(0, 5)
        .map(function (d) { return { name: d.replace(/_/g, ' '), count: diseaseCount[d] }; });
  
      var html = '<div class="mb-3"><div class="text-muted small mb-2">Phân phối rủi ro (' + total + ' kết quả)</div>';
      ['low', 'medium', 'high', 'critical'].forEach(function (lv) {
        var v = riskCount[lv] || 0;
        var percent = total ? Math.round((v / total) * 100) : 0;
        html +=
          '<div class="mb-2">' +
          '<div class="d-flex justify-content-between small"><span>' + riskLabel(lv) + '</span><span>' + v + ' (' + percent + '%)</span></div>' +
          '<div class="progress" style="height:8px;"><div class="progress-bar bg-' + badgeClassByRisk(lv) + '" style="width:' + percent + '%\"></div></div>' +
          '</div>';
      });
      html += '</div>';
  
      html += '<div><div class="text-muted small mb-2">Top bệnh lý</div>';
      if (!topDiseases.length) {
        html += '<p class="text-muted mb-0">Chưa có thống kê bệnh lý.</p>';
      } else {
        html += '<ul class="list-group list-group-flush">';
        topDiseases.forEach(function (d) {
          html += '<li class="list-group-item d-flex justify-content-between align-items-center px-0">' +
            '<span>' + d.name + '</span><span class="badge bg-secondary rounded-pill">' + d.count + '</span></li>';
        });
        html += '</ul>';
      }
      html += '</div>';
  
      aiReport.innerHTML = html;
    }
  
    function renderRecentReviews(reviewsData) {
      if (!recentReviews) return;
      var reviews = (reviewsData && reviewsData.reviews) || [];
      if (!reviews.length) {
        recentReviews.innerHTML = '<p class="text-muted mb-0">Chưa có review nào.</p>';
        return;
      }
      // sort by reviewed_at desc
      reviews.sort(function (a, b) {
        var da = a.reviewed_at ? new Date(a.reviewed_at).getTime() : 0;
        var db = b.reviewed_at ? new Date(b.reviewed_at).getTime() : 0;
        return db - da;
      });
      var html = '<div class="table-responsive"><table class="table table-sm table-hover align-middle mb-0">' +
        '<thead class="table-light"><tr><th>Review #</th><th>Phân tích #</th><th>Trạng thái</th><th>Thời gian</th></tr></thead><tbody>';
      reviews.slice(0, 8).forEach(function (r) {
        html += '<tr>' +
          '<td>' + (r.review_id || '-') + '</td>' +
          '<td>' + (r.analysis_id || '-') + '</td>' +
          '<td><span class="badge bg-' + (r.validation_status === 'approved' ? 'success' : r.validation_status === 'rejected' ? 'danger' : r.validation_status === 'needs_revision' ? 'warning' : 'secondary') + '">' + (r.validation_status || '-') + '</span></td>' +
          '<td class="text-muted small">' + (r.reviewed_at ? new Date(r.reviewed_at).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) : '-') + '</td>' +
          '</tr>';
      });
      html += '</tbody></table></div>';
      recentReviews.innerHTML = html;
    }
  
    function renderRecentReports(reportsData) {
      if (!recentReports) return;
      var reports = (reportsData && reportsData.reports) || [];
      if (!reports.length) {
        recentReports.innerHTML = '<p class="text-muted mb-0">Chưa có báo cáo y tế nào.</p>';
        return;
      }
      reports.sort(function (a, b) {
        var da = a.created_at ? new Date(a.created_at).getTime() : 0;
        var db = b.created_at ? new Date(b.created_at).getTime() : 0;
        return db - da;
      });
      var html = '<div class="table-responsive"><table class="table table-sm table-hover align-middle mb-0">' +
        '<thead class="table-light"><tr><th>Báo cáo #</th><th>Bệnh nhân #</th><th>Ngày tạo</th></tr></thead><tbody>';
      reports.slice(0, 8).forEach(function (r) {
        html += '<tr>' +
          '<td>' + (r.report_id || r.id || '-') + '</td>' +
          '<td>' + (r.patient_id || '-') + '</td>' +
          '<td class="text-muted small">' + (r.created_at ? new Date(r.created_at).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) : '-') + '</td>' +
          '</tr>';
      });
      html += '</tbody></table></div>';
      recentReports.innerHTML = html;
    }
  
    function load() {
      showError('');
      if (!accountId) {
        showError('Không tìm thấy thông tin tài khoản.');
        return;
      }
      setText(perfScore, '-');
      setText(statPatients, '-');
      setText(statReviews, '-');
      setText(statApprovalRate, '-');
      setText(statReports, '-');
      if (reviewDistribution) reviewDistribution.textContent = 'Đang tải...';
      if (aiReport) aiReport.textContent = 'Đang tải...';
      if (recentReviews) recentReviews.textContent = 'Đang tải...';
      if (recentReports) recentReports.textContent = 'Đang tải...';
  
      window.AuraAPI.getDoctorByAccount(accountId)
        .then(function (doctor) {
          if (!doctor || !doctor.doctor_id) throw new Error('Bạn chưa có hồ sơ bác sĩ.');
          var doctorId = doctor.doctor_id;
          return Promise.all([
            window.AuraAPI.getDoctorPerformance(doctorId),
            window.AuraAPI.getReviewsByDoctor(doctorId),
            window.AuraAPI.getReportsByDoctor(doctorId),
            window.AuraAPI.getAllResults()
          ]);
        })
        .then(function (arr) {
          var perf = arr[0];
          var reviewsData = arr[1];
          var reportsData = arr[2];
          var resultsData = arr[3];
  
          setText(perfScore, (perf && perf.performance_score != null) ? perf.performance_score : '-');
          setText(statPatients, (perf && perf.unique_patients != null) ? perf.unique_patients : '-');
          setText(statReviews, (perf && perf.total_reviews != null) ? perf.total_reviews : '-');
          setText(statApprovalRate, (perf && perf.approval_rate != null) ? pct(perf.approval_rate) : '-');
          setText(statReports, (perf && perf.total_reports != null) ? perf.total_reports : ((reportsData && reportsData.count != null) ? reportsData.count : ((reportsData && reportsData.reports) ? reportsData.reports.length : '-')));
  
          renderReviewDistribution(perf);
          renderAiReport(resultsData);
          renderRecentReviews(reviewsData);
          renderRecentReports(reportsData);
        })
        .catch(function (err) {
          showError(err.message || 'Tải dữ liệu thất bại.');
        });
    }
  
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', load);
    } else {
      load();
    }
  })();
  
  