import os

from flask import Flask, flash, redirect, render_template, request, session
from peewee import SqliteDatabase
from werkzeug.security import generate_password_hash, check_password_hash

from vodkabets.forms.login_form import LoginForm
from vodkabets.forms.register_form import RegisterForm

from vodkabets.models.base_model import set_model_database
from vodkabets.models.user import User

app = Flask(__name__, instance_relative_config=True)
app.config.from_json("config.json")

# initialize database
db = SqliteDatabase(os.path.join(app.instance_path, "users.db"))
set_model_database(db) # Assign this table to the base model
db.create_tables([User])

@app.before_request
def on_first_user():
    # make logged in sessions last for 30 days
    session.permenant = True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if "logged_in" not in session:
        flash("Please log in to continue", "ERROR")
        return redirect("/login")

    return render_template("dashboard.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if "logged_in" in session:
        flash("Already logged in!", "INFO")
        return redirect("/dashboard")

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        if not User.select().where(User.username == username).exists():
            password = generate_password_hash(form.password.data, salt_length=15)

            User.create(username=username, password=password)
            flash("Registered user!", "SUCCESS")
            return redirect("/login")
        else:
            flash("Username Already Registered!", "ERROR")

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    if "logged_in" in session:
        flash("Already logged in!", "ERROR")
        return redirect("/dashboard")

    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.select().where(User.username == form.username.data).get()
        if user:
            # validate password
            if check_password_hash(user.password, form.password.data):
                session["logged_in"] = True
                session["user"] = user.username
                flash("Sucessfully logged in!", "SUCCESS")
                return redirect("/dashboard")
        flash("Invalid credentials!", "ERROR")

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    if "logged_in" not in session:
        flash("Silly! You can't logout if you aren't logged in :P", "ERROR")
        return redirect("/login")

    session.clear()
    flash("You are now logged out!", "SUCCESS")
    return redirect("/")
