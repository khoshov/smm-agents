from pydantic import BaseSettings


class Settings(BaseSettings):
    google_api_key: str
    google_cse_id: str
    flowise_host: str
    flowise_id: str

    class Config:
        env_file = ".env"


settings = Settings()
