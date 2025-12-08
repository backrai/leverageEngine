#!/usr/bin/env python3
"""
backrAI YouTube Scraper
Scrapes discount codes from YouTube videos (descriptions and closed captions)
Links codes to creators in the database
"""

import asyncio
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Set
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, Page
from supabase import create_client, Client
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class YouTubeScraper:
    """
    Specialized YouTube scraper for extracting discount codes
    from video descriptions and closed captions
    """

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.found_codes: Set[str] = set()  # Track unique codes

    async def initialize(self):
        """Initialize browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        # Set user agent to avoid detection
        await self.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()

    async def scrape_brand_videos(
        self, 
        brand_name: str, 
        max_videos: int = 50
    ) -> List[Dict[str, any]]:
        """
        Search YouTube for videos mentioning the brand
        Returns list of video data with codes found
        """
        print(f"\n🔍 Searching YouTube for '{brand_name}' videos...")
        
        # Search YouTube
        search_query = f"{brand_name} discount code OR coupon code OR promo code"
        search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
        
        try:
            await self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            await self.page.wait_for_timeout(3000)  # Wait for results to load
            
            # Scroll to load more videos
            for _ in range(3):
                await self.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                await self.page.wait_for_timeout(2000)
            
            # Extract video links
            video_links = await self.page.evaluate("""
                () => {
                    const links = [];
                    document.querySelectorAll('a[href*="/watch"]').forEach(a => {
                        const href = a.getAttribute('href');
                        if (href && href.startsWith('/watch') && !links.includes(href)) {
                            links.push(href);
                        }
                    });
                    return links.slice(0, 50); // Limit to 50 videos
                }
            """)
            
            print(f"📹 Found {len(video_links)} videos")
            
            videos_with_codes = []
            for i, video_path in enumerate(video_links[:max_videos], 1):
                video_url = f"https://www.youtube.com{video_path}"
                print(f"\n[{i}/{min(max_videos, len(video_links))}] Processing: {video_url}")
                
                video_data = await self.scrape_video(video_url, brand_name)
                if video_data and video_data.get('codes'):
                    videos_with_codes.append(video_data)
                    print(f"  ✅ Found {len(video_data['codes'])} code(s)")
                else:
                    print(f"  ⚠️  No codes found")
                
                # Rate limiting
                await asyncio.sleep(2)
            
            return videos_with_codes
            
        except Exception as e:
            print(f"❌ Error searching YouTube: {e}")
            return []

    async def scrape_video(
        self, 
        video_url: str, 
        brand_name: str
    ) -> Optional[Dict[str, any]]:
        """
        Scrape a single YouTube video for discount codes
        Extracts from description and closed captions
        """
        try:
            await self.page.goto(video_url, wait_until="networkidle", timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # Extract video metadata
            video_data = await self._extract_video_metadata()
            
            # Extract codes from description
            description_codes = await self._extract_codes_from_description()
            
            # Extract codes from closed captions
            cc_codes = await self._extract_codes_from_captions()
            
            # Combine and deduplicate codes
            all_codes = list(set(description_codes + cc_codes))
            
            # Filter codes that mention the brand
            brand_codes = [
                code for code in all_codes 
                if self._code_mentions_brand(code, brand_name)
            ]
            
            if not brand_codes:
                return None
            
            # Extract creator info
            creator_info = await self._extract_creator_info()
            
            return {
                'video_url': video_url,
                'video_title': video_data.get('title', ''),
                'video_id': video_data.get('video_id', ''),
                'creator_channel_id': creator_info.get('channel_id'),
                'creator_username': creator_info.get('username'),
                'creator_display_name': creator_info.get('display_name'),
                'codes': brand_codes,
                'source': 'description' if description_codes else 'captions',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  ❌ Error scraping video {video_url}: {e}")
            return None

    async def _extract_video_metadata(self) -> Dict[str, str]:
        """Extract video title and ID"""
        try:
            title = await self.page.evaluate("""
                () => {
                    const titleEl = document.querySelector('h1.ytd-watch-metadata yt-formatted-string, h1.title');
                    return titleEl ? titleEl.textContent.trim() : '';
                }
            """)
            
            video_id = await self.page.evaluate("""
                () => {
                    const urlParams = new URLSearchParams(window.location.search);
                    return urlParams.get('v') || '';
                }
            """)
            
            return {'title': title, 'video_id': video_id}
        except:
            return {'title': '', 'video_id': ''}

    async def _extract_codes_from_description(self) -> List[str]:
        """Extract discount codes from video description"""
        try:
            # Click "Show more" if it exists
            try:
                show_more = await self.page.query_selector('button[aria-label*="more"], #more')
                if show_more:
                    await show_more.click()
                    await self.page.wait_for_timeout(1000)
            except:
                pass
            
            # Get description text
            description = await self.page.evaluate("""
                () => {
                    const desc = document.querySelector('#description, ytd-video-secondary-info-renderer #description');
                    return desc ? desc.textContent : '';
                }
            """)
            
            return self._extract_codes_from_text(description)
            
        except Exception as e:
            print(f"    ⚠️  Error extracting description: {e}")
            return []

    async def _extract_codes_from_captions(self) -> List[str]:
        """Extract discount codes from closed captions"""
        try:
            # Try to enable captions
            # Look for CC button
            cc_button = await self.page.query_selector('button[aria-label*="Subtitles"], button[aria-label*="CC"]')
            if cc_button:
                await cc_button.click()
                await self.page.wait_for_timeout(2000)
            
            # Extract caption text
            caption_text = await self.page.evaluate("""
                () => {
                    const captions = [];
                    document.querySelectorAll('.caption-window, .ytp-caption-window-container').forEach(el => {
                        captions.push(el.textContent);
                    });
                    return captions.join(' ');
                }
            """)
            
            # Alternative: Try to get captions via API if available
            if not caption_text:
                # YouTube stores captions in a specific format
                # This is a fallback - may need to use YouTube Data API for better results
                caption_text = await self.page.evaluate("""
                    () => {
                        // Try to find caption track data
                        const scripts = Array.from(document.querySelectorAll('script'));
                        for (const script of scripts) {
                            const text = script.textContent || '';
                            if (text.includes('captionTracks')) {
                                try {
                                    const match = text.match(/captionTracks[^}]+}/);
                                    if (match) {
                                        return text; // Return raw for parsing
                                    }
                                } catch(e) {}
                            }
                        }
                        return '';
                    }
                """)
            
            return self._extract_codes_from_text(caption_text)
            
        except Exception as e:
            print(f"    ⚠️  Error extracting captions: {e}")
            return []

    def _extract_codes_from_text(self, text: str) -> List[str]:
        """
        Extract discount codes from text using multiple patterns
        Looks for common code formats
        """
        if not text:
            return []
        
        codes = []
        
        # Pattern 1: "CODE: ABC123" or "Code: ABC123"
        pattern1 = re.compile(r'(?:code|promo|discount|coupon)[\s:]*([A-Z0-9]{4,20})', re.IGNORECASE)
        codes.extend(pattern1.findall(text))
        
        # Pattern 2: "Use code ABC123" or "Enter ABC123"
        pattern2 = re.compile(r'(?:use|enter|try)[\s]+(?:code|promo)?[\s]*([A-Z0-9]{4,20})', re.IGNORECASE)
        codes.extend(pattern2.findall(text))
        
        # Pattern 3: Standalone codes (all caps, 4-20 chars, alphanumeric)
        pattern3 = re.compile(r'\b([A-Z]{2,}[0-9]{2,}|[A-Z0-9]{4,20})\b')
        potential_codes = pattern3.findall(text)
        
        # Filter potential codes (must be uppercase, reasonable length)
        for code in potential_codes:
            if code.isupper() and 4 <= len(code) <= 20 and code.isalnum():
                # Exclude common false positives
                if code not in ['HTTP', 'HTTPS', 'WWW', 'COM', 'ORG', 'NET']:
                    codes.append(code)
        
        # Deduplicate and clean
        unique_codes = list(set([c.upper().strip() for c in codes if c]))
        
        return unique_codes

    def _code_mentions_brand(self, code: str, brand_name: str) -> bool:
        """Check if code context mentions the brand"""
        # This is a simple check - in production, you'd want more context
        # For now, we'll accept all codes found in brand-related videos
        return True  # Accept all codes from brand search results

    async def _extract_creator_info(self) -> Dict[str, Optional[str]]:
        """Extract creator/channel information from video page"""
        try:
            # Get channel ID and name
            channel_info = await self.page.evaluate("""
                () => {
                    const channelLink = document.querySelector('ytd-channel-name a, #channel-name a');
                    const channelId = channelLink ? channelLink.getAttribute('href') : '';
                    const channelName = channelLink ? channelLink.textContent.trim() : '';
                    
                    // Extract channel ID from URL
                    let id = '';
                    if (channelId) {
                        const match = channelId.match(/channel\\/([^/]+)/) || channelId.match(/user\\/([^/]+)/) || channelId.match(/c\\/([^/]+)/);
                        if (match) id = match[1];
                    }
                    
                    return {
                        channel_id: id,
                        display_name: channelName,
                        channel_url: channelId ? `https://youtube.com${channelId}` : ''
                    };
                }
            """)
            
            # Try to get username from channel page
            username = None
            if channel_info.get('channel_url'):
                try:
                    await self.page.goto(f"https://youtube.com{channel_info.get('channel_url', '')}", wait_until="networkidle", timeout=10000)
                    await self.page.wait_for_timeout(2000)
                    username = await self.page.evaluate("""
                        () => {
                            const handle = document.querySelector('#channel-handle, yt-formatted-string#channel-handle');
                            return handle ? handle.textContent.trim() : null;
                        }
                    """)
                except:
                    pass
            
            return {
                'channel_id': channel_info.get('channel_id'),
                'display_name': channel_info.get('display_name'),
                'username': username,
                'channel_url': channel_info.get('channel_url')
            }
            
        except Exception as e:
            print(f"    ⚠️  Error extracting creator info: {e}")
            return {
                'channel_id': None,
                'display_name': None,
                'username': None,
                'channel_url': None
            }

    async def match_creator_to_database(
        self, 
        youtube_channel_id: Optional[str],
        youtube_username: Optional[str],
        display_name: Optional[str]
    ) -> Optional[str]:
        """
        Match YouTube creator to database creator
        Returns creator_id if found, None otherwise
        """
        if not youtube_channel_id and not youtube_username and not display_name:
            return None
        
        # Try to find by channel ID first
        if youtube_channel_id:
            result = supabase.table("creators").select("id").eq("youtube_channel_id", youtube_channel_id).execute()
            if result.data:
                return result.data[0]['id']
        
        # Try to find by username
        if youtube_username:
            # Clean username (remove @ if present)
            clean_username = youtube_username.replace('@', '').strip()
            result = supabase.table("creators").select("id").eq("youtube_username", clean_username).execute()
            if result.data:
                return result.data[0]['id']
        
        # Try to find by display name (fuzzy match)
        if display_name:
            result = supabase.table("creators").select("id").ilike("display_name", f"%{display_name}%").execute()
            if result.data:
                return result.data[0]['id']
        
        return None

    async def create_or_update_creator(
        self,
        youtube_channel_id: Optional[str],
        youtube_username: Optional[str],
        display_name: str,
        channel_url: Optional[str] = None
    ) -> str:
        """
        Create a new creator in database or update existing one
        Returns creator_id
        """
        # Check if creator exists
        existing = None
        if youtube_channel_id:
            result = supabase.table("creators").select("id").eq("youtube_channel_id", youtube_channel_id).execute()
            if result.data:
                existing = result.data[0]
        
        if not existing and youtube_username:
            clean_username = youtube_username.replace('@', '').strip()
            result = supabase.table("creators").select("id").eq("youtube_username", clean_username).execute()
            if result.data:
                existing = result.data[0]
        
        if existing:
            # Update existing creator
            update_data = {}
            if youtube_channel_id and not existing.get('youtube_channel_id'):
                update_data['youtube_channel_id'] = youtube_channel_id
            if youtube_username and not existing.get('youtube_username'):
                update_data['youtube_username'] = youtube_username.replace('@', '').strip()
            if channel_url and not existing.get('youtube_channel_url'):
                update_data['youtube_channel_url'] = channel_url
            if display_name and display_name != existing.get('display_name'):
                update_data['display_name'] = display_name
            
            if update_data:
                result = supabase.table("creators").update(update_data).eq("id", existing['id']).execute()
            
            return existing['id']
        else:
            # Create new creator
            # Generate affiliate_ref_code from username or display_name
            ref_code = youtube_username.replace('@', '').lower().replace(' ', '_') if youtube_username else display_name.lower().replace(' ', '_')
            
            creator_data = {
                'display_name': display_name,
                'youtube_channel_id': youtube_channel_id,
                'youtube_username': youtube_username.replace('@', '').strip() if youtube_username else None,
                'youtube_channel_url': channel_url,
                'affiliate_ref_code': ref_code
            }
            
            result = supabase.table("creators").insert(creator_data).execute()
            if result.data:
                print(f"  ✅ Created new creator: {display_name} ({ref_code})")
                return result.data[0]['id']
            else:
                raise Exception(f"Failed to create creator: {result}")

    async def save_codes_to_database(
        self,
        brand_id: str,
        videos_with_codes: List[Dict[str, any]]
    ) -> int:
        """
        Save all found codes to database
        Creates/updates creators and offers
        Returns number of codes saved
        """
        total_codes_saved = 0
        
        for video_data in videos_with_codes:
            creator_id = None
            
            # Try to match or create creator
            if video_data.get('creator_channel_id') or video_data.get('creator_username'):
                # Try to match existing creator
                creator_id = await self.match_creator_to_database(
                    video_data.get('creator_channel_id'),
                    video_data.get('creator_username'),
                    video_data.get('creator_display_name')
                )
                
                # If not found, create new creator
                if not creator_id:
                    creator_id = await self.create_or_update_creator(
                        video_data.get('creator_channel_id'),
                        video_data.get('creator_username'),
                        video_data.get('creator_display_name', 'Unknown Creator'),
                        video_data.get('creator_channel_url')
                    )
            else:
                # No creator info - use default creator or skip
                print(f"  ⚠️  No creator info for video, skipping...")
                continue
            
            # Save each code as an offer
            for code in video_data.get('codes', []):
                try:
                    # Check if offer already exists
                    existing = supabase.table("offers").select("id").eq(
                        "creator_id", creator_id
                    ).eq("brand_id", brand_id).eq("code", code).execute()
                    
                    if existing.data and len(existing.data) > 0:
                        # Update existing offer
                        supabase.table("offers").update({
                            "is_active": True,
                            "updated_at": datetime.now().isoformat()
                        }).eq("id", existing.data[0]['id']).execute()
                        print(f"    ✅ Updated offer: {code}")
                    else:
                        # Create new offer
                        supabase.table("offers").insert({
                            "creator_id": creator_id,
                            "brand_id": brand_id,
                            "code": code,
                            "discount_amount": "Found on YouTube",  # Default, can be improved
                            "discount_type": "percentage",
                            "is_active": True
                        }).execute()
                        print(f"    ✅ Created offer: {code}")
                        total_codes_saved += 1
                        
                except Exception as e:
                    print(f"    ❌ Error saving code {code}: {e}")
        
        return total_codes_saved


async def scrape_youtube_for_brand(brand_id: str, max_videos: int = 50):
    """
    Main function to scrape YouTube for a specific brand
    """
    scraper = YouTubeScraper()
    await scraper.initialize()
    
    try:
        # Get brand info
        brand_response = supabase.table("brands").select("id, name, domain_pattern").eq("id", brand_id).execute()
        
        if not brand_response.data or len(brand_response.data) == 0:
            print(f"❌ Brand with ID {brand_id} not found")
            return
        
        brand = brand_response.data[0]
        brand_name = brand['name']
        
        print(f"\n{'='*60}")
        print(f"🎬 YouTube Scraper for {brand_name}")
        print(f"{'='*60}\n")
        
        # Scrape videos
        videos_with_codes = await scraper.scrape_brand_videos(brand_name, max_videos)
        
        if not videos_with_codes:
            print(f"\n⚠️  No codes found for {brand_name}")
            return
        
        print(f"\n📊 Summary:")
        print(f"  Videos processed: {len(videos_with_codes)}")
        total_codes = sum(len(v.get('codes', [])) for v in videos_with_codes)
        print(f"  Total codes found: {total_codes}")
        
        # Save to database
        print(f"\n💾 Saving to database...")
        codes_saved = await scraper.save_codes_to_database(brand_id, videos_with_codes)
        
        print(f"\n✅ Complete! Saved {codes_saved} new code(s) to database")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python youtube_scraper.py <brand_id> [max_videos]")
        print("Example: python youtube_scraper.py abc-123-def 50")
        sys.exit(1)
    
    brand_id = sys.argv[1]
    max_videos = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    asyncio.run(scrape_youtube_for_brand(brand_id, max_videos))
