from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_KEY: str
    APP_SECRET: str
    A_APP_KEY: str
    A_APP_SECRET: str
    USER_ID: str
    CONDITION_NAME: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


env_settings = Settings()
