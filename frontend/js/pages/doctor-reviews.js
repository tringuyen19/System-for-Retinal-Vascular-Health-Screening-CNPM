/**
 * AURA - Doctor Reviews page
 * Pending analyses list (create review: approved/rejected/needs_revision), my reviews list
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var doctorId = null;

  var pageError = document.getElementById('pageError');
  var pendingLoading = document.getElementById('pendingLoading');
  var pendingContent = document.getElementById('pendingContent');
  var pendingBody = document.getElementById('pendingBody');
  var pendingEmpty = document.getElementById('pendingEmpty');
  var pendingBadge = document.getElementById('pendingBadge');
  var doneLoading = document.getElementById('doneLoading');
  var doneContent = document.getElementById('doneContent');
  var doneBody = document.getElementById('doneBody');
  var doneEmpty = document.getElementById('doneEmpty');
  var reviewModal = document.getElementById('reviewModal');
  var reviewModalAnalysisId = document.getElementById('reviewModalAnalysisId');
  var reviewAnalysisId = document.getElementById('reviewAnalysisId');
  var reviewStatus = document.getElementById('reviewStatus');
  var reviewComment = document.getElementById('reviewComment');
  var reviewAiAccuracyFeedback = document.getElementById('reviewAiAccuracyFeedback');
  var btnSubmitReview = document.getElementById('btnSubmitReview');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function setPendingBadge(n) {
    if (pendingBadge) pendingBadge.textContent = n != null ? n : '0';
  }

  function loadDoctorThen(cb) {
    if (doctorId) {
      if (cb) cb();
      return Promise.resolve();
    }
    if (!accountId) {
      showError('Không tìm thấy tài khoản.');
      return Promise.reject(new Error('No account'));
    }
    return window.AuraAPI.getDoctorByAccount(accountId)
      .then(function (doctor) {
        if (!doctor || !doctor.doctor_id) {
          showError('Bạn chưa có hồ sơ bác sĩ. Vui lòng cập nhật Hồ sơ.');
          return Promise.reject(new Error('No doctor profile'));
        }
        doctorId = doctor.doctor_id;
        if (cb) cb();
      });
  }

  function validationStatusLabel(s) {
    var map = { pending: 'Chờ duyệt', rejected: 'Từ chối', needs_revision: 'Cần chỉnh sửa', approved: 'Đã duyệt' };
    return map[s] || s || '-';
  }
  function validationStatusBadgeClass(s) {
    var map = { pending: 'secondary', rejected: 'danger', needs_revision: 'warning', approved: 'success' };
    return map[s] || 'secondary';
  }

  function loadPending() {
    pendingLoading.classList.remove('d-none');
    pendingContent.classList.add('d-none');
    pendingEmpty.classList.add('d-none');
    window.AuraAPI.getPendingReviews()
      .then(function (data) {
        pendingLoading.classList.add('d-none');
        // Support both { count, pending_analyses, need_revision_reviews } and { data: { ... } }
        var payload = (data && data.data !== undefined) ? data.data : (data || {});
        var pendingList = (payload.pending_analyses && Array.isArray(payload.pending_analyses)) ? payload.pending_analyses : [];
        var needRevListRaw = (payload.need_revision_reviews && Array.isArray(payload.need_revision_reviews)) ? payload.need_revision_reviews : [];
        // Chỉ hiển thị bên "Cần duyệt": chưa approved (pending, rejected, needs_revision). Loại bỏ approved.
        var needRevList = needRevListRaw.filter(function (r) {
          return (r.validation_status || '').toLowerCase() !== 'approved';
        });
        var totalItems = pendingList.length + needRevList.length;
        var count = totalItems;
        setPendingBadge(count);
        if (totalItems === 0) {
          pendingEmpty.classList.remove('d-none');
          pendingContent.classList.add('d-none');
          pendingEmpty.textContent = 'Không có kết quả AI nào chờ duyệt.';
          return;
        }
        pendingContent.classList.remove('d-none');
        pendingEmpty.classList.add('d-none');
        var html = '';
        pendingList.forEach(function (a) {
          var completed = a.completed_at ? new Date(a.completed_at).toLocaleDateString('vi-VN') : '-';
          html += '<tr data-analysis-id="' + (a.analysis_id || a.id) + '">' +
            '<td>' + (a.analysis_id || a.id) + '</td>' +
            '<td>' + (a.image_id != null ? a.image_id : '-') + '</td>' +
            '<td><span class="badge bg-secondary">Chưa duyệt</span></td>' +
            '<td>' + completed + '</td>' +
            '<td><button type="button" class="btn btn-sm btn-primary btn-review" data-analysis-id="' + (a.analysis_id || a.id) + '">Duyệt</button></td>' +
            '</tr>';
        });
        needRevList.forEach(function (r) {
          var dateStr = (r.reviewed_at || r.completed_at) ? new Date(r.reviewed_at || r.completed_at).toLocaleDateString('vi-VN') : '-';
          var badgeClass = validationStatusBadgeClass(r.validation_status);
          html += '<tr data-analysis-id="' + (r.analysis_id || r.id) + '">' +
            '<td>' + (r.analysis_id || r.id) + '</td>' +
            '<td>' + (r.image_id != null ? r.image_id : '-') + '</td>' +
            '<td><span class="badge bg-' + badgeClass + '">' + validationStatusLabel(r.validation_status) + '</span></td>' +
            '<td>' + dateStr + '</td>' +
            '<td><button type="button" class="btn btn-sm btn-primary btn-review" data-analysis-id="' + (r.analysis_id || r.id) + '">Duyệt</button></td>' +
            '</tr>';
        });
        if (pendingBody) pendingBody.innerHTML = html;
        if (pendingBody) pendingBody.querySelectorAll('.btn-review').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var id = btn.getAttribute('data-analysis-id');
            if (id) openReviewModal(parseInt(id, 10));
          });
        });
      })
      .catch(function (err) {
        pendingLoading.classList.add('d-none');
        pendingContent.classList.add('d-none');
        pendingEmpty.classList.remove('d-none');
        pendingEmpty.textContent = err.message || 'Không tải được danh sách.';
        setPendingBadge(0);
        showError(err.message || 'Tải danh sách chờ duyệt thất bại.');
      });
  }

  function loadDone() {
    if (!doctorId) return;
    doneLoading.classList.remove('d-none');
    doneContent.classList.add('d-none');
    doneEmpty.classList.add('d-none');
    window.AuraAPI.getReviewsByDoctor(doctorId)
      .then(function (data) {
        doneLoading.classList.add('d-none');
        // Hỗ trợ response bọc trong data (data.data)
        var payload = (data && data.data !== undefined) ? data.data : (data || {});
        var allReviews = (payload.reviews && Array.isArray(payload.reviews)) ? payload.reviews : [];
        // Tab "Đã duyệt" chỉ hiển thị review đã approved; còn lại (rejected, needs_revision, pending) ở "Cần duyệt"
        var list = allReviews.filter(function (r) {
          return (r.validation_status || '').toLowerCase() === 'approved';
        });
        if (!list.length) {
          doneEmpty.classList.remove('d-none');
          doneContent.classList.add('d-none');
          doneEmpty.textContent = 'Chưa có review nào đã duyệt (approved).';
          return;
        }
        doneContent.classList.remove('d-none');
        doneEmpty.classList.add('d-none');
        var html = '';
        list.forEach(function (r) {
          var reviewedAt = (r.reviewed_at) ? new Date(r.reviewed_at).toLocaleString('vi-VN') : '-';
          html += '<tr>' +
            '<td>' + (r.review_id || r.id) + '</td>' +
            '<td>' + (r.analysis_id || '-') + '</td>' +
            '<td><span class="badge bg-success">Đã duyệt</span></td>' +
            '<td>' + reviewedAt + '</td>' +
            '</tr>';
        });
        if (doneBody) doneBody.innerHTML = html;
      })
      .catch(function (err) {
        doneLoading.classList.add('d-none');
        doneContent.classList.add('d-none');
        doneEmpty.classList.remove('d-none');
        doneEmpty.textContent = err.message || 'Không tải được danh sách.';
      });
  }

  function openReviewModal(analysisId) {
    if (!analysisId || !doctorId) return;
    reviewAnalysisId.value = analysisId;
    reviewModalAnalysisId.textContent = '#' + analysisId;
    reviewStatus.value = 'approved';
    reviewComment.value = '';
    window.AuraAPI.getReviewByAnalysis(analysisId).then(function (r) {
      if (r && r.validation_status) {
        reviewStatus.value = r.validation_status;
        if (r.comment) reviewComment.value = r.comment;
      }
    }).catch(function () {});
    var modal = bootstrap.Modal.getOrCreateInstance(reviewModal);
    modal.show();
  }

  function submitReview() {
    var analysisId = parseInt(reviewAnalysisId.value, 10);
    var status = reviewStatus.value;
    var comment = (reviewComment && reviewComment.value) ? reviewComment.value.trim() : null;
    var aiAccuracyFeedback = (reviewAiAccuracyFeedback && reviewAiAccuracyFeedback.value) ? reviewAiAccuracyFeedback.value.trim() : null;
    if (!analysisId || !doctorId) return;
    if (!status) status = 'approved';
    btnSubmitReview.disabled = true;
    var payload = {
      analysis_id: analysisId,
      doctor_id: doctorId,
      validation_status: status,
      comment: comment || undefined
    };
    if (aiAccuracyFeedback) payload.ai_accuracy_feedback = aiAccuracyFeedback;
    window.AuraAPI.createDoctorReview(payload)
      .then(function () {
        if (window.AuraAlert && window.AuraAlert.toast) {
          window.AuraAlert.toast('Đã gửi đánh giá.', 'success');
        } else {
          alert('Đã gửi đánh giá.');
        }
        bootstrap.Modal.getInstance(reviewModal).hide();
        loadPending();
        loadDone();
      })
      .catch(function (err) {
        showError(err.message || 'Gửi đánh giá thất bại.');
        if (window.AuraAlert && window.AuraAlert.toast) {
          window.AuraAlert.toast(err.message || 'Gửi thất bại.', 'danger');
        }
      })
      .finally(function () {
        btnSubmitReview.disabled = false;
      });
  }

  if (btnSubmitReview) {
    btnSubmitReview.addEventListener('click', submitReview);
  }

  document.getElementById('done-tab').addEventListener('shown.bs.tab', function () {
    loadDoctorThen(loadDone);
  });

  function init() {
    loadDoctorThen(function () {
      loadPending();
      var params = new URLSearchParams(window.location.search);
      var analysisIdParam = params.get('analysis_id');
      if (analysisIdParam) {
        var aid = parseInt(analysisIdParam, 10);
        if (!isNaN(aid)) {
          setTimeout(function () { openReviewModal(aid); }, 300);
        }
      }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
