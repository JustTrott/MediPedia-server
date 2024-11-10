from peewee import ForeignKeyField, TextField, IntegerField, DateTimeField, FloatField
from app.database import BaseModel
from datetime import datetime
from .user import User
from .medicine import Medicine

class Review(BaseModel):
    user = ForeignKeyField(User, backref='reviews')
    medicine = ForeignKeyField(Medicine, backref='reviews')
    rating = IntegerField()
    comment = TextField()
    sentiment_score = FloatField(null=True)  # From Cohere API
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'reviews' 