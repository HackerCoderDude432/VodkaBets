from flask_login import UserMixin
from peewee import TextField
from vodkabets.models.base_model import BaseModel

class User(BaseModel, UserMixin):
    username = TextField(unique=True)
    password = TextField()
