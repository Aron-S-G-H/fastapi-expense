from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    AUTH_MODE: str
        
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    
settings = Setting()