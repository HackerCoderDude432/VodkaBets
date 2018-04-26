from peewee import DateTimeField, FloatField, PrimaryKeyField, TextField
from vodkabets.models.base_model import BaseModel

class Record(BaseModel):
    id = PrimaryKeyField()
    time_gen = DateTimeField()
    crash_point = FloatField()
    computed_hash = TextField()
    combined_client_hashes = TextField()
