import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


def build_database_url() -> str:
    # 1) If DATABASE_URL is explicitly provided, use it
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # 2) Otherwise, build from creds in .env
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    dbname = os.getenv("POSTGRES_DB")

    # In docker-compose network, service name "postgres" is the host
    host = os.getenv("POSTGRES_HOST") or "postgres"

    # IMPORTANT: containers should use 5432 (container port), not host-mapped port
    port = os.getenv("POSTGRES_PORT") or "5432"

    missing = [k for k, v in {
        "POSTGRES_USER": user,
        "POSTGRES_PASSWORD": password,
        "POSTGRES_DB": dbname,
    }.items() if not v]

    if missing:
        raise ValueError(f"Missing required env vars to build DATABASE_URL: {', '.join(missing)}")

    password_enc = quote_plus(password)  # safe for special chars
    return f"postgresql+psycopg2://{user}:{password_enc}@{host}:{port}/{dbname}"


class Settings:
    DATABASE_URL = build_database_url()
    APP_TITLE = "Bayeon Hwayeon Creatures API Admin"
    APP_VERSION = "1.1.0"


settings = Settings()