import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Scraper konfigürasyon ayarları"""
    
    # TikTok API Settings
    tiktok_base_url: str = os.getenv("TIKTOK_BASE_URL", "https://library.tiktok.com")
    tiktok_api_version: str = os.getenv("TIKTOK_API_VERSION", "v1")
    tiktok_country: str = os.getenv("TIKTOK_COUNTRY", "TR")
    tiktok_session_timeout: int = int(os.getenv("TIKTOK_SESSION_TIMEOUT", "300"))
    tiktok_max_ads_per_search: int = int(os.getenv("TIKTOK_MAX_ADS_PER_SEARCH", "200"))
    
    # Proxy Settings
    use_proxies: bool = os.getenv("USE_PROXIES", "false").lower() == "true"
    proxy_rotation_interval: int = int(os.getenv("PROXY_ROTATION_INTERVAL", "10"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Rate Limiting
    requests_per_minute: int = int(os.getenv("REQUESTS_PER_MINUTE", "30"))
    delay_between_requests: int = int(os.getenv("DELAY_BETWEEN_REQUESTS", "2"))
    
    # Database
    db_type: str = os.getenv("DB_TYPE", "sqlite")
    db_url: str = os.getenv("DB_URL", "sqlite:///data\\ads.db")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs\\scraper.log")
    
    # Banking Keywords
    banking_keywords: List[str] = os.getenv("BANKING_KEYWORDS", "").split(",")
    
    # File Paths (Windows uyumlu)
    media_download_path: str = os.getenv("MEDIA_DOWNLOAD_PATH", "data\\media")
    raw_data_path: str = os.getenv("RAW_DATA_PATH", "data\\raw")
    processed_data_path: str = os.getenv("PROCESSED_DATA_PATH", "data\\processed")
    
    # User Agents
    rotate_user_agents: bool = os.getenv("ROTATE_USER_AGENTS", "true").lower() == "true"
    
    # Turkish Banking Companies
    turkish_banks: List[str] = [
        "garanti", "isbank", "yapikredi", "akbank", "halkbank", "vakifbank",
        "denizbank", "ingbank", "teb", "finansbank", "kuveytturk", "albaraka",
        "papara", "ininal", "tosla", "param", "paratica", "ziraat"
    ]
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings() 
