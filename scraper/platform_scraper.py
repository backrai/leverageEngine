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

    # ------------------------------------------------------------------
    # Creator-centric methods (new — the core of backrAI)
    # ------------------------------------------------------------------
    def discover_creators(
        self, queries: Optional[List[str]] = None, max_results: int = 20
    ) -> List[Dict]:
        """
        Discover content creators on this platform.
        Returns list of creator discovery dicts.
        Default implementation returns empty — subclasses should override.
        """
        return []

    def extract_creator_codes(
        self, creator_id: str, max_content: int = 20
    ) -> List[Dict]:
        """
        Extract discount/affiliate codes from a specific creator's content.
        Returns list of {code, brand, context} dicts.
        Default implementation returns empty — subclasses should override.
        """
        return []


class YouTubeScraperAdapter(PlatformScraper):
    """
    Adapter to make YouTubeScraper conform to PlatformScraper interface.
    Uses TranscriptService (no browser) as primary method.
    """

    def __init__(self):
        from youtube_scraper import YouTubeScraper
        self.scraper = YouTubeScraper()

    async def initialize(self):
        # No browser needed for primary path — only initialize on demand
        pass

    async def close(self):
        await self.scraper.close()

    async def search_content(self, brand_name: str, max_results: int = 50) -> List[Dict]:
        return await self.scraper.scrape_brand_videos(brand_name, max_results)

    async def extract_codes(self, content_url: str, brand_name: str) -> List[str]:
        video_data = await self.scraper.scrape_video(content_url, brand_name)
        return video_data.get('codes', []) if video_data else []

    async def extract_creator_info(self, content_url: str) -> Dict[str, Optional[str]]:
        from transcript_service import TranscriptService
        video_id = TranscriptService.extract_video_id(content_url)
        if video_id:
            metadata = TranscriptService.get_video_metadata(video_id)
            if metadata:
                return {
                    'channel_id': metadata.get('channel_id'),
                    'display_name': metadata.get('channel_name'),
                    'channel_url': metadata.get('channel_url'),
                    'username': None,
                }
        return {'channel_id': None, 'display_name': None, 'channel_url': None, 'username': None}

    def discover_creators(
        self, queries: Optional[List[str]] = None, max_results: int = 20
    ) -> List[Dict]:
        """Discover creators via YouTube search using creator_discovery engine."""
        from creator_discovery import CreatorDiscovery
        engine = CreatorDiscovery()
        return engine.discover_via_search(
            queries=queries, max_results_per_query=max_results
        )

    def extract_creator_codes(
        self, creator_id: str, max_content: int = 20
    ) -> List[Dict]:
        """Extract codes from a creator's recent YouTube videos."""
        from creator_discovery import CreatorDiscovery
        engine = CreatorDiscovery()
        # creator_id here could be a channel URL
        return engine.discover_from_channel(
            channel_url=creator_id, max_videos=max_content
        )

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

