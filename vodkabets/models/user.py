from flask_login import UserMixin
from peewee import IntegerField, TextField
from vodkabets.models.base_model import BaseModel

class User(BaseModel, UserMixin):
    id = IntegerField(unique=True)
    username = TextField(unique=True)
    password = TextField()
