document.addEventListener("DOMContentLoaded", function() {
    const chatList = document.getElementById("chat-list");
    const messageInput = document.getElementById("message");
    const sendMessageButton = document.getElementById("sendMessage");

    function loadMessages() {
        const messages = JSON.parse(localStorage.getItem("messages")) || [];
        chatList.innerHTML = "";
        messages.forEach(msg => {
            let li = document.createElement("li");
            li.textContent = msg;
            chatList.appendChild(li);
        });
    }

    sendMessageButton.addEventListener("click", function() {
        let message = messageInput.value.trim();
        if (message) {
            let messages = JSON.parse(localStorage.getItem("messages")) || [];
            messages.push(message);
            localStorage.setItem("messages", JSON.stringify(messages));
            messageInput.value = "";
            loadMessages();
        }
    });

    loadMessages();
});
