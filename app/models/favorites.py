from peewee import ForeignKeyField, DateTimeField
from app.database import BaseModel
from datetime import datetime
from app.models.user import User
from app.models.medicine import Medicine

class Favorite(BaseModel):
    user = ForeignKeyField(User, backref='favorites')
    medicine = ForeignKeyField(Medicine, backref='favorited_by')
    added_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'favorites'