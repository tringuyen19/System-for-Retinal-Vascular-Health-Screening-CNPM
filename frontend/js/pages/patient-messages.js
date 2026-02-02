/**
 * AURA - Patient Messages (FR-10 / FR-20)
 * Tư vấn trực tuyến với bác sĩ: danh sách bác sĩ đã review, tạo/lấy conversation, gửi và xem tin nhắn
 */
(function () {
    'use strict';
  
    if (!window.AuraAuth || !window.AuraAuth.requireRole || !window.AuraAuth.requireRole('Patient')) return;
  
    var user = window.AuraAuth.getUser();
    var accountId = user && user.account_id;
    var patientId = null;
    var patientName = '';
  
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
  
    var conversationsByDoctorId = {}; // doctor_id -> { conversation_id, ... }
    var doctorsList = []; // { doctor_id, doctor_name }
  
    function showError(msg) {
      if (!pageError) return;
      pageError.textContent = msg || '';
      pageError.classList.toggle('d-none', !msg);
    }
  
    function loadPatient(cb) {
      if (patientId) {
        if (cb) cb();
        return Promise.resolve();
      }
      if (!accountId) {
        showError('Không tìm thấy tài khoản.');
        return Promise.reject(new Error('No account'));
      }
      return window.AuraAPI.getPatientByAccount(accountId)
        .then(function (patient) {
          if (!patient || !patient.patient_id) {
            showError('Bạn chưa có hồ sơ bệnh nhân. Vui lòng cập nhật Hồ sơ.');
            return Promise.reject(new Error('No patient profile'));
          }
          patientId = patient.patient_id;
          patientName = patient.patient_name || 'Bệnh nhân';
          if (cb) cb();
        });
    }
  
    function loadDoctorsAndConversations() {
      if (!patientId) return;
      conversationsLoading.classList.remove('d-none');
      if (conversationsList) conversationsList.classList.add('d-none');
      if (conversationsEmpty) conversationsEmpty.classList.add('d-none');
  
      Promise.all([
        window.AuraAPI.getDoctorsWhoReviewedPatient(patientId),
        window.AuraAPI.getConversationsByPatient(patientId, false)
      ])
        .then(function (results) {
          var doctorsData = results[0] || {};
          var convData = results[1] || {};
          doctorsList = (doctorsData.doctors) || [];
          var convs = (convData.conversations) || [];
          conversationsByDoctorId = {};
          convs.forEach(function (c) {
            conversationsByDoctorId[c.doctor_id] = c;
          });
  
          conversationsLoading.classList.add('d-none');
          if (!conversationsList) return;
  
          if (!doctorsList.length) {
            conversationsList.classList.remove('d-none');
            conversationsList.innerHTML = '<div class="list-group-item text-muted text-center py-4">Chưa có bác sĩ nào review kết quả của bạn. Sau khi bác sĩ duyệt kết quả phân tích, bạn có thể nhắn tin tại đây.</div>';
            if (conversationsEmpty) conversationsEmpty.classList.add('d-none');
            return;
          }
  
          if (conversationsEmpty) conversationsEmpty.classList.add('d-none');
          var html = '';
          doctorsList.forEach(function (doc) {
            var conv = conversationsByDoctorId[doc.doctor_id];
            var label = 'BS. ' + (doc.doctor_name || '#' + doc.doctor_id);
            if (conv) {
              html += '<a href="#" class="list-group-item list-group-item-action conversation-item" data-conversation-id="' + (conv.conversation_id || conv.id) + '" data-doctor-id="' + doc.doctor_id + '" data-doctor-name="' + (doc.doctor_name || '').replace(/"/g, '&quot;') + '">' + label + '</a>';
            } else {
              html += '<a href="#" class="list-group-item list-group-item-action conversation-item" data-doctor-id="' + doc.doctor_id + '" data-doctor-name="' + (doc.doctor_name || '').replace(/"/g, '&quot;') + '">' + label + ' <small class="text-muted">(Chưa có tin nhắn)</small></a>';
            }
          });
          conversationsList.innerHTML = html;
          conversationsList.classList.remove('d-none');
  
          conversationsList.querySelectorAll('.conversation-item').forEach(function (el) {
            el.addEventListener('click', function (e) {
              e.preventDefault();
              var cid = el.getAttribute('data-conversation-id');
              var did = el.getAttribute('data-doctor-id');
              var dname = el.getAttribute('data-doctor-name');
              var displayName = (dname ? 'BS. ' + dname : 'Bác sĩ #' + did);
              if (cid) {
                selectConversation(parseInt(cid, 10), displayName);
              } else if (did) {
                openOrCreateConversation(parseInt(did, 10), displayName);
              }
            });
          });
        })
        .catch(function (err) {
          conversationsLoading.classList.add('d-none');
          if (conversationsList) {
            conversationsList.classList.remove('d-none');
            conversationsList.innerHTML = '<div class="list-group-item text-danger text-center py-4">' + (err.message || 'Không tải được danh sách.') + '</div>';
          }
          showError(err.message || 'Tải thất bại.');
        });
    }
  
    function openOrCreateConversation(doctorId, doctorDisplayName) {
      var conv = conversationsByDoctorId[doctorId];
      if (conv) {
        selectConversation(conv.conversation_id || conv.id, doctorDisplayName);
        return;
      }
      if (!patientId) return;
      btnSend.disabled = true;
      messageFormWrap.classList.add('d-none');
      messagesPlaceholder.classList.remove('d-none');
      messagesList.classList.add('d-none');
      chatTitle.textContent = 'Đang tạo cuộc hội thoại...';
      window.AuraAPI.createConversation(patientId, doctorId)
        .then(function (data) {
          var c = (data && data.data) || data || {};
          var newCid = c.conversation_id || c.id;
          if (newCid) {
            conversationsByDoctorId[doctorId] = { conversation_id: newCid, doctor_id: doctorId };
            var itemEl = conversationsList && conversationsList.querySelector('.conversation-item[data-doctor-id="' + doctorId + '"]');
            if (itemEl) itemEl.setAttribute('data-conversation-id', newCid);
            selectConversation(newCid, doctorDisplayName);
          }
          chatTitle.textContent = doctorDisplayName || 'Bác sĩ';
        })
        .catch(function (err) {
          showError(err.message || 'Không tạo được cuộc hội thoại.');
          chatTitle.textContent = 'Chọn bác sĩ';
        })
        .finally(function () {
          btnSend.disabled = false;
        });
    }
  
    function selectConversation(conversationId, doctorDisplayName) {
      if (currentConversationId) currentConversationId.value = conversationId;
      if (chatTitle) chatTitle.textContent = doctorDisplayName || ('Hội thoại #' + conversationId);
      messagesPlaceholder.classList.add('d-none');
      messagesList.classList.remove('d-none');
      messageFormWrap.classList.remove('d-none');
      messagesList.innerHTML = '<div class="text-center py-3">Đang tải tin nhắn...</div>';
  
      window.AuraAPI.getMessagesByConversation(conversationId)
        .then(function (data) {
          var list = (data && data.messages) || [];
          if (!list.length) {
            messagesList.innerHTML = '<p class="text-muted text-center mb-0">Chưa có tin nhắn. Hãy gửi lời chào.</p>';
            messagesList.scrollTop = messagesList.scrollHeight;
            return;
          }
          var html = '';
          list.forEach(function (m) {
            var isPatient = (m.sender_type || '').toLowerCase() === 'patient';
            var align = isPatient ? 'end' : 'start';
            html += '<div class="d-flex justify-content-' + align + ' mb-2">' +
              '<div class="rounded px-3 py-2 ' + (isPatient ? 'bg-primary text-white' : 'bg-light') + '" style="max-width: 80%;">' +
              '<small class="d-block opacity-75">' + (m.sender_name || '').replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</small>' +
              '<span>' + (m.content || '').replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</span>' +
              '</div></div>';
          });
          messagesList.innerHTML = html;
          messagesList.scrollTop = messagesList.scrollHeight;
        })
        .catch(function (err) {
          messagesList.innerHTML = '<p class="text-danger text-center mb-0">' + (err.message || 'Không tải được tin nhắn.') + '</p>';
        });
  
      if (conversationsList) {
        conversationsList.querySelectorAll('.conversation-item').forEach(function (el) {
          var cid = el.getAttribute('data-conversation-id');
          el.classList.toggle('active', cid && parseInt(cid, 10) === conversationId);
        });
      }
    }
  
    function sendMessage(e) {
      e.preventDefault();
      var cid = currentConversationId && currentConversationId.value ? parseInt(currentConversationId.value, 10) : null;
      var content = messageContent && messageContent.value ? messageContent.value.trim() : '';
      if (!cid || !content) return;
      btnSend.disabled = true;
      window.AuraAPI.sendMessage({
        conversation_id: cid,
        sender_type: 'patient',
        sender_name: patientName,
        content: content,
        message_type: 'text'
      })
        .then(function () {
          messageContent.value = '';
          var docName = chatTitle ? chatTitle.textContent : '';
          selectConversation(cid, docName);
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
  
    loadPatient(function () {
      loadDoctorsAndConversations();
    });
  })();
  