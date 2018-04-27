from flask_login import UserMixin
from peewee import IntegerField, Model, PrimaryKeyField, TextField

from vodkabets.application import db

class User(Model, UserMixin):
    id = PrimaryKeyField()
    username = TextField(unique=True)
    password = TextField()
    session_token = TextField(unique=True)
    vlads = IntegerField()
    client_seed = TextField(null=True)

    class Meta:
        database = db

    def get_id(self):
        return self.session_token
