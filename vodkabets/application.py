import os

from flask import Flask, flash, redirect, render_template, request
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from peewee import SqliteDatabase
from secrets import token_urlsafe
from werkzeug.security import generate_password_hash, check_password_hash

from vodkabets.forms.login_form import LoginForm
from vodkabets.forms.register_form import RegisterForm

from vodkabets.models.base_model import set_model_database
from vodkabets.models.user import User

from vodkabets.misc.redirect import safe_redirect

app = Flask(__name__, instance_relative_config=True)
app.config.from_json("config.json")

# initialize database
db = SqliteDatabase(os.path.join(app.instance_path, "users.db"))
set_model_database(db) # Assign this table to the base model
db.create_tables([User])

# Init flask_login
login_man = LoginManager()
login_man.login_view = "/login"
login_man.login_message = "Please login to continue!"
login_man.login_message_category = "ERROR"
login_man.session_protection = "strong"
login_man.init_app(app)

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
        flash("Already logged in!", "ERROR")
        return redirect("/dashboard")

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        if not User.select().where(User.username == username).exists():
            # password is auto-salted
            password = generate_password_hash(form.password.data, salt_length=app.config.get("SALT_LENGTH"))

            # (recursivly) generate first session token
            new_token = token_urlsafe(app.config.get("SESSION_TOKEN_LENGTH"))
            while User.select().where(User.session_token == new_token).exists():
                new_token = token_urlsafe(app.config.get("SESSION_TOKEN_LENGTH"))

            User.create(username=username, password=password, session_token=new_token)
            flash("Registered user!", "SUCCESS")
            return redirect("/login")
        else:
            flash("Username Already Registered!", "ERROR")

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        flash("Already logged in!", "ERROR")
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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out!", "SUCCESS")
    return redirect("/")

if __name__ == "__main__":
    app.run()
