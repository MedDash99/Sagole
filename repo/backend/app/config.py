from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # The default value is for a local postgres instance.
    # In a real setup (like with Docker Compose), this URL
    # will be overridden by an environment variable.
    DATABASE_URL: str = "postgresql://user:password@localhost/db"

    class Config:
        env_file = ".env"

settings = Settings()