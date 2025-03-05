from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from os import getcwd

# print(Path(__file__).parent)


class Settings(BaseSettings):
    postgres_db: str | None
    postgres_user: str
    postgres_password: str
    postgres_host: str
    db_test_name: str | None = "fastapi_project_test_db"
    max_connection_count: int = 10

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}/{self.postgres_db}"

    @property
    def database_test_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}/{self.db_test_name}"

    model_config = SettingsConfigDict(
        env_file=Path(getcwd()).parent / ".env", env_file_encoding="utf-8"
    )


settings = Settings()
