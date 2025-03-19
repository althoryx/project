document.addEventListener("DOMContentLoaded", function() {
    const darkModeToggle = document.getElementById("darkMode");
    const notificationsToggle = document.getElementById("notifications");
    const saveButton = document.getElementById("saveSettings");

    // Загрузка настроек из localStorage
    if (darkModeToggle) {
        darkModeToggle.checked = localStorage.getItem("darkMode") === "true";
        document.body.classList.toggle("dark-mode", darkModeToggle.checked);
    }
    if (notificationsToggle) {
        notificationsToggle.checked = localStorage.getItem("notifications") === "true";
    }

    // Сохранение настроек
    saveButton.addEventListener("click", function() {
        if (darkModeToggle) {
            localStorage.setItem("darkMode", darkModeToggle.checked);
            document.body.classList.toggle("dark-mode", darkModeToggle.checked);
        }
        if (notificationsToggle) {
            localStorage.setItem("notifications", notificationsToggle.checked);
        }
        alert("Настройки сохранены!");
    });
});