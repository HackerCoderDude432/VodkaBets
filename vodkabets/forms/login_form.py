from wtforms import Form, StringField, PasswordField, validators

class LoginForm(Form):
    username = StringField("Username", [validators.Length(min=1, max=25)])
    password = PasswordField("Password", [validators.DataRequired()])
