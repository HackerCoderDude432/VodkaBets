from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, validators

from vodkabets.application import app

class RegisterForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=1, max=app.config["MAX_USERNAME_LENGTH"])])
    email = StringField("Email", [validators.Email()])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo("confirmation", message="Passwords do not match")
    ])
    confirmation = PasswordField("Confirm Password")

    # Only enable recaptcha if it is enabled in the config
    if app.config["ENABLE_RECAPTCHA"] == True:
        recaptcha = RecaptchaField()
