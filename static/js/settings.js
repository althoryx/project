document.addEventListener("DOMContentLoaded", function() {
    const darkModeToggle = document.getElementById("darkMode");
    const notificationsToggle = document.getElementById("notifications");
    const saveButton = document.getElementById("saveSettings");
    const settingsMessage = document.getElementById("settingsMessage");
    const modal = document.getElementById("infoModal");
    const modalText = document.getElementById("modalText");
    const closeModal = document.getElementById("closeModal");

    // 🔹 Проверяем существование элементов перед работой с ними
    if (darkModeToggle) {
        darkModeToggle.checked = localStorage.getItem("darkMode") === "true";
        document.body.classList.toggle("dark-mode", darkModeToggle.checked);
    }
    if (notificationsToggle) {
        notificationsToggle.checked = localStorage.getItem("notifications") === "true";
    }

    // 🔹 Сохранение настроек (проверяем, существует ли кнопка)
    if (saveButton) {
        saveButton.addEventListener("click", function() {
            if (darkModeToggle) {
                localStorage.setItem("darkMode", darkModeToggle.checked);
                document.body.classList.toggle("dark-mode", darkModeToggle.checked);
            }
            if (notificationsToggle) {
                localStorage.setItem("notifications", notificationsToggle.checked);
            }

            if (settingsMessage) {
                settingsMessage.style.color = "green";
                settingsMessage.textContent = "Настройки сохранены!";
                settingsMessage.style.display = "block";

                // Скрытие сообщения через 3 секунды
                setTimeout(() => settingsMessage.style.display = "none", 3000);
            }
        });
    }

    // 🔹 Открытие модального окна
    if (modal && modalText) {
        document.querySelectorAll(".more-info-btn").forEach(button => {
            button.addEventListener("click", function() {
                modalText.textContent = this.getAttribute("data-info");
                modal.style.display = "block";
            });
        });
    }

    // 🔹 Закрытие модального окна
    if (closeModal) {
        closeModal.addEventListener("click", function() {
            modal.style.display = "none";
        });
    }

    // 🔹 Закрытие при клике вне окна
    if (modal) {
        window.addEventListener("click", function(event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });

        // 🔹 Закрытие по клавише "Escape"
        document.addEventListener("keydown", function(event) {
            if (event.key === "Escape") {
                modal.style.display = "none";
            }
        });
    }
});
