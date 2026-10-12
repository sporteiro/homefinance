from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_name: str = "HomeFinance"
    app_env: str = "development"

    postgres_user: str = "homefinance"
    postgres_password: str = "change_me"
    postgres_db: str = "homefinance"
    postgres_host: str = "db"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
