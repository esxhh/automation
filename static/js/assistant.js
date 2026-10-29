(function () {
  'use strict';

  document.querySelectorAll('.nav').forEach(function (nav) {
    var toggle = nav.querySelector('.nav-toggle');
    var links = nav.querySelector('.links');
    if (!toggle || !links) return;
    function closeNav() {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open navigation menu');
    }
    toggle.addEventListener('click', function () {
      var isOpen = toggle.getAttribute('aria-expanded') === 'true';
      nav.classList.toggle('is-open', !isOpen);
      toggle.setAttribute('aria-expanded', String(!isOpen));
      toggle.setAttribute('aria-label', isOpen ? 'Open navigation menu' : 'Close navigation menu');
    });
    links.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeNav();
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeNav();
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 800) closeNav();
    });
  });

  var widget = document.querySelector('.assistant-widget');
  if (!widget) return;

  var launcher = widget.querySelector('.assistant-launcher');
  var panel = widget.querySelector('.assistant-panel');
  var closeButton = widget.querySelector('.assistant-close');
  var messageList = widget.querySelector('.assistant-messages');
  var form = widget.querySelector('.assistant-form');
  var input = widget.querySelector('textarea');
  var sendButton = form.querySelector('button[type="submit"]');
  var history = [];
  var busy = false;

  function setOpen(open) {
    panel.hidden = !open;
    launcher.setAttribute('aria-expanded', String(open));
    if (open) input.focus();
    else launcher.focus();
  }

  function appendMessage(text, kind) {
    var message = document.createElement('article');
    message.className = 'assistant-message assistant-message-' + kind;
    message.textContent = text;
    messageList.appendChild(message);
    messageList.scrollTop = messageList.scrollHeight;
    return message;
  }

  function sendMessage(text) {
    var cleanText = text.trim();
    if (!cleanText || busy) return;

    busy = true;
    input.value = '';
    input.style.height = '';
    appendMessage(cleanText, 'user');
    history.push({ role: 'user', content: cleanText });
    var pending = appendMessage('Thinking...', 'bot assistant-message-pending');
    sendButton.disabled = true;
    input.disabled = true;

    fetch(widget.getAttribute('data-chat-endpoint'), {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': form.elements.csrfmiddlewaretoken.value,
        'X-Requested-With': 'fetch',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ messages: history.slice(-8) })
    }).then(function (response) {
      return response.json().catch(function () { return {}; }).then(function (data) {
        return { response: response, data: data };
      });
    }).then(function (result) {
      pending.remove();
      var reply = result.data.reply || 'I could not respond just now. Please contact the team through the consultation form.';
      appendMessage(reply, 'bot');
      if (result.response.ok) history.push({ role: 'assistant', content: reply });
    }).catch(function () {
      pending.remove();
      appendMessage('I could not connect just now. Please try again or contact the team through the consultation form.', 'bot');
    }).then(function () {
      busy = false;
      sendButton.disabled = false;
      input.disabled = false;
      input.focus();
    });
  }

  launcher.addEventListener('click', function () { setOpen(panel.hidden); });
  closeButton.addEventListener('click', function () { setOpen(false); });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !panel.hidden) setOpen(false);
  });
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    sendMessage(input.value);
  });
  input.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage(input.value);
    }
  });
  input.addEventListener('input', function () {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 100) + 'px';
  });
  widget.querySelectorAll('[data-prompt]').forEach(function (button) {
    button.addEventListener('click', function () { sendMessage(button.getAttribute('data-prompt')); });
  });
})();
