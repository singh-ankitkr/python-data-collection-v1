from pydantic import BaseSettings


class Settings(BaseSettings):
    db_path: str = "database.db"


settings = Settings()
