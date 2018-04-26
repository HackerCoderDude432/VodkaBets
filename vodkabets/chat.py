from flask import Markup, request
from flask_login import current_user
from flask_socketio import emit, Namespace

class Chat(Namespace):
    def __init__(self, socket, max_length=255):
        super().__init__(namespace="/_chat")
        socket.on_namespace(self)

        self.num_connected = 0
        self.max_length = max_length

    def on_connect(self):
        if current_user.is_authenticated:
            self.num_connected += 1
            emit("update_chat_count", (self.num_connected), broadcast=True)
        else:
            emit("update_chat_count", (self.num_connected), room=request.sid)

    def on_send_message(self, message):
        if current_user.is_authenticated:
            safe_message = Markup.escape(message)
            if len(safe_message) > self.max_length:
                emit("flash", ("Message is too long!", "ERROR"), namespace="/", room=request.sid)
                return
            emit("process_message", (str(current_user.username), str(safe_message)), broadcast=True)

    def on_disconnect(self):
        if current_user.is_authenticated:
            self.num_connected -= 1
            emit("update_chat_count", (self.num_connected), broadcast=True)
        else:
            emit("update_chat_count", (self.num_connected), room=request.sid)
