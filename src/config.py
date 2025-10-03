from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/postgres"
    SECRET_KEY: str
    ALGORITHM: str
    AUTH_MODE: str
    SUPPORTED_LANGS: str
    DEFAULT_LANG: str
    REDIS_URL: str = "redis://redis:6379"
    SENTRY_DSN: str = "https://11395568eaeae90b40c6cf95202d8801@sentry.hamravesh.com/9091"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def supported_langs_list(self):
        return [lang.strip() for lang in self.SUPPORTED_LANGS.split(",")]


settings = Setting()
