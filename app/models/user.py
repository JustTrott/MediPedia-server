from peewee import CharField, AutoField
from app.database import BaseModel

class User(BaseModel):
    id = AutoField(primary_key=True)
    email = CharField(unique=True)

    class Meta:
        table_name = 'users' 