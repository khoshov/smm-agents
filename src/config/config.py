from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    google_api_key: str
    google_cse_id: str
    flowise_host: str
    flowise_id: str
    moderator_bot_token: SecretStr
    publisher_bot_token: SecretStr

    class Config:
        env_file = ".env"
