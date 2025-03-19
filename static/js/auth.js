document.addEventListener("DOMContentLoaded", function() {
    // Функция для регистрации пользователя
    async function registerUser(username, email, password) {
        localStorage.setItem("username", username);
        localStorage.setItem("email", email);
        localStorage.setItem("password", password);
        alert("Регистрация успешна! Теперь войдите в аккаунт.");
        window.location.href = "/login";
    }

    // Функция для входа пользователя
    async function loginUser(username, password) {
        const storedUsername = localStorage.getItem("username");
        const storedPassword = localStorage.getItem("password");
        
        if (username === storedUsername && password === storedPassword) {
            alert("Вход выполнен успешно!");
            window.location.href = "/profile";
        } else {
            alert("Неверный логин или пароль.");
        }
    }

    // Обработчик формы регистрации
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", function(event) {
            event.preventDefault();
            const username = document.getElementById("username").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            registerUser(username, email, password);
        });
    }

    // Обработчик формы входа
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", function(event) {
            event.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            loginUser(username, password);
        });
    }
});