from peewee import SqliteDatabase, Model
from app.config import settings

db = SqliteDatabase(settings.DATABASE_URL.replace("sqlite:///", ""))

class BaseModel(Model):
    class Meta:
        database = db 