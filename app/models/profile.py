from peewee import AutoField, ForeignKeyField, CharField, IntegerField, TextField, DateTimeField
from datetime import datetime
from app.database import BaseModel
from .user import User

class PersonalProfile(BaseModel):
    id = AutoField(primary_key=True)
    user = ForeignKeyField(User, backref='profile')
    first_name = CharField()
    last_name = CharField()
    age = IntegerField()
    gender = CharField()
    phone = CharField(null=True)
    address = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'personal_profiles'

class MedicalData(BaseModel):
    id = AutoField(primary_key=True)
    profile = ForeignKeyField(PersonalProfile, backref='medical_data')
    allergies = TextField(null=True)
    conditions = TextField(null=True)
    preferred_medication_type = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'medical_data' 