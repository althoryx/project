document.addEventListener("DOMContentLoaded", function() {
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");

    // Регистрация
    if (registerForm) {
        registerForm.addEventListener("submit", async function(event) {
            event.preventDefault();
            const username = document.getElementById("username").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const registerMessage = document.getElementById("registerMessage");

            registerMessage.style.display = "none";

            try {
                const response = await fetch("/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    registerMessage.style.color = "green";
                    registerMessage.textContent = "Регистрация успешна!";
                    registerMessage.style.display = "block";
                    setTimeout(() => { window.location.href = "/login"; }, 2000);
                } else {
                    registerMessage.style.color = "red";
                    registerMessage.textContent = data.error || "Ошибка регистрации";
                    registerMessage.style.display = "block";
                }
            } catch (error) {
                registerMessage.textContent = "Ошибка сети!";
                registerMessage.style.display = "block";
            }
        });
    }

    // Вход
    if (loginForm) {
        loginForm.addEventListener("submit", async function(event) {
            event.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const loginMessage = document.getElementById("loginMessage");

            loginMessage.style.display = "none";

            try {
                const response = await fetch("/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.href = "/profile";
                } else {
                    loginMessage.style.color = "red";
                    loginMessage.textContent = data.error || "Ошибка входа";
                    loginMessage.style.display = "block";
                }
            } catch (error) {
                loginMessage.textContent = "Ошибка сети!";
                loginMessage.style.display = "block";
            }
        });
    }
});
