document.addEventListener("DOMContentLoaded", function () {
    const friendsList = document.getElementById("friends-list");
    if (friendsList) {
        function loadFriends() {
            fetch(`/api/get_friends/${profileUserId}`)
                .then(response => response.json())
                .then(friends => {
                    friendsList.innerHTML = "";
                    if (friends.length === 0) {
                        friendsList.innerHTML = "<p>Нет друзей</p>";
                    } else {
                        friends.slice(0, 6).forEach(friend => {
                            let div = document.createElement("div");
                            div.classList.add("friend-card");

                            let avatar = document.createElement("img");
                            avatar.src = friend.avatar_url || "/static/img/default_avatar.png";
                            avatar.classList.add("friend-avatar");

                            let name = document.createElement("a");
                            name.href = `/profile/${friend.id}`;
                            name.textContent = friend.name;
                            name.classList.add("friend-name");

                            div.appendChild(avatar);
                            div.appendChild(name);
                            friendsList.appendChild(div);
                        });
                    }
                });
        }
        loadFriends();
    }

    document.querySelectorAll(".like-post").forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-id");

            fetch(`/api/like_post/${postId}`, { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        this.textContent = `❤️ ${data.likes}`;
                    } else {
                        alert("Ошибка: " + (data.error || "Неизвестная ошибка"));
                    }
                });
        });
    });

    document.querySelectorAll(".comment-btn").forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-id");
            const commentInput = document.querySelector(`.comment-input[data-id='${postId}']`);
            const commentText = commentInput.value.trim();

            if (!commentText) {
                alert("Комментарий не может быть пустым!");
                return;
            }

            fetch(`/api/comment_post/${postId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: commentText })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    location.reload();
                } else {
                    alert("Ошибка при отправке комментария: " + (data.error || "Неизвестная ошибка"));
                }
            });
        });
    });

    document.querySelectorAll(".delete-comment").forEach(button => {
        button.addEventListener("click", function () {
            const commentId = this.getAttribute("data-id");

            fetch(`/api/delete_comment/${commentId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        document.getElementById(`comment-${commentId}`).remove();
                    } else {
                        alert("Ошибка удаления: " + (data.error || "Неизвестная ошибка"));
                    }
                });
        });
    });

    const modal = document.getElementById("infoModal");
    const btn = document.getElementById("toggleInfo");
    const closeBtn = document.querySelector(".modal .close");

    if (modal && btn && closeBtn) {
        modal.style.display = "none";

        btn.addEventListener("click", function () {
            modal.style.display = "flex";
        });

        closeBtn.addEventListener("click", function () {
            modal.style.display = "none";
        });

        window.addEventListener("click", function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    }
});
document.querySelectorAll(".comment-toggle").forEach(button => {
    button.addEventListener("click", function() {
        const postId = this.getAttribute("data-id");
        const commentSection = document.getElementById(`comment-section-${postId}`);
        commentSection.classList.toggle("hidden");
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("friendsModal");
    const closeBtn = modal.querySelector(".close");
    const allFriendsList = document.getElementById("all-friends-list");
    const showAllFriendsBtn = document.getElementById("showAllFriends");

    if (showAllFriendsBtn) {
        showAllFriendsBtn.addEventListener("click", function (event) {
            event.preventDefault();
            modal.style.display = "flex";

            fetch(`/api/get_friends/${profileUserId}`)
                .then(response => response.json())
                .then(friends => {
                    allFriendsList.innerHTML = "";
                    if (friends.length === 0) {
                        allFriendsList.innerHTML = "<p>Нет друзей</p>";
                    } else {
                        friends.forEach(friend => {
                            let div = document.createElement("div");
                            div.classList.add("friends-modal-item");

                            let avatar = document.createElement("img");
                            avatar.src = friend.avatar_url || "/static/img/default_avatar.png";
                            avatar.alt = "Аватар";

                            let name = document.createElement("a");
                            name.href = `/profile/${friend.id}`;
                            name.textContent = friend.name;

                            div.appendChild(avatar);
                            div.appendChild(name);
                            allFriendsList.appendChild(div);
                        });
                    }
                });
        });
    }

    closeBtn.addEventListener("click", function () {
        modal.style.display = "none";
    });

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});
