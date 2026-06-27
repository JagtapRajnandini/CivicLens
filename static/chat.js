function initChat(reportId, chatUrl) {
  var messagesEl = document.getElementById('chatMessages');
  var inputEl = document.getElementById('chatInput');
  var sendBtn = document.getElementById('chatSend');
  var typingEl = document.getElementById('chatTyping');

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function appendMessage(role, content) {
    var div = document.createElement('div');
    div.className = 'chat-msg ' + role;
    var bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    bubble.textContent = content;
    div.appendChild(bubble);
    messagesEl.appendChild(div);
    scrollToBottom();
  }

  function sendMessage() {
    var message = inputEl.value.trim();
    if (!message) return;

    appendMessage('user', message);
    inputEl.value = '';
    sendBtn.disabled = true;
    typingEl.style.display = 'block';
    scrollToBottom();

    fetch(chatUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: message }),
    })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        typingEl.style.display = 'none';
        sendBtn.disabled = false;
        if (data.response) {
          appendMessage('assistant', data.response);
        } else if (data.error) {
          appendMessage('assistant', 'Sorry, something went wrong. Please try again.');
        }
      })
      .catch(function() {
        typingEl.style.display = 'none';
        sendBtn.disabled = false;
        appendMessage('assistant', 'Connection error. Please refresh and try again.');
      });
  }

  sendBtn.addEventListener('click', sendMessage);
  inputEl.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  scrollToBottom();
}