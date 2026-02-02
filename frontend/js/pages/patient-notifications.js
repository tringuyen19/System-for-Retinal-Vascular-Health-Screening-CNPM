/**
 * AURA - Patient Notifications (FR-5, FR-9)
 * Hiển thị thông báo: khuyến nghị/cảnh báo sức khỏe tự động, kết quả phân tích, thông báo hệ thống.
 */
(function () {
    'use strict';
  
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Patient')) return;
  
    var user = window.AuraAuth.getUser();
    var accountId = user && user.account_id;
  
    var notificationsError = document.getElementById('notificationsError');
    var notificationsLoading = document.getElementById('notificationsLoading');
    var notificationsList = document.getElementById('notificationsList');
    var notificationsEmpty = document.getElementById('notificationsEmpty');
    var notificationsCards = document.getElementById('notificationsCards');
  
    function showError(msg) {
      if (!notificationsError) return;
      notificationsError.textContent = msg || '';
      notificationsError.classList.toggle('d-none', !msg);
    }
  
    function typeLabel(type) {
      if (!type) return 'Thông báo';
      var map = {
        health_recommendation: 'Khuyến nghị sức khỏe',
        high_risk_alert: 'Cảnh báo nguy cơ cao',
        ai_result_ready: 'Kết quả phân tích'
      };
      return map[type] || type;
    }
  
    function typeIcon(type) {
      if (!type) return 'bi-bell';
      if (type === 'health_recommendation') return 'bi-heart-pulse';
      if (type === 'high_risk_alert') return 'bi-exclamation-triangle';
      if (type === 'ai_result_ready') return 'bi-graph-up';
      return 'bi-bell';
    }
  
    function formatDate(s) {
      if (!s) return '';
      try {
        var d = new Date(s);
        return isNaN(d.getTime()) ? s : d.toLocaleString('vi-VN');
      } catch (e) { return s; }
    }
  
    function load() {
      showError('');
      if (!accountId) {
        showError('Không tìm thấy thông tin tài khoản.');
        if (notificationsLoading) notificationsLoading.classList.add('d-none');
        if (notificationsList) notificationsList.classList.remove('d-none');
        if (notificationsEmpty) notificationsEmpty.classList.remove('d-none');
        return;
      }
      if (notificationsLoading) notificationsLoading.classList.remove('d-none');
      if (notificationsList) notificationsList.classList.add('d-none');
  
      window.AuraAPI.getNotificationsByAccount(accountId)
        .then(function (data) {
          if (notificationsLoading) notificationsLoading.classList.add('d-none');
          if (!notificationsList) return;
          notificationsList.classList.remove('d-none');
          var list = (data && data.notifications) || [];
          if (!list.length) {
            if (notificationsEmpty) notificationsEmpty.classList.remove('d-none');
            if (notificationsCards) notificationsCards.innerHTML = '';
            return;
          }
          if (notificationsEmpty) notificationsEmpty.classList.add('d-none');
          if (notificationsCards) {
            notificationsCards.innerHTML = list.map(function (n) {
              var type = n.notification_type || '';
              var content = (n.content || '').replace(/\n/g, '<br>');
              var isRead = n.is_read;
              var cardClass = isRead ? 'border' : 'border-primary border-2';
              return '<div class="card border-0 shadow-sm mb-3 ' + cardClass + '">' +
                '<div class="card-body">' +
                '<div class="d-flex justify-content-between align-items-start mb-2">' +
                '<span class="badge bg-secondary me-2">' + typeLabel(type) + '</span>' +
                '<small class="text-muted">' + formatDate(n.created_at) + '</small>' +
                '</div>' +
                '<div class="notification-content">' + content + '</div>' +
                '</div></div>';
            }).join('');
          }
        })
        .catch(function (err) {
          if (notificationsLoading) notificationsLoading.classList.add('d-none');
          if (notificationsList) notificationsList.classList.remove('d-none');
          if (notificationsEmpty) notificationsEmpty.classList.add('d-none');
          if (notificationsCards) notificationsCards.innerHTML = '';
          showError(err.message || 'Không tải được thông báo.');
        });
    }
  
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', load);
    } else {
      load();
    }
  })();
  