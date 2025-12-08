#!/usr/bin/env python3
"""
Platform-Agnostic Scraper Interface
Allows easy extension to TikTok, Spotify, etc. in the future
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


class PlatformScraper(ABC):
    """
    Abstract base class for platform-specific scrapers
    Enables scalability to TikTok, Spotify, etc.
    """
    
    @abstractmethod
    async def initialize(self):
        """Initialize scraper (browser, API client, etc.)"""
        pass
    
    @abstractmethod
    async def close(self):
        """Clean up resources"""
        pass
    
    @abstractmethod
    async def search_content(self, brand_name: str, max_results: int = 50) -> List[Dict]:
        """
        Search platform for content mentioning the brand
        Returns list of content items with codes found
        """
        pass
    
    @abstractmethod
    async def extract_codes(self, content_url: str, brand_name: str) -> List[str]:
        """
        Extract discount codes from a specific piece of content
        Returns list of codes found
        """
        pass
    
    @abstractmethod
    async def extract_creator_info(self, content_url: str) -> Dict[str, Optional[str]]:
        """
        Extract creator information from content
        Returns dict with creator identifiers
        """
        pass
    
    def get_platform_name(self) -> str:
        """Return platform name (YouTube, TikTok, etc.)"""
        return self.__class__.__name__.replace('Scraper', '').lower()


class YouTubeScraperAdapter(PlatformScraper):
    """
    Adapter to make YouTubeScraper conform to PlatformScraper interface
    """
    
    def __init__(self):
        from youtube_scraper import YouTubeScraper
        self.scraper = YouTubeScraper()
    
    async def initialize(self):
        await self.scraper.initialize()
    
    async def close(self):
        await self.scraper.close()
    
    async def search_content(self, brand_name: str, max_results: int = 50) -> List[Dict]:
        return await self.scraper.scrape_brand_videos(brand_name, max_results)
    
    async def extract_codes(self, content_url: str, brand_name: str) -> List[str]:
        video_data = await self.scraper.scrape_video(content_url, brand_name)
        return video_data.get('codes', []) if video_data else []
    
    async def extract_creator_info(self, content_url: str) -> Dict[str, Optional[str]]:
        return await self.scraper._extract_creator_info()
    
    def get_platform_name(self) -> str:
        return 'youtube'


# Future: TikTok Scraper
# class TikTokScraper(PlatformScraper):
#     async def search_content(self, brand_name: str, max_results: int = 50):
#         # TikTok-specific implementation
#         pass

# Future: Spotify Scraper  
# class SpotifyScraper(PlatformScraper):
#     async def search_content(self, brand_name: str, max_results: int = 50):
#         # Spotify podcast ad scraping
#         pass

