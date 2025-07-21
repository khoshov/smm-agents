from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str
    google_cse_id: str
    flowise_host: str
    flowise_filter_id: str
    flowise_copywriter_id: str
    
    # Настройки для генерации изображений (OpenAI DALL-E)
    generate_images: bool = True  # Включить/выключить генерацию изображений
    openai_api_key: str = ""
    
    # Настройки сбора новостей
    rss_hours_period: int = 72  # Период в часах для RSS (по умолчанию 3 дня)
    enable_google_news: bool = True   # Включить Google Custom Search
    enable_rss_news: bool = True      # Включить RSS ленты

    class Config:
        env_file = ".env"


settings = Settings()
