from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # noinspection PyArgumentList
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    DATABASE_URL: str
    REDIS_URL: str

    OPENAI_API_KEY: str
    WAQI_KEY: str

# noinspection PyArgumentList
settings = Settings()





