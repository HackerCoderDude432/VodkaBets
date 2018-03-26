from flask import Blueprint, render_template
from flask_login import current_user
from flask_socketio import Namespace

crash_blueprint = Blueprint("crash", __name__)

@crash_blueprint.route("/")
def crash():
    return render_template("/crash/crash.html")

class CrashGame(Namespace):
    def __init__(self, socket):
        super().__init__(namespace="/_crash")
        self.socket = socket

    def start(self):
        # Connects the namespace and starts the background task
        self.socket.on_namespace(self)
        self.socket.start_background_task(self.update)

    def update(self):
        while True:
            print("Sleeping!")
            self.socket.sleep(10)

    def on_connect(self):
        if current_user.is_authenticated:
            print("User " + current_user.username + " joined!")
