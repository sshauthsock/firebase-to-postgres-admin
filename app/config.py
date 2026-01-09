import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    APP_TITLE = "Bayeon Hwayeon Creatures API Admin"
    APP_VERSION = "1.1.0"
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")


settings = Settings()