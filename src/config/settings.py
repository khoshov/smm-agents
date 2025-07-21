from pydantic_settings import BaseSettings
from pydantic import SecretStr
from typing import Optional

class Settings(BaseSettings):
    # Google API Configuration
    google_api_key: str = ""
    google_cse_id: str = ""
    
    # Flowise Configuration
    flowise_host: str = "http://localhost:3000"
    flowise_id: str = ""
    
    # Telegram Bot Tokens
    moderator_bot_token: SecretStr
    publisher_bot_token: SecretStr
    
    # Channel Configuration
    channel_id: str = "@your_channel_name"
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./telegram_bot.db"
    
    # Database Credentials for Docker
    db_user: str = "smm_user"
    db_password: str = "smm_password"
    
    # System Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    publish_interval_seconds: int = 300
    
    # Environment
    environment: str = "development"
    
    # Optional SSL settings
    webhook_host: Optional[str] = None
    webhook_port: Optional[int] = None
    webhook_path: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Создаем глобальный экземпляр настроек
settings = Settings() 