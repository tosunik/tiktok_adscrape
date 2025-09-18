#!/usr/bin/env python3
"""
N8N TikTok Ad Scraper Wrapper
Usage: python n8n_tiktok_scraper.py --keywords "banka,kredi" --max-results 50
"""

import sys
import json
import argparse
from pathlib import Path

# Proje modüllerini import et
sys.path.append(str(Path(__file__).parent))
from src.config.settings import settings
from src.scraper.tiktok_scraper import TikTokAdScraper

def main():
    parser = argparse.ArgumentParser(description='TikTok Ad Scraper for N8N')
    parser.add_argument('--keywords', default='banka,kredi,kart,finans', 
                       help='Comma-separated keywords')
    parser.add_argument('--max-results', type=int, default=100,
                       help='Maximum number of ads to scrape')
    parser.add_argument('--output-format', choices=['json', 'n8n'], default='n8n',
                       help='Output format')
    
    args = parser.parse_args()
    
    try:
        # Scraper'ı çalıştır
        scraper = TikTokAdScraper(headless=True)  # N8N'de headless
        keywords = args.keywords.split(',')
        
        result = scraper.search_ads(keywords, args.max_results)
        
        # N8N formatında output
        if args.output_format == 'n8n':
            # N8N'nin beklediği format: array of objects
            n8n_output = []
            
            for ad in scraper.scraped_ads:
                ad_dict = ad.dict()
                
                # N8N için ek meta bilgiler
                ad_dict['n8n_meta'] = {
                    'media_count': len(ad_dict.get('media_urls', [])),
                    'has_video': ad.is_video(),
                    'has_image': ad.is_image(),
                    'is_banking': ad.is_banking_ad,
                    'processing_priority': 'high' if ad.is_banking_ad else 'normal'
                }
                
                n8n_output.append(ad_dict)
            
            # N8N output
            print(json.dumps(n8n_output, ensure_ascii=False, default=str))
            
        else:
            # Standard JSON format
            output = {
                'summary': {
                    'total_ads': result.total_ads,
                    'banking_ads': result.banking_ads,
                    'video_ads': result.video_ads,
                    'image_ads': result.image_ads,
                    'duration_seconds': result.duration_seconds
                },
                'ads': [ad.dict() for ad in scraper.scraped_ads]
            }
            print(json.dumps(output, ensure_ascii=False, default=str))
            
    except Exception as e:
        # N8N error format
        error_output = {
            'error': True,
            'message': str(e),
            'type': type(e).__name__
        }
        print(json.dumps(error_output))
        sys.exit(1)

if __name__ == "__main__":
    main()