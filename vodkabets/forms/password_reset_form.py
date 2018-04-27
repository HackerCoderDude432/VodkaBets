from flask_wtf import FlaskForm, RecaptchaField
from wtforms import HiddenField, PasswordField, validators

from vodkabets.application import app

class PasswordResetForm(FlaskForm):
    user_sid = HiddenField()
    password = PasswordField("New Password", [
        validators.DataRequired(),
        validators.EqualTo("confirmation", message="Passwords do not match")
    ])
    confirmation = PasswordField("Confirm New Password")

    # Only enable recaptcha if it is enabled in the config
    if app.config["ENABLE_RECAPTCHA"] == True:
        recaptcha = RecaptchaField()
