from flask_login import UserMixin
from peewee import BooleanField, IntegerField, Model, PrimaryKeyField, TextField

from vodkabets.application import app, db

class User(Model, UserMixin):
    id = PrimaryKeyField()
    username = TextField(unique=True)
    email = TextField(unique=True)

    # Only enable email verification is mail is enabled
    if app.config["ENABLE_MAIL"] == True:
        verified_email = BooleanField()

    password = TextField()
    session_token = TextField(unique=True)
    vlads = IntegerField()
    client_seed = TextField(null=True)

    class Meta:
        database = db

    def get_id(self):
        return self.session_token
