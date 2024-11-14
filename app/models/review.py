from peewee import ForeignKeyField, TextField, IntegerField, DateTimeField, FloatField, AutoField
from app.database import BaseModel
from datetime import datetime
from .user import User
from .medicine import Medicine

class Review(BaseModel):
    id = AutoField(primary_key=True)
    user = ForeignKeyField(User, backref='reviews')
    medicine = ForeignKeyField(Medicine, backref='reviews')
    rating = IntegerField()
    comment = TextField()
    sentiment_score = FloatField(null=True)  # From Cohere API
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'reviews' 