import os
from pydantic_settings import BaseSettings

APP_ENV = os.getenv("APP_ENV", "dev")

class Settings(BaseSettings):
    APP_ENV: str = APP_ENV
    DATABASE_URL: str = f"postgresql://sagole_user:password@localhost/{APP_ENV}_db"
    DB_SCHEMA: str = APP_ENV

    # Security settings
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_an_env_file"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        # e.g. .env.dev, .env.test
        # The order is important. Variables from the right-most file will override
        # those in files to its left.
        env_file = (".env", f".env.{APP_ENV}")

settings = Settings()