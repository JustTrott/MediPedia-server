from peewee import CharField, TextField, DateTimeField, AutoField
from app.database import BaseModel
from datetime import datetime

class Medicine(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    description = TextField(null=True)
    fda_id = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'medicines' 