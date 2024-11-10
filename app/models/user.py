from peewee import CharField, BooleanField
from app.database import BaseModel

class User(BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    hashed_password = CharField()
    is_active = BooleanField(default=True)
    is_superuser = BooleanField(default=False)

    class Meta:
        table_name = 'users' 