from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class MediaType(str, Enum):
    """Reklam medya türleri"""
    VIDEO = "video"
    IMAGE = "image" 
    TEXT = "text"

class AdStatus(str, Enum):
    """Reklam durumu"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class TikTokAd(BaseModel):
    """TikTok Reklam Veri Modeli"""
    
    # Temel Bilgiler
    ad_id: str = Field(..., description="Reklam ID")
    advertiser_name: str = Field(..., description="Reklam veren ismi")
    advertiser_id: Optional[str] = Field(None, description="Reklam veren ID")
    
    # İçerik
    ad_text: Optional[str] = Field(None, description="Reklam metni")
    headline: Optional[str] = Field(None, description="Başlık")
    description: Optional[str] = Field(None, description="Açıklama")
    call_to_action: Optional[str] = Field(None, description="Eylem çağrısı")
    
    # Medya
    media_type: MediaType = Field(..., description="Medya türü")
    media_urls: List[str] = Field(default_factory=list, description="Medya URL'leri")
    thumbnail_url: Optional[str] = Field(None, description="Küçük resim URL")
    
    # Banking specific fields
    is_banking_ad: bool = Field(default=False, description="Bankacılık reklamı mı")
    banking_keywords_found: List[str] = Field(default_factory=list, description="Bulunan bankacılık anahtar kelimeleri")
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now, description="Scrape edilme tarihi")
    source_url: Optional[str] = Field(None, description="Kaynak URL")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Ham veri")
    
    def is_video(self) -> bool:
        return self.media_type == MediaType.VIDEO
    
    def is_image(self) -> bool:
        return self.media_type == MediaType.IMAGE

class ScrapingResult(BaseModel):
    """Scraping sonuç modeli"""
    
    total_ads: int = 0
    banking_ads: int = 0
    video_ads: int = 0
    image_ads: int = 0
    text_ads: int = 0
    failed_ads: int = 0
    
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    def complete(self):
        """Scraping'i tamamla"""
        self.end_time = datetime.now()
        if self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def add_error(self, error: str):
        """Hata ekle"""
        self.errors.append(f"{datetime.now()}: {error}")
    
    def add_warning(self, warning: str):
        """Uyarı ekle"""
        self.warnings.append(f"{datetime.now()}: {warning}")