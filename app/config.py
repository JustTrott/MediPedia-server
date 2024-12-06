import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    API_V1_STR = "/api/v1"
    OPENFDA_API_KEY = os.getenv("OPENFDA_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


settings = Config() 