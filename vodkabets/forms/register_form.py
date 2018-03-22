from wtforms import Form, StringField, PasswordField, validators

class RegisterForm(Form):
    username = StringField("Username", [validators.Length(min=1, max=25)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo("confirmation", message="Passwords do not match")
    ])
    confirmation = PasswordField("Confirm Password")
