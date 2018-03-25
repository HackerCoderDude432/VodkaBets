from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators

class LoginForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=1, max=25)])
    password = PasswordField("Password", [validators.DataRequired()])
    remember_me = BooleanField("Remember Me")
