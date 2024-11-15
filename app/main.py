from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import db
from app.models.user import User
from app.models.profile import PersonalProfile, MedicalData
from app.models.medicine import Medicine
from app.models.review import Review
from app.api.v1.endpoints import users, medicines, reviews, profiles
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup - Connect to DB and create tables
    db.connect()
    db.create_tables([
        User, 
        PersonalProfile, 
        MedicalData,
        Medicine, 
        Review
    ])
    
    yield
    
    if not db.is_closed():
        db.close()

app = FastAPI(
    title="MediPedia API",
    lifespan=lifespan
)

# Include routers
app.include_router(
    users.router,
    prefix=settings.API_V1_STR + "/users",
    tags=["users"]
)
app.include_router(
    profiles.router,
    prefix=settings.API_V1_STR + "/profiles",
    tags=["profiles"]
)
app.include_router(
    medicines.router,
    prefix=settings.API_V1_STR + "/medicines",
    tags=["medicines"]
)
app.include_router(
    reviews.router,
    prefix=settings.API_V1_STR + "/reviews",
    tags=["reviews"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to MediPedia API"} 