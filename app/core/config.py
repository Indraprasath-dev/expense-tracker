from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str
    LOG_LEVEL: str = "INFO"
    JWT_SECRET_KEY: SecretStr = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
