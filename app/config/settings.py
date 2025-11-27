import os
from typing import List

class Settings:
    def __init__(self):
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        self.SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY")
        self.DEBUG = os.getenv("DEBUG", "True").lower() == "true"
        self.CORS_ORIGINS = ["*"]
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_here")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

settings = Settings()