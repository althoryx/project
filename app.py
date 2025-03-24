from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, UTC
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['JWT_SECRET_KEY'] = 'jwtsecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
socketio = SocketIO(app, cors_allowed_origins="*")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
jwt = JWTManager(app)

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(10), default="pending")  # pending, accepted, rejected

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)
    user = db.relationship('User', foreign_keys=[user_id])
    friend = db.relationship('User', foreign_keys=[friend_id])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, default="")
    avatar_url = db.Column(db.String(300), default="/static/img/default_avatar.png")
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False)

    def get_avatar(self):
        return self.avatar_url if self.avatar_url else "/static/img/default_avatar.png"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    notifications = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('settings', uselist=False))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', backref='post', lazy=True) 

class PostLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='comments')

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_name = db.Column(db.String(100), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        emit('user_connected', {'user_id': current_user.id, 'username': current_user.username}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        emit('user_disconnected', {'user_id': current_user.id}, broadcast=True)

@socketio.on('join_chat')
def join_chat(data):
    chat_id = data.get('chat_id')
    join_room(chat_id)

@socketio.on('leave_chat')
def leave_chat(data):
    chat_id = data.get('chat_id')
    leave_room(chat_id)

@socketio.on('send_message')
def handle_send_message(data):
    receiver_id = data.get('receiver_id')
    content = data.get('content')

    if not receiver_id or not content:
        return

    message = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()

    emit('new_message', {
        'sender': current_user.username,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, room=str(receiver_id))

@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not receiver_id or not content:
        return jsonify({"error": "Получатель и текст сообщения обязательны"}), 400

    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({"error": "Пользователь не найден"}), 404

    message = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()

    return jsonify({"message": "Сообщение отправлено"}), 200

@app.route('/api/get_messages/<int:receiver_id>', methods=['GET'])
@login_required
def get_messages(receiver_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    return jsonify([
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "sender_id": msg.sender.id,  # Добавляем sender_id
            "receiver": msg.receiver.username,
            "receiver_id": msg.receiver.id,  # Добавляем receiver_id
            "content": msg.content,
            "timestamp": msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for msg in messages
    ])

@app.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(UTC)
        db.session.commit()

@app.route('/api/get_settings', methods=['GET'])
@login_required
def get_settings():
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()

    return jsonify({
        "dark_mode": settings.dark_mode,
        "notifications": settings.notifications,
        "is_private": current_user.is_private
    })


@app.route('/api/update_settings', methods=['POST'])
@login_required
def update_settings():
    data = request.json
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()

    if not settings:
        settings = UserSettings(user_id=current_user.id)

    settings.dark_mode = data.get("dark_mode", False)
    settings.notifications = data.get("notifications", True)
    current_user.is_private = data.get("is_private", False)

    db.session.add(settings)
    db.session.commit()

    return jsonify({"message": "Настройки успешно сохранены!"})

@app.route('/api/send_friend_request', methods=['POST'])
@login_required
def send_friend_request():
    data = request.json
    receiver_name = data.get("receiver_id")  # Это username, а не ID

    if not receiver_name:
        return jsonify({"error": "Не указано имя получателя"}), 400

    receiver = User.query.filter_by(username=receiver_name).first()
    if not receiver:
        return jsonify({"error": "Пользователь не найден"}), 404

    if receiver.id == current_user.id:
        return jsonify({"error": "Нельзя отправить заявку самому себе"}), 400

    # Проверяем, является ли этот пользователь уже другом
    existing_friendship = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == receiver.id)) |
        ((Friendship.user_id == receiver.id) & (Friendship.friend_id == current_user.id))
    ).first()

    if existing_friendship:
        return jsonify({"error": "Вы уже друзья"}), 400

    # Проверяем, нет ли уже отправленной заявки текущим пользователем
    existing_request = FriendRequest.query.filter_by(
        sender_id=current_user.id, receiver_id=receiver.id
    ).first()

    if existing_request:
        return jsonify({"error": "Вы уже отправили заявку"}), 400

    # Проверяем, нет ли заявки от получателя
    reverse_request = FriendRequest.query.filter_by(
        sender_id=receiver.id, receiver_id=current_user.id
    ).first()

    if reverse_request:
        return jsonify({"error": "Этот пользователь уже отправил вам заявку"}), 400

    # Создаём новую заявку
    new_request = FriendRequest(sender_id=current_user.id, receiver_id=receiver.id)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Заявка отправлена!"}), 200

@app.route('/api/accept_friend_request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)

    if not friend_request or friend_request.receiver_id != current_user.id:
        return jsonify({"error": "Заявка не найдена"}), 404

    sender_id = friend_request.sender_id
    receiver_id = friend_request.receiver_id

    db.session.delete(friend_request)

    existing_friendship = Friendship.query.filter(
        ((Friendship.user_id == sender_id) & (Friendship.friend_id == receiver_id)) |
        ((Friendship.user_id == receiver_id) & (Friendship.friend_id == sender_id))
    ).first()

    if not existing_friendship:
        db.session.add(Friendship(user_id=sender_id, friend_id=receiver_id))

    db.session.commit()

    return jsonify({"message": "Заявка принята!"}), 200


@app.route('/api/remove_friend/<int:friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    friendship = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == current_user.id))
    ).first()

    if not friendship:
        return jsonify({"error": "Пользователь не в друзьях"}), 400

    db.session.delete(friendship)

    FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == friend_id)) |
        ((FriendRequest.sender_id == friend_id) & (FriendRequest.receiver_id == current_user.id))
    ).delete()

    db.session.commit()

    return jsonify({"message": "Пользователь удалён из друзей"}), 200


