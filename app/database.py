from peewee import SqliteDatabase, Model
from app.config import settings

db = SqliteDatabase(settings.DATABASE_URL.replace("sqlite:///", ""))
test_db = SqliteDatabase('unit_test.db')

class BaseModel(Model):
    class Meta:
        database = db 