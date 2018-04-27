import os

from flask import Flask
from peewee import SqliteDatabase

# INIT THE APP AND DATABASE BEFORE EVERYTHING IS IMPORTED

# App
app = Flask(__name__, instance_relative_config=True)
app.config.from_json("config.json")

# database
db = SqliteDatabase(os.path.join(app.instance_path, "users.db"))

from flask import flash, Markup, redirect, render_template, request
from flask_gravatar import Gravatar
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_socketio import SocketIO
from itsdangerous import BadTimeSignature, SignatureExpired, URLSafeTimedSerializer
from secrets import token_urlsafe
from werkzeug.security import generate_password_hash, check_password_hash

from vodkabets.chat import Chat

from vodkabets.forms.login_form import LoginForm
from vodkabets.forms.password_reset_form import PasswordResetForm
from vodkabets.forms.register_form import RegisterForm

from vodkabets.games.crash import crash_blueprint, CrashGame

from vodkabets.models.record import Record
from vodkabets.models.user import User

from vodkabets.misc.redirect import safe_redirect

# initialize database
db.create_tables([User, Record])

# SocketIO
socket = SocketIO(app)

# init chat
chat = Chat(socket, max_length=app.config.get("MAX_CHAT_MESSAGE_LENGTH"))

# Init games
crash = CrashGame(socket)
app.register_blueprint(crash_blueprint, url_prefix="/crash")

# Init flask_login
login_man = LoginManager()
login_man.login_view = "/login"
login_man.login_message = "Please login to continue!"
login_man.login_message_category = "ERROR"
login_man.session_protection = "strong"
login_man.init_app(app)

# Flask-Mail
if app.config["ENABLE_MAIL"]:
    mail = Mail(app)

# Gravatar icons
gravatar = Gravatar(app)

@login_man.user_loader
def get_user(token):
    # check if user exists, if true return user, otherwise return None
    query = User.select().where(User.session_token == token)
    if query.exists():
        return query.get()
    else:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        flash("Already logged in!", "WARNING")
        return redirect("/dashboard")

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # check username length
        if len(form.username.data) > app.config["MAX_USERNAME_LENGTH"]:
            flash("Username is too long!", "ERROR")

        username = Markup.escape(form.username.data)
        if not User.select().where(User.username == username).exists():
            # password is auto-salted
            password = generate_password_hash(form.password.data, salt_length=app.config.get("SALT_LENGTH"))

            # (recursivly) generate first session token
            new_token = token_urlsafe(app.config.get("SESSION_TOKEN_LENGTH"))
            while User.select().where(User.session_token == new_token).exists():
                new_token = token_urlsafe(app.config.get("SESSION_TOKEN_LENGTH"))

            vars = {
                "username": username,
                "email": form.email.data,
                "password": password,
                "session_token": new_token,
                "vlads": app.config.get("STARTING_VLADS"),
                "client_seed": None
            }

            # Only add the verified_email boolean if mail is on
            if app.config["ENABLE_MAIL"]:
                vars["verified_email"] = False

            User.create(**vars)

            # generate an email verification link and send it (if enabled)
            if app.config["ENABLE_MAIL"]:
                serializer = URLSafeTimedSerializer(secret_key=app.config["SECRET_KEY"], salt="email_verification")
                verification_token = serializer.dumps(new_token)
                verification_url = request.url_root + "/verify/" + verification_token

                msg = Message(subject="VodkaBets Verification")
                msg.add_recipient(form.email.data)
                msg.html = open(os.path.join(app.root_path, "assets", "verify_email.html"), "r").read().format(username, verification_url)

                mail.send(msg)

            flash("Registered user!", "SUCCESS")
            return redirect("/login")
        else:
            flash("Username Already Registered!", "ERROR")

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        flash("Already logged in!", "WARNING")
        return redirect("/dashboard")

    form = LoginForm(request.form)
    if form.validate_on_submit():
        # check if user exists
        query = User.select().where(User.username == form.username.data)
        if query.exists():
            user = query.get() # get user as they exist

            # validate password
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash("Sucessfully logged in!", "SUCCESS")

                # check if there is a redirect after the login, and verify it is safe
                target_redirect = request.args.get("next")
                return safe_redirect(request.host_url, target_redirect, fallback="/dashboard")
        flash("Invalid credentials!", "ERROR")

    return render_template("login.html", form=form)

