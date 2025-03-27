function appendMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.innerHTML = `<p>${message}</p>`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const question = userInput.value.trim();

    if (question === "") {
        return;
    }

    appendMessage('user', question);
    userInput.value = '';

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            appendMessage('bot', `Error: ${data.error}`);
        } else {
            appendMessage('bot', data.answer);
        }
    })
    .catch(error => {
        appendMessage('bot', `Error: ${error.message}`);
    });
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}