from peewee import Model, Proxy

database_proxy = Proxy()
class BaseModel(Model):
    class Meta:
        database = database_proxy

def set_model_database(database):
    database_proxy.initialize(database)