@app.route('/api/reject_friend_request/<int:request_id>', methods=['POST'])
@login_required
def reject_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)

    if not friend_request or friend_request.receiver_id != current_user.id:
        return jsonify({"error": "Заявка не найдена"}), 404

    db.session.delete(friend_request)
    db.session.commit()

    return jsonify({"message": "Заявка отклонена!"}), 200

@app.route('/api/get_friends/<int:user_id>', methods=['GET'])
@login_required
def get_friends(user_id):
    friendships = Friendship.query.filter(
        (Friendship.user_id == user_id) | (Friendship.friend_id == user_id)
    ).all()

    friends_set = set()
    friends_list = []

    for friendship in friendships:
        friend = friendship.friend if friendship.user_id == user_id else friendship.user
        if friend.id not in friends_set:
            friends_set.add(friend.id)
            friends_list.append({
                "id": friend.id,
                "name": friend.username,
                "avatar_url": friend.avatar_url or "/static/img/default_avatar.png"
            })

    return jsonify(friends_list)

@app.route('/api/friends', methods=['GET'])
@login_required
def get_friends_short():
    friendships = Friendship.query.filter(
        (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)
    ).all()

    friends_set = set()
    friends_list = []

    for friendship in friendships:
        friend = friendship.friend if friendship.user_id == current_user.id else friendship.user
        if friend.id not in friends_set:
            friends_set.add(friend.id)
            friends_list.append({"id": friend.id, "name": friend.username})

    return jsonify(friends_list)

@app.route('/api/get_friend_requests', methods=['GET'])
@login_required
def get_friend_requests():
    requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status="pending").all()
    return jsonify([
        {"id": req.id, "sender": req.sender.username}
        for req in requests
    ])

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Ожидается JSON-данные"}), 400

        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "Все поля обязательны!"}), 400

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                return jsonify({"error": "Этот логин уже занят!"}), 400
            if existing_user.email == email:
                return jsonify({"error": "Этот email уже используется!"}), 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Регистрация успешна!"}), 200

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Ожидается JSON-данные"}), 400

        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return jsonify({"message": "Вход выполнен успешно"}), 200

        return jsonify({"error": "Неверный логин или пароль"}), 401

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).all()
    return render_template('profile.html', user=current_user, posts=posts)

@app.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)

    if user.is_private and user.id != current_user.id:
        return render_template('private_profile.html', user=user)

    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    
    return render_template('view_profile.html', user=user, posts=posts)

@app.route('/api/toggle_privacy', methods=['POST'])
@login_required
def toggle_privacy():
    current_user.is_private = not current_user.is_private
    db.session.commit()
    return jsonify({"message": "Настройки приватности обновлены", "is_private": current_user.is_private})

@app.route('/api/users')
@login_required
def get_users():
    query = request.args.get('query', '').lower()
    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    return jsonify([{"id": user.id, "username": user.username} for user in users])

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    return jsonify([{ "text": note.text } for note in notifications])

