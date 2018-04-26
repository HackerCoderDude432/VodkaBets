from flask_login import UserMixin
from peewee import IntegerField, PrimaryKeyField, TextField
from vodkabets.models.base_model import BaseModel

class User(BaseModel, UserMixin):
    id = PrimaryKeyField()
    username = TextField(unique=True)
    password = TextField()
    session_token = TextField(unique=True)
    vlads = IntegerField()
    client_seed = TextField(null=True)

    def get_id(self):
        return self.session_token
