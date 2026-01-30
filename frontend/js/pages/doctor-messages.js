/**
 * AURA - Doctor Messages
 * List conversations (getConversationsByDoctor), load messages, send message (sender_type: doctor)
 */
(function () {
  'use strict';

  if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Doctor')) return;

  var user = window.AuraAuth.getUser();
  var accountId = user && user.account_id;
  var doctorId = null;
  var doctorName = '';

  var pageError = document.getElementById('pageError');
  var conversationsLoading = document.getElementById('conversationsLoading');
  var conversationsList = document.getElementById('conversationsList');
  var conversationsEmpty = document.getElementById('conversationsEmpty');
  var chatTitle = document.getElementById('chatTitle');
  var messagesPlaceholder = document.getElementById('messagesPlaceholder');
  var messagesList = document.getElementById('messagesList');
  var messageFormWrap = document.getElementById('messageFormWrap');
  var messageForm = document.getElementById('messageForm');
  var currentConversationId = document.getElementById('currentConversationId');
  var messageContent = document.getElementById('messageContent');
  var btnSend = document.getElementById('btnSend');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  function loadDoctor(cb) {
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
        doctorName = doctor.doctor_name || 'Bác sĩ';
        if (cb) cb();
      });
  }

  function loadConversations() {
    if (!doctorId) return;
    conversationsLoading.classList.remove('d-none');
    conversationsList.classList.add('d-none');
    conversationsEmpty.classList.add('d-none');
    window.AuraAPI.getConversationsByDoctor(doctorId, false)
      .then(function (data) {
        conversationsLoading.classList.add('d-none');
        var list = (data && data.conversations) || [];
        if (!list.length) {
          conversationsList.classList.remove('d-none');
          conversationsList.innerHTML = '<div class="list-group-item text-muted text-center py-4">Chưa có cuộc hội thoại nào.</div>';
          if (conversationsEmpty) conversationsEmpty.classList.add('d-none');
          return;
        }
        if (conversationsEmpty) conversationsEmpty.classList.add('d-none');
        var html = '';
        list.forEach(function (c) {
          var label = 'Hội thoại #' + (c.conversation_id || c.id);
          if (c.patient_id) label += ' (BN #' + c.patient_id + ')';
          html += '<a href="#" class="list-group-item list-group-item-action conversation-item" data-id="' + (c.conversation_id || c.id) + '" data-patient-id="' + (c.patient_id || '') + '">' + label + '</a>';
        });
        conversationsList.innerHTML = html;
        conversationsList.querySelectorAll('.conversation-item').forEach(function (el) {
          el.addEventListener('click', function (e) {
            e.preventDefault();
            var id = el.getAttribute('data-id');
            if (id) selectConversation(parseInt(id, 10));
          });
        });
      })
      .catch(function (err) {
        conversationsLoading.classList.add('d-none');
        conversationsList.classList.remove('d-none');
        conversationsList.innerHTML = '<div class="list-group-item text-danger text-center py-4">' + (err.message || 'Không tải được danh sách.') + '</div>';
        showError(err.message || 'Tải hội thoại thất bại.');
      });
  }

  function selectConversation(conversationId) {
    currentConversationId.value = conversationId;
    chatTitle.textContent = 'Hội thoại #' + conversationId;
    messagesPlaceholder.classList.add('d-none');
    messagesList.classList.remove('d-none');
    messageFormWrap.classList.remove('d-none');
    messagesList.innerHTML = '<div class="text-center py-3">Đang tải tin nhắn...</div>';
    window.AuraAPI.getMessagesByConversation(conversationId)
      .then(function (data) {
        var list = (data && data.messages) || [];
        if (!list.length) {
          messagesList.innerHTML = '<p class="text-muted text-center mb-0">Chưa có tin nhắn.</p>';
          return;
        }
        var html = '';
        list.forEach(function (m) {
          var isDoctor = (m.sender_type || '').toLowerCase() === 'doctor';
          var align = isDoctor ? 'end' : 'start';
          html += '<div class="d-flex justify-content-' + align + ' mb-2">' +
            '<div class="rounded px-3 py-2 ' + (isDoctor ? 'bg-primary text-white' : 'bg-light') + '" style="max-width: 80%;">' +
            '<small class="d-block opacity-75">' + (m.sender_name || '') + '</small>' +
            '<span>' + (m.content || '').replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</span>' +
            '</div></div>';
        });
        messagesList.innerHTML = html;
        messagesList.scrollTop = messagesList.scrollHeight;
      })
      .catch(function (err) {
        messagesList.innerHTML = '<p class="text-danger text-center mb-0">' + (err.message || 'Không tải được tin nhắn.') + '</p>';
      });
    conversationsList.querySelectorAll('.conversation-item').forEach(function (el) {
      el.classList.toggle('active', parseInt(el.getAttribute('data-id'), 10) === conversationId);
    });
  }

  function sendMessage(e) {
    e.preventDefault();
    var cid = currentConversationId.value ? parseInt(currentConversationId.value, 10) : null;
    var content = messageContent.value ? messageContent.value.trim() : '';
    if (!cid || !content) return;
    btnSend.disabled = true;
    window.AuraAPI.sendMessage({
      conversation_id: cid,
      sender_type: 'doctor',
      sender_name: doctorName,
      content: content
    })
      .then(function () {
        messageContent.value = '';
        selectConversation(cid);
      })
      .catch(function (err) {
        showError(err.message || 'Gửi tin nhắn thất bại.');
        if (window.AuraAlert && window.AuraAlert.toast) {
          window.AuraAlert.toast(err.message || 'Gửi thất bại.', 'danger');
        }
      })
      .finally(function () {
        btnSend.disabled = false;
      });
  }

  if (messageForm) {
    messageForm.addEventListener('submit', sendMessage);
  }

  loadDoctor(function () {
    loadConversations();
  });
})();