@app.route('/friends')
@login_required
def friends():
    return render_template('friends.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/messages')
@login_required
def messages():
    return render_template('messages.html')

@app.route('/feed')
@login_required
def feed():
    posts = Post.query.order_by(Post.timestamp.desc()).all()  # Загружаем все посты пользователей
    return render_template('feed.html', user=current_user, posts=posts)


@app.route('/api/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({"error": "Файл не загружен"}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "Файл не выбран"}), 400

    filename = f"user_{current_user.id}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    file.save(filepath)

    current_user.avatar_url = f"/static/uploads/{filename}"
    db.session.commit()
    
    return jsonify({"success": True, "avatar_url": current_user.avatar_url}), 200

@app.route('/api/delete_avatar', methods=['POST'])
@login_required
def delete_avatar():
    current_user.avatar_url = "/static/img/default_avatar.png"
    db.session.commit()
    return jsonify({"success": True}), 200

@app.route('/api/get_posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    post_list = []
    for post in posts:
        if not post.user:
            continue
        post_list.append({
            'id': post.id,
            'username': post.user.username if post.user else 'Удалённый пользователь',
            'avatar_url': post.user.avatar_url if post.user else '/static/img/default_avatar.png',
            'content': post.content,
            'timestamp': post.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'likes': post.likes,
            'comments': [{'username': c.user.username, 'content': c.content, 'timestamp': c.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for c in post.comments]
        })
    return jsonify(post_list)


@app.route('/api/create_post', methods=['POST'])
@login_required
def create_post():
    data = request.json
    if 'content' in data:
        new_post = Post(user_id=current_user.id, content=data['content'])
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"message": "Пост опубликован"}), 200
    return jsonify({"error": "Контент не может быть пустым"}), 400

@app.route('/api/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = PostLikes.query.filter_by(post_id=post_id, user_id=current_user.id).first()

    if existing_like:
        db.session.delete(existing_like)
        post.likes = max(0, post.likes - 1)  # Исключаем отрицательные значения
    else:
        new_like = PostLikes(post_id=post_id, user_id=current_user.id)
        db.session.add(new_like)
        post.likes += 1

    db.session.commit()
    return jsonify({'message': 'Лайк обновлён', 'likes': post.likes})


@app.route('/api/comment_post/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    data = request.json
    content = data.get('content', '').strip()

    if not content:
        return jsonify({"error": "Комментарий не может быть пустым"}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Пост не найден"}), 404

    comment = Comment(user_id=current_user.id, post_id=post_id, content=content)
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Комментарий добавлен"}), 200


@app.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    email = data.get('email')
    bio = data.get('bio')

    if email:
        current_user.email = email
    if bio:
        current_user.bio = bio

    db.session.commit()
    return jsonify({"message": "Профиль обновлён"}), 200

@app.route('/api/delete_post/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        return jsonify({'error': 'Вы не можете удалить этот пост'}), 403
    
    Comment.query.filter_by(post_id=post_id).delete()
    PostLikes.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Пост удалён'}), 200

@app.route('/api/delete_comment/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        return jsonify({'error': 'Вы не можете удалить этот комментарий'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Комментарий удалён'}), 200

@app.route('/api/get_comments/<int:post_id>', methods=['GET'])
@login_required
def get_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).limit(3).all()

    return jsonify([
        {
            "id": comment.id,
            "username": comment.user.username,
            "avatar_url": comment.user.avatar_url,
            "content": comment.content,
            "timestamp": comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for comment in comments
    ])

@app.route('/api/get_comments/<int:post_id>/<int:offset>', methods=['GET'])
@login_required
def get_comments_paginated(post_id, offset):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).offset(offset).limit(3).all()

    return jsonify([
        {
            "id": comment.id,
            "username": comment.user.username,
            "avatar_url": comment.user.avatar_url,
            "content": comment.content,
            "timestamp": comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for comment in comments
    ])

@app.route('/api/check_like/<int:post_id>', methods=['GET'])
@login_required
def check_like(post_id):
    liked = PostLikes.query.filter_by(post_id=post_id, user_id=current_user.id).first() is not None
    return jsonify({'liked': liked})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)