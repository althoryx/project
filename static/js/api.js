document.addEventListener("DOMContentLoaded", function() {
    async function searchUsers(query) {
        try {
            let response = await fetch(`/api/users?query=${query}`);
            let users = await response.json();
            return users;
        } catch (error) {
            console.error("Ошибка загрузки пользователей:", error);
            return [];
        }
    }

    async function loadMessages() {
        try {
            let response = await fetch("/api/messages");
            let messages = await response.json();
            return messages;
        } catch (error) {
            console.error("Ошибка загрузки сообщений:", error);
            return [];
        }
    }

    async function loadNotifications() {
        try {
            let response = await fetch("/api/notifications");
            let notifications = await response.json();
            return notifications;
        } catch (error) {
            console.error("Ошибка загрузки уведомлений:", error);
            return [];
        }
    }

    const searchInput = document.getElementById("searchQuery");
    const searchButton = document.getElementById("searchButton");
    const searchResults = document.getElementById("searchResults");

    if (searchButton) {
        searchButton.addEventListener("click", async function() {
            let query = searchInput.value.trim();
            if (query) {
                let users = await searchUsers(query);
                searchResults.innerHTML = "";
                if (users.length > 0) {
                    users.forEach(user => {
                        let li = document.createElement("li");
                        li.textContent = user.username;
                        searchResults.appendChild(li);
                    });
                } else {
                    searchResults.innerHTML = "Пользователь не найден";
                }
            }
        });
    }
});