# Only include the verify endpoint if mail is enabled
if app.config["ENABLE_MAIL"]:

    @app.route("/verify/<token>")
    def verify_email(token):
        serializer = URLSafeTimedSerializer(secret_key=app.config["SECRET_KEY"], salt="email_verification")

        try:
            user_sid = serializer.loads(s=token,max_age=int(app.config["MAX_EMAIL_VERIFICATION_AGE"]))
        except BadTimeSignature:
            flash("Invalid Token sent!", "ERROR")
            return redirect("/")
        except SignatureExpired:
            flash("The token has expired! Try resending the message...", "ERROR")
            return redirect("/")
        else:
            # check if user exists
            query = User.select().where(User.session_token == user_sid)
            if query.exists():
                user = query.get() # get user as they exist

                # Check if already verified, if so throw a hissy fit
                if user.verified_email == True:
                    flash("User is already verified!", "INFO")
                    return redirect("/")

                # Verify the email and invalidate the old session token
                # (recursivly) generate first session token
                new_token = token_urlsafe(app.config.get("SESSION_TOKEN_LENGTH"))
                while User.select().where(User.session_token == new_token).exists():
                    new_token = token_urlsafe(app.config.get("SESSION_TOKEN_LENGTH"))

                # apply the changes
                user.verified_email = True
                user.session_token = new_token
                user.save()

                flash("Sucessfully verified your account! Please relog to contine...", "SUCCESS")
                return redirect("/login")
            else:
                flash("User does not exist!", "ERROR")

        return redirect("/")

    @app.route("/reset/<token>")
    def verify_email(token):
        # form submit
        form = PasswordResetForm(request.form)
        if form.validate_on_submit():
            # check if user exists
            query = User.select().where(User.session_token == form.user_sid.data)
            if query.exists():
                user = query.get() # get user as they exist

                # change the password and invalidate the old session token

                # change the password
                password = generate_password_hash(form.password.data, salt_length=app.config.get("SALT_LENGTH"))

                # (recursivly) generate first session token
                new_token = token_urlsafe(app.config.get("SESSION_TOKEN_LENGTH"))
                while User.select().where(User.session_token == new_token).exists():
                    new_token = token_urlsafe(app.config.get("SESSION_TOKEN_LENGTH"))

                # apply the changes
                user.password = password
                user.session_token = new_token
                user.save()

                flash("Password sucessfully reset! Please login...", "SUCCESS")
                return redirect("/login")
            else:
                flash("User does not exist!", "ERROR")
                return redirect("/")
        else:
            # Generate a password_reset_form if token is valid
            serializer = URLSafeTimedSerializer(secret_key=app.config["SECRET_KEY"], salt="password_reset")

            try:
                user_sid = serializer.loads(s=token,max_age=app.config["MAX_PASSWORD_RESET_AGE"])
            except BadTimeSignature:
                flash("Invalid Token sent!", "ERROR")
                return redirect("/")
            except SignatureExpired:
                flash("The token has expired! Try resending the message...", "ERROR")
                return redirect("/")
            else:
                # check if user exists
                query = User.select().where(User.session_token == user_sid)
                if query.exists():
                    user = query.get() # get user as they exist

                    # set the hidden field
                    form.user_sid.data = user.session_token

                    # render the password_reset.html file
                    return render_template("password_reset.html", form=form)
                else:
                    flash("User does not exist!", "ERROR")
                    return redirect("/")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out!", "SUCCESS")
    return redirect("/")

if __name__ == "__main__":
    socket.run(app)
