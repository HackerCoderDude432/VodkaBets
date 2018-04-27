from peewee import DateTimeField, FloatField, Model, PrimaryKeyField, TextField

from vodkabets.application import db

class Record(Model):
    id = PrimaryKeyField()
    time_gen = DateTimeField()
    crash_point = FloatField()
    computed_hash = TextField()
    combined_client_hashes = TextField()

    class Meta:
        database = db
