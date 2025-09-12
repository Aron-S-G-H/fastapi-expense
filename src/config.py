from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    AUTH_MODE: str
    SUPPORTED_LANGS: str
    DEFAULT_LANG: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def supported_langs_list(self):
        return [lang.strip() for lang in self.SUPPORTED_LANGS.split(",")]


settings = Setting()
