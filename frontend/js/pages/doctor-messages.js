/**
 * AURA - Doctor Messages (FR-20)
 *
 * Luồng:
 * 1. Vào Tin nhắn → loadDoctor() → GET /api/doctors/account/:accountId (lấy doctor_id)
 * 2. loadConversations() → GET /api/conversations/doctor/:doctorId (danh sách hội thoại + patient_name)
 * 3. Chọn hội thoại → selectConversation() → GET /api/messages/conversation/:id (tin nhắn)
 * 4. Gửi tin → POST /api/messages { conversation_id, sender_type: 'doctor', sender_name, content }
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
  var btnRefreshConversations = document.getElementById('btnRefreshConversations');

  function showError(msg) {
    if (!pageError) return;
    pageError.textContent = msg || '';
    pageError.classList.toggle('d-none', !msg);
  }

  /** Lấy doctor_id từ API, cache vào doctorId/doctorName. Trả về Promise. */
  function loadDoctor() {
    if (doctorId) return Promise.resolve();
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
      });
  }

  /** Chuẩn hóa response GET /api/conversations/doctor/:id → { list, count, doctor_id } */
  function parseConversationsResponse(response) {
    if (!response) response = {};
    var payload = response.data != null ? response.data : response;
    if (!payload) payload = {};
    var list = payload.conversations || payload.Conversations || [];
    if (!Array.isArray(list)) list = [];
    var count = payload.count != null ? payload.count : list.length;
    var docId = payload.doctor_id != null ? payload.doctor_id : (doctorId || '');
    return { list: list, count: count, doctor_id: docId };
  }

  /** Tải danh sách hội thoại của bác sĩ (có patient_name từ backend). */
  function loadConversations() {
    if (!doctorId) return Promise.resolve();
    conversationsLoading.classList.remove('d-none');
    conversationsList.classList.add('d-none');
    if (conversationsEmpty) conversationsEmpty.classList.add('d-none');

    return window.AuraAPI.getConversationsByDoctor(doctorId, false)
      .then(function (response) {
        conversationsLoading.classList.add('d-none');
        var parsed = parseConversationsResponse(response);
        var list = parsed.list;
        var count = parsed.count;
        var docIdLabel = parsed.doctor_id !== '' ? ' (BS #' + parsed.doctor_id + ')' : '';

        // Luôn hiển thị khu vực danh sách (list / trống / lỗi)
        conversationsList.classList.remove('d-none');

        if (!list.length) {
          conversationsList.innerHTML =
            '<div class="list-group-item text-muted text-center py-4">' +
            'Chưa có cuộc hội thoại nào' + docIdLabel + '.<br>' +
            '<small class="d-block mt-2">Bệnh nhân cần nhắn tin từ trang Tin nhắn của họ (sau khi bạn đã duyệt kết quả AI).</small>' +
            '</div>';
          return;
        }

        var html = '';
        list.forEach(function (c) {
          var cid = c.conversation_id || c.id;
          var pid = c.patient_id || '';
          var pname = (c.patient_name || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
          var label = pname ? ('Bệnh nhân: ' + pname) : ('Hội thoại #' + cid + (pid ? ' (BN #' + pid + ')' : ''));
          html += '<a href="#" class="list-group-item list-group-item-action conversation-item" data-id="' + cid + '" data-patient-id="' + pid + '" data-patient-name="' + pname + '">' + label + '</a>';
        });
        conversationsList.innerHTML = html;
        conversationsList.querySelectorAll('.conversation-item').forEach(function (el) {
          el.addEventListener('click', function (e) {
            e.preventDefault();
            var id = el.getAttribute('data-id');
            var pname = el.getAttribute('data-patient-name') || '';
            var displayName = pname ? ('Bệnh nhân: ' + pname) : ('Hội thoại #' + id);
            if (id) selectConversation(parseInt(id, 10), displayName);
          });
        });
      })
      .catch(function (err) {
        conversationsLoading.classList.add('d-none');
        conversationsList.classList.remove('d-none');
        conversationsList.innerHTML =
          '<div class="list-group-item text-danger text-center py-4">' +
          (err.message || 'Không tải được danh sách hội thoại.') +
          '</div>';
        showError(err.message || 'Tải hội thoại thất bại.');
      });
  }

  /** Chọn một hội thoại: đặt tiêu đề, tải tin nhắn, bật form gửi. */
  function selectConversation(conversationId, displayName) {
    currentConversationId.value = conversationId;
    chatTitle.textContent = displayName || ('Hội thoại #' + conversationId);
    messagesPlaceholder.classList.add('d-none');
    messagesList.classList.remove('d-none');
    messageFormWrap.classList.remove('d-none');
    messagesList.innerHTML = '<div class="text-center py-3">Đang tải tin nhắn...</div>';

    window.AuraAPI.getMessagesByConversation(conversationId)
      .then(function (data) {
        var list = (data && data.messages) ? data.messages : [];
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

    if (conversationsList) {
      conversationsList.querySelectorAll('.conversation-item').forEach(function (el) {
        el.classList.toggle('active', parseInt(el.getAttribute('data-id'), 10) === conversationId);
      });
    }
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
        var displayName = chatTitle ? chatTitle.textContent : '';
        selectConversation(cid, displayName);
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

  if (messageForm) messageForm.addEventListener('submit', sendMessage);

  function doRefresh() {
    showError('');
    doctorId = null;
    conversationsLoading.classList.remove('d-none');
    conversationsList.classList.add('d-none');
    if (conversationsEmpty) conversationsEmpty.classList.add('d-none');
    loadDoctor()
      .then(function () { return loadConversations(); })
      .catch(function () { conversationsLoading.classList.add('d-none'); });
  }

  if (btnRefreshConversations) {
    btnRefreshConversations.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      doRefresh();
    });
  }

  // Khởi tạo: load doctor rồi mới load danh sách hội thoại
  loadDoctor()
    .then(function () { return loadConversations(); })
    .catch(function () { if (conversationsLoading) conversationsLoading.classList.add('d-none'); });
})();
