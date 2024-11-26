#Many to many users with users
#Using ManyToManyField

from peewee import IntegerField, CharField, TextField, DateTimeField, AutoField, ManyToManyField, ForeignKeyField
from app.database import BaseModel
from datetime import datetime
from .user import User
from .medicine import Medicine

class Favorite(BaseModel):
    #Will be userid when user favorites something
    user = ForeignKeyField(User, backref= 'favorites')
    medicine = ForeignKeyField(User, backref = 'favorite_of')
    time = DateTimeField(default=datetime.now)

    class Meta:
        table_name='favoriteMeds'
