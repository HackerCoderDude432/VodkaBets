from flask import Flask, flash, redirect, render_template, request, session
from passlib.hash import sha256_crypt
from tinydb import TinyDB, Query

from vodkabets.forms.login_form import LoginForm
from vodkabets.forms.register_form import RegisterForm

db = TinyDB("db.json")
creds = db.table(name="creds")

app = Flask(__name__)
app.secret_key = "This iS a Secret!"

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
        flash("Please log in to continue")
        return redirect("/login")

    return render_template("dashboard.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if "logged_in" in session:
        flash("Already logged in!")
        return redirect("/dashboard")

    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        if not creds.contains(Query().username == username):
            password = sha256_crypt.encrypt(form.username.data + str(form.password.data))

            #entry = User(username, password)
            creds.insert({"username": username, "password": password, "items": None})
            flash("Registered user!")
            return redirect("/login")
        else:
            flash("Username Already Registered! Do you want to <a href='/login'>login?</a>")

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    if "logged_in" in session:
        flash("Already logged in!")
        return redirect("/dashboard")

    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = creds.get(Query().username == form.username.data)
        if user:
            # validate password
            if sha256_crypt.verify(form.username.data + str(form.password.data), user["password"]):
                session["logged_in"] = True
                session["user"] = user["username"]
                return redirect("/dashboard")
        flash("Invalid credentials!")

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    if "logged_in" not in session:
        flash("Silly! You can't logout if you aren't logged in :P")
        return redirect("/login")

    session.clear()
    flash("You are now logged out!")
    return redirect("/")
