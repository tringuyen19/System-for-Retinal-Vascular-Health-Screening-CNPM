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

  function loadPending() {
    pendingLoading.classList.remove('d-none');
    pendingContent.classList.add('d-none');
    pendingEmpty.classList.add('d-none');
    window.AuraAPI.getPendingReviews()
      .then(function (data) {
        pendingLoading.classList.add('d-none');
        var list = (data && data.pending_analyses) || [];
        var count = (data && data.count != null) ? data.count : list.length;
        setPendingBadge(count);
        if (!list.length) {
          pendingEmpty.classList.remove('d-none');
          pendingContent.classList.add('d-none');
          return;
        }
        pendingContent.classList.remove('d-none');
        pendingEmpty.classList.add('d-none');
        var html = '';
        list.forEach(function (a) {
          var completed = a.completed_at ? new Date(a.completed_at).toLocaleDateString('vi-VN') : '-';
          html += '<tr data-analysis-id="' + (a.analysis_id || a.id) + '">' +
            '<td>' + (a.analysis_id || a.id) + '</td>' +
            '<td>' + (a.image_id || '-') + '</td>' +
            '<td><span class="badge bg-secondary">' + (a.status || '-') + '</span></td>' +
            '<td>' + completed + '</td>' +
            '<td><button type="button" class="btn btn-sm btn-primary btn-review" data-analysis-id="' + (a.analysis_id || a.id) + '">Duyệt</button></td>' +
            '</tr>';
        });
        pendingBody.innerHTML = html;
        pendingBody.querySelectorAll('.btn-review').forEach(function (btn) {
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
        var list = (data && data.reviews) || [];
        if (!list.length) {
          doneEmpty.classList.remove('d-none');
          doneContent.classList.add('d-none');
          return;
        }
        doneContent.classList.remove('d-none');
        doneEmpty.classList.add('d-none');
        var html = '';
        list.forEach(function (r) {
          var reviewedAt = (r.reviewed_at) ? new Date(r.reviewed_at).toLocaleString('vi-VN') : '-';
          var statusClass = r.validation_status === 'approved' ? 'success' : (r.validation_status === 'rejected' ? 'danger' : 'warning');
          html += '<tr>' +
            '<td>' + (r.review_id || r.id) + '</td>' +
            '<td>' + (r.analysis_id || '-') + '</td>' +
            '<td><span class="badge bg-' + statusClass + '">' + (r.validation_status || '-') + '</span></td>' +
            '<td>' + reviewedAt + '</td>' +
            '</tr>';
        });
        doneBody.innerHTML = html;
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
    var modal = bootstrap.Modal.getOrCreateInstance(reviewModal);
    modal.show();
  }

  function submitReview() {
    var analysisId = parseInt(reviewAnalysisId.value, 10);
    var status = reviewStatus.value;
    var comment = (reviewComment && reviewComment.value) ? reviewComment.value.trim() : null;
    if (!analysisId || !doctorId) return;
    if (!status) status = 'approved';
    btnSubmitReview.disabled = true;
    window.AuraAPI.createDoctorReview({
      analysis_id: analysisId,
      doctor_id: doctorId,
      validation_status: status,
      comment: comment || undefined
    })
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
