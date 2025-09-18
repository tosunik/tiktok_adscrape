import re
import time
import random
from typing import List, Dict, Optional, Any
from loguru import logger
from datetime import datetime

def is_banking_related(text: str, keywords: List[str]) -> tuple[bool, List[str]]:
    """Metinde bankacılık anahtar kelimesi var mı kontrol et"""
    found_keywords = []
    if not text:
        return False, found_keywords
    
    text_lower = text.lower()
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return len(found_keywords) > 0, found_keywords

def clean_text(text: str) -> str:
    """Metni temizle"""
    if not text:
        return ""
    
    # HTML taglarını temizle
    text = re.sub(r'<[^>]+>', '', text)
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text)
    
    # Baş ve son boşlukları temizle
    text = text.strip()
    
    return text

def extract_urls_from_text(text: str) -> List[str]:
    """Metinden URL'leri çıkar"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def safe_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Güvenli bekleme (random delay)"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def format_datetime(dt: datetime) -> str:
    """Datetime'ı string'e çevir"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """String'den datetime parse et"""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except:
            return None

def create_filename_safe(text: str, max_length: int = 50) -> str:
    """Dosya adı için güvenli string oluştur"""
    # Türkçe karakterleri değiştir
    replacements = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
    }
    
    for tr_char, en_char in replacements.items():
        text = text.replace(tr_char, en_char)
    
    # Sadece harf, rakam, tire ve underscore bırak
    text = re.sub(r'[^a-zA-Z0-9_-]', '_', text)
    
    # Çoklu underscoreları tek yap
    text = re.sub(r'_+', '_', text)
    
    # Baş ve sondaki underscoreları temizle
    text = text.strip('_')
    
    # Maksimum uzunluğa sınırla
    if len(text) > max_length:
        text = text[:max_length]
    
    return text or "untitled"

logger.info("Helper functions loaded")
