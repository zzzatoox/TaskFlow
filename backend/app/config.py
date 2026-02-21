from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskFlow API"
    db: str = "postgresql"
    db_provider: str = "asyncpg"
    db_username: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "taskflow"

    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def database_url(self) -> str:
        return f"{self.db}+{self.db_provider}://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
