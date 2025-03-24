document.addEventListener("DOMContentLoaded", function() {
    // Переключение темной темы
    const darkModeToggle = document.getElementById("darkMode");
    if (darkModeToggle) {
        darkModeToggle.checked = localStorage.getItem("darkMode") === "true";
        document.body.classList.toggle("dark-mode", darkModeToggle.checked);
        
        darkModeToggle.addEventListener("change", function() {
            localStorage.setItem("darkMode", darkModeToggle.checked);
            document.body.classList.toggle("dark-mode", darkModeToggle.checked);
        });
    }

    // Уведомления о новых сообщениях (API)
    async function checkNotifications() {
        try {
            let response = await fetch("/api/notifications");
            let notifications = await response.json();
            if (notifications.length > 0) {
                document.getElementById("notificationBell").classList.add("new-notification");
            }
        } catch (error) {
            console.error("Ошибка загрузки уведомлений:", error);
        }
    }

    setInterval(checkNotifications, 5000);
});

document.addEventListener("DOMContentLoaded", function() {
    const avatarInput = document.getElementById("avatarInput");
    const avatarImage = document.getElementById("avatarImage");

    if (avatarInput) {
        avatarInput.addEventListener("change", function() {
            let formData = new FormData();
            formData.append("avatar", avatarInput.files[0]);

            fetch("/api/upload_avatar", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    avatarImage.src = data.avatar_url + "?t=" + new Date().getTime(); // Добавляем timestamp, чтобы избежать кэширования
                } else {
                    alert("Ошибка загрузки аватара: " + data.error);
                }
            })
            .catch(error => console.error("Ошибка загрузки:", error));
        });
    }
});
