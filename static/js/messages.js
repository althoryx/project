document.addEventListener("DOMContentLoaded", function() {
    const chatList = document.getElementById("chat-list");
    const messageInput = document.getElementById("message");
    const sendMessageButton = document.getElementById("sendMessage");

    async function loadMessages() {
        try {
            let response = await fetch("/api/messages");
            if (!response.ok) throw new Error("Ошибка загрузки: " + response.statusText);
            
            let messages = await response.json();
            chatList.innerHTML = "";
            messages.forEach(msg => {
                let li = document.createElement("li");
                li.textContent = msg.content;
                chatList.appendChild(li);
            });
        } catch (error) {
            console.error("Ошибка загрузки сообщений:", error);
        }
    }

    sendMessageButton.addEventListener("click", async function() {
        let message = messageInput.value.trim();
        if (message) {
            try {
                let response = await fetch("/api/messages", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ content: message })
                });

                if (!response.ok) throw new Error("Ошибка отправки: " + response.statusText);

                messageInput.value = "";
                loadMessages();
            } catch (error) {
                console.error("Ошибка отправки сообщения:", error);
            }
        }
    });

    loadMessages();
    
    setInterval(loadMessages, 5000);
});
