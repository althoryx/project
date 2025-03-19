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

    // Уведомления о новых сообщениях (имитация)
    const notificationBell = document.getElementById("notificationBell");
    if (notificationBell) {
        setInterval(() => {
            let hasNew = Math.random() > 0.7;
            if (hasNew) {
                notificationBell.classList.add("new-notification");
            }
        }, 5000);
    }

    // Удаление классов уведомлений при клике
    if (notificationBell) {
        notificationBell.addEventListener("click", function() {
            this.classList.remove("new-notification");
        });
    }

    // Обработчик форм входа и регистрации (localStorage)
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", function(event) {
            event.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const storedUsername = localStorage.getItem("username");
            const storedPassword = localStorage.getItem("password");
            
            if (username === storedUsername && password === storedPassword) {
                alert("Вход выполнен успешно!");
                window.location.href = "/profile";
            } else {
                alert("Неверный логин или пароль.");
            }
        });
    }

    // Сохранение данных профиля
    const saveProfileButton = document.getElementById("saveProfile");
    if (saveProfileButton) {
        saveProfileButton.addEventListener("click", function() {
            localStorage.setItem("email", document.getElementById("email").value);
            localStorage.setItem("bio", document.getElementById("bio").value);
            alert("Данные профиля сохранены!");
        });
    }
});
