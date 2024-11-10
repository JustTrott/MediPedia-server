from peewee import CharField, TextField, DateTimeField
from app.database import BaseModel
from datetime import datetime

class Medicine(BaseModel):
    name = CharField()
    description = TextField(null=True)
    fda_id = CharField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'medicines' 