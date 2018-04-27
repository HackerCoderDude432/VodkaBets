from flask_wtf import FlaskForm, RecaptchaField
from wtforms import BooleanField, StringField, PasswordField, validators

from vodkabets.application import app

class LoginForm(FlaskForm):
    username = StringField("Username/Email", [validators.Length(min=1)])
    password = PasswordField("Password", [validators.DataRequired()])

    # Only enable recaptcha if it is enabled in the config
    if app.config["ENABLE_RECAPTCHA"] == True:
        recaptcha = RecaptchaField()

    remember_me = BooleanField("Remember Me")
