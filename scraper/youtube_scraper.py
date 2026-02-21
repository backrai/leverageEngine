#!/usr/bin/env python3
"""
backrAI YouTube Scraper
========================
Scrapes discount codes from YouTube videos (descriptions and closed captions).
Links codes to creators in the database.

PRIMARY: youtube-transcript-api + yt-dlp (no browser, fast, free)
FALLBACK: Playwright browser automation (slow, fragile)
"""

import asyncio
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Set

from dotenv import load_dotenv
from supabase import create_client, Client

# Local imports — no browser dependency
from code_extractor import extract_codes_from_text, extract_codes_with_context
from transcript_service import TranscriptService

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class YouTubeScraper:
    """
    Specialized YouTube scraper for extracting discount codes
    from video descriptions and closed captions.

    Uses TranscriptService (no browser) as primary method.
    Playwright browser automation is available as a fallback.
    """

    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None
        self.found_codes: Set[str] = set()
        self.transcript_svc = TranscriptService

    # ------------------------------------------------------------------
    # Browser lifecycle (only used for fallback)
    # ------------------------------------------------------------------
    async def initialize(self):
        """Initialize Playwright browser (only needed for fallback scraping)."""
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            await self.page.set_extra_http_headers({
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36"
                ),
            })
        except ImportError:
            print("⚠️  Playwright not installed. Browser fallback disabled.")
        except Exception as e:
            print(f"⚠️  Could not launch browser: {e}")

    async def _ensure_browser(self):
        """Ensure browser is running (restart if crashed)."""
        if not self.browser or not self.browser.is_connected():
            await self.initialize()

    async def close(self):
        """Close browser and Playwright."""
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # PRIMARY: No-browser scraping via TranscriptService
    # ------------------------------------------------------------------
    async def scrape_brand_videos(
        self,
        brand_name: str,
        max_videos: int = 50,
    ) -> List[Dict[str, any]]:
        """
        Search YouTube for videos mentioning the brand and extract codes.
        Uses yt-dlp for search + metadata, youtube-transcript-api for transcripts.
        Falls back to Playwright only if needed.
        """
        print(f"\n🔍 Searching YouTube for '{brand_name}' videos...")

        # Primary: Use yt-dlp search (no browser)
        search_query = f"{brand_name} discount code OR coupon code OR promo code"
        videos = self.transcript_svc.search_videos(search_query, max_results=max_videos)

        if not videos:
            print("  ⚠️  No search results from yt-dlp, trying Playwright fallback...")
            return await self._fallback_scrape_brand_videos(brand_name, max_videos)

        print(f"📹 Found {len(videos)} videos (via yt-dlp)")

        videos_with_codes = []
        for i, video in enumerate(videos[:max_videos], 1):
            video_id = video.get("video_id", "")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"\n[{i}/{min(max_videos, len(videos))}] Processing: {video_url}")

            video_data = await self.scrape_video(video_url, brand_name)
            if video_data and video_data.get("codes"):
                videos_with_codes.append(video_data)
                print(f"  ✅ Found {len(video_data['codes'])} code(s)")
            else:
                print(f"  ⚠️  No codes found")

        return videos_with_codes

    async def scrape_video(
        self,
        video_url: str,
        brand_name: str,
    ) -> Optional[Dict[str, any]]:
        """
        Scrape a single YouTube video for discount codes.
        Primary: TranscriptService (no browser).
        Fallback: Playwright browser.
        """
        # Extract video ID from URL
        video_id = self.transcript_svc.extract_video_id(video_url)
        if not video_id:
            print(f"  ⚠️  Could not extract video ID from {video_url}")
            return None

        try:
            # Step 1: Get metadata via yt-dlp (no browser)
            metadata = self.transcript_svc.get_video_metadata(video_id)
            description = ""
            title = ""
            creator_info = {
                "channel_id": None,
                "display_name": None,
                "username": None,
                "channel_url": None,
            }

            if metadata:
                description = metadata.get("description", "") or ""
                title = metadata.get("title", "") or ""
                channel_url = metadata.get("channel_url", "") or ""
                creator_info = {
                    "channel_id": metadata.get("channel_id"),
                    "display_name": metadata.get("channel_name"),
                    "username": _extract_username(channel_url),
                    "channel_url": channel_url,
                }

            # Step 2: Get transcript via youtube-transcript-api (no browser)
            transcript = self.transcript_svc.get_transcript(video_id)
            transcript_text = transcript or ""

            # Step 3: Combine all text and extract codes
            combined_text = "\n\n".join(filter(None, [title, description, transcript_text]))

            if not combined_text.strip():
                # Last resort: try Playwright
                return await self._fallback_scrape_video(video_url, brand_name)

            # Step 4: Extract codes using code_extractor
            description_codes = extract_codes_from_text(description)
            transcript_codes = extract_codes_from_text(transcript_text)
            all_codes = list(set(description_codes + transcript_codes))

            if not all_codes:
                return None

            source = "description" if description_codes else "transcript"

            return {
                "video_url": video_url,
                "video_title": title,
                "video_id": video_id,
                "creator_channel_id": creator_info.get("channel_id"),
                "creator_username": creator_info.get("username"),
                "creator_display_name": creator_info.get("display_name"),
                "creator_channel_url": creator_info.get("channel_url"),
                "codes": all_codes,
                "source": source,
                "scraped_at": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"  ❌ Error scraping video {video_url}: {e}")
            return None

    # ------------------------------------------------------------------
    # FALLBACK: Playwright-based scraping
    # ------------------------------------------------------------------
    async def _fallback_scrape_brand_videos(
        self,
        brand_name: str,
        max_videos: int = 50,
    ) -> List[Dict[str, any]]:
        """Fallback: search YouTube via Playwright browser."""
        await self._ensure_browser()
        if not self.page:
            print("  ❌ No browser available for fallback")
            return []

        search_query = f"{brand_name} discount code OR coupon code OR promo code"
        search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"

        try:
            await self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            await self.page.wait_for_timeout(3000)

            for _ in range(3):
                await self.page.evaluate(
                    "window.scrollTo(0, document.documentElement.scrollHeight)"
                )
                await self.page.wait_for_timeout(2000)

            video_links = await self.page.evaluate("""
                () => {
                    const links = [];
                    document.querySelectorAll('a[href*="/watch"]').forEach(a => {
                        const href = a.getAttribute('href');
                        if (href && href.startsWith('/watch') && !links.includes(href)) {
                            links.push(href);
                        }
                    });
                    return links.slice(0, 50);
                }
            """)

            print(f"📹 Found {len(video_links)} videos (via Playwright)")

            videos_with_codes = []
            for i, video_path in enumerate(video_links[:max_videos], 1):
                video_url = f"https://www.youtube.com{video_path}"
                print(f"\n[{i}/{min(max_videos, len(video_links))}] Processing: {video_url}")

                video_data = await self._fallback_scrape_video(video_url, brand_name)
                if video_data and video_data.get("codes"):
                    videos_with_codes.append(video_data)
                    print(f"  ✅ Found {len(video_data['codes'])} code(s)")
                else:
                    print(f"  ⚠️  No codes found")

                await asyncio.sleep(2)

            return videos_with_codes

        except Exception as e:
            print(f"❌ Error in Playwright fallback: {e}")
            return []

    async def _fallback_scrape_video(
        self,
        video_url: str,
        brand_name: str,
    ) -> Optional[Dict[str, any]]:
        """Fallback: scrape a single video via Playwright browser."""
        await self._ensure_browser()
        if not self.page:
            return None

        try:
            page = await self.browser.new_page()
            try:
                await page.goto(video_url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)

                # Extract metadata
                title = await page.evaluate("""
                    () => {
                        const el = document.querySelector(
                            'h1.ytd-watch-metadata yt-formatted-string, h1.title'
                        );
                        return el ? el.textContent.trim() : '';
                    }
                """)
                video_id = await page.evaluate("""
                    () => new URLSearchParams(window.location.search).get('v') || ''
                """)

                # Click "Show more" for full description
                try:
                    show_more = await page.query_selector(
                        'button[aria-label*="more"], #more'
                    )
                    if show_more:
                        await show_more.click()
                        await page.wait_for_timeout(1000)
                except Exception:
                    pass

                description = await page.evaluate("""
                    () => {
                        const desc = document.querySelector(
                            '#description, ytd-video-secondary-info-renderer #description'
                        );
                        return desc ? desc.textContent : '';
                    }
                """)

                # Extract creator info
                channel_info = await page.evaluate("""
                    () => {
                        const link = document.querySelector(
                            'ytd-channel-name a, #channel-name a'
                        );
                        const href = link ? link.getAttribute('href') : '';
                        const name = link ? link.textContent.trim() : '';
                        let id = '';
                        if (href) {
                            const m = href.match(/channel\\/([^/]+)/)
                                || href.match(/user\\/([^/]+)/)
                                || href.match(/c\\/([^/]+)/);
                            if (m) id = m[1];
                        }
                        return {
                            channel_id: id,
                            display_name: name,
                            channel_url: href ? `https://youtube.com${href}` : ''
                        };
                    }
                """)

                # Extract codes
                all_codes = extract_codes_from_text(description or "")

                if not all_codes:
                    return None

                return {
                    "video_url": video_url,
                    "video_title": title or "",
                    "video_id": video_id or "",
                    "creator_channel_id": channel_info.get("channel_id"),
                    "creator_username": _extract_username(
                        channel_info.get("channel_url", "")
                    ),
                    "creator_display_name": channel_info.get("display_name"),
                    "creator_channel_url": channel_info.get("channel_url"),
                    "codes": all_codes,
                    "source": "description_playwright",
                    "scraped_at": datetime.now().isoformat(),
                }

            finally:
                await page.close()

        except Exception as e:
            print(f"  ❌ Playwright fallback error: {e}")
            return None

    # ------------------------------------------------------------------
    # Database methods (unchanged from original)
    # ------------------------------------------------------------------
    async def match_creator_to_database(
        self,
        youtube_channel_id: Optional[str],
        youtube_username: Optional[str],
        display_name: Optional[str],
    ) -> Optional[str]:
        """
        Match YouTube creator to database creator.
        Returns creator_id if found, None otherwise.
        """
        if not youtube_channel_id and not youtube_username and not display_name:
            return None

        # Try by channel ID first
        if youtube_channel_id:
            result = (
                supabase.table("creators")
                .select("id")
                .eq("youtube_channel_id", youtube_channel_id)
                .execute()
            )
            if result.data:
                return result.data[0]["id"]

        # Try by username
        if youtube_username:
            clean_username = youtube_username.replace("@", "").strip()
            result = (
                supabase.table("creators")
                .select("id")
                .eq("youtube_username", clean_username)
                .execute()
            )
            if result.data:
                return result.data[0]["id"]

        # Try by display name (fuzzy)
        if display_name:
            result = (
                supabase.table("creators")
                .select("id")
                .ilike("display_name", f"%{display_name}%")
                .execute()
            )
            if result.data:
                return result.data[0]["id"]

        return None

    async def create_or_update_creator(
        self,
        youtube_channel_id: Optional[str],
        youtube_username: Optional[str],
        display_name: str,
        channel_url: Optional[str] = None,
    ) -> str:
        """
        Create a new creator in database or update existing one.
        Returns creator_id.
        """
        # Check if creator exists
        existing = None
        if youtube_channel_id:
            result = (
                supabase.table("creators")
                .select("id, youtube_channel_id, youtube_username, youtube_channel_url, display_name")
                .eq("youtube_channel_id", youtube_channel_id)
                .execute()
            )
            if result.data:
                existing = result.data[0]

        if not existing and youtube_username:
            clean_username = youtube_username.replace("@", "").strip()
            result = (
                supabase.table("creators")
                .select("id, youtube_channel_id, youtube_username, youtube_channel_url, display_name")
                .eq("youtube_username", clean_username)
                .execute()
            )
            if result.data:
                existing = result.data[0]

        if existing:
            # Update existing creator with any new info
            update_data = {}
            if youtube_channel_id and not existing.get("youtube_channel_id"):
                update_data["youtube_channel_id"] = youtube_channel_id
            if youtube_username and not existing.get("youtube_username"):
                update_data["youtube_username"] = (
                    youtube_username.replace("@", "").strip()
                )
            if channel_url and not existing.get("youtube_channel_url"):
                update_data["youtube_channel_url"] = channel_url
            if display_name and display_name != existing.get("display_name"):
                update_data["display_name"] = display_name

            if update_data:
                supabase.table("creators").update(update_data).eq(
                    "id", existing["id"]
                ).execute()

            return existing["id"]
        else:
            # Create new creator
            ref_code = (
                youtube_username.replace("@", "").lower().replace(" ", "_")
                if youtube_username
                else display_name.lower().replace(" ", "_")
            )

            creator_data = {
                "display_name": display_name,
                "youtube_channel_id": youtube_channel_id,
                "youtube_username": (
                    youtube_username.replace("@", "").strip()
                    if youtube_username
                    else None
                ),
                "youtube_channel_url": channel_url,
                "affiliate_ref_code": ref_code,
            }

            result = supabase.table("creators").insert(creator_data).execute()
            if result.data:
                print(f"  ✅ Created new creator: {display_name} ({ref_code})")
                return result.data[0]["id"]
            else:
                raise Exception(f"Failed to create creator: {result}")

    async def save_codes_to_database(
        self,
        brand_id: str,
        videos_with_codes: List[Dict[str, any]],
    ) -> int:
        """
        Save all found codes to database.
        Creates/updates creators and offers.
        Returns number of codes saved.
        """
        total_codes_saved = 0

        for video_data in videos_with_codes:
            creator_id = None

            if video_data.get("creator_channel_id") or video_data.get(
                "creator_username"
            ):
                creator_id = await self.match_creator_to_database(
                    video_data.get("creator_channel_id"),
                    video_data.get("creator_username"),
                    video_data.get("creator_display_name"),
                )

                if not creator_id:
                    creator_id = await self.create_or_update_creator(
                        video_data.get("creator_channel_id"),
                        video_data.get("creator_username"),
                        video_data.get("creator_display_name", "Unknown Creator"),
                        video_data.get("creator_channel_url"),
                    )
            else:
                print(f"  ⚠️  No creator info for video, skipping...")
                continue

            for code in video_data.get("codes", []):
                try:
                    existing = (
                        supabase.table("offers")
                        .select("id")
                        .eq("creator_id", creator_id)
                        .eq("brand_id", brand_id)
                        .eq("code", code)
                        .execute()
                    )

                    if existing.data and len(existing.data) > 0:
                        supabase.table("offers").update(
                            {
                                "is_active": True,
                                "updated_at": datetime.now().isoformat(),
                            }
                        ).eq("id", existing.data[0]["id"]).execute()
                        print(f"    ✅ Updated offer: {code}")
                    else:
                        supabase.table("offers").insert(
                            {
                                "creator_id": creator_id,
                                "brand_id": brand_id,
                                "code": code,
                                "discount_amount": "Found on YouTube",
                                "discount_type": "percentage",
                                "is_active": True,
                            }
                        ).execute()
                        print(f"    ✅ Created offer: {code}")
                        total_codes_saved += 1

                except Exception as e:
                    print(f"    ❌ Error saving code {code}: {e}")

        return total_codes_saved


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _extract_username(channel_url: str) -> Optional[str]:
    """Extract @username from a YouTube channel URL."""
    if not channel_url:
        return None
    match = re.search(r"@([A-Za-z0-9_-]+)", channel_url)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
async def scrape_youtube_for_brand(brand_id: str, max_videos: int = 50):
    """Main function to scrape YouTube for a specific brand."""
    scraper = YouTubeScraper()

    try:
        # Get brand info
        brand_response = (
            supabase.table("brands")
            .select("id, name, domain_pattern")
            .eq("id", brand_id)
            .execute()
        )

        if not brand_response.data or len(brand_response.data) == 0:
            print(f"❌ Brand with ID {brand_id} not found")
            return

        brand = brand_response.data[0]
        brand_name = brand["name"]

        print(f"\n{'='*60}")
        print(f"🎬 YouTube Scraper for {brand_name}")
        print(f"   Primary: TranscriptService (no browser)")
        print(f"   Fallback: Playwright browser")
        print(f"{'='*60}\n")

        # Scrape videos (no browser needed for primary path)
        videos_with_codes = await scraper.scrape_brand_videos(
            brand_name, max_videos
        )

        if not videos_with_codes:
            print(f"\n⚠️  No codes found for {brand_name}")
            return

        print(f"\n📊 Summary:")
        print(f"  Videos processed: {len(videos_with_codes)}")
        total_codes = sum(len(v.get("codes", [])) for v in videos_with_codes)
        print(f"  Total codes found: {total_codes}")

        # Save to database
        print(f"\n💾 Saving to database...")
        codes_saved = await scraper.save_codes_to_database(
            brand_id, videos_with_codes
        )

        print(f"\n✅ Complete! Saved {codes_saved} new code(s) to database")

    finally:
        await scraper.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python youtube_scraper.py <brand_id> [max_videos]")
        print("Example: python youtube_scraper.py abc-123-def 50")
        sys.exit(1)

    brand_id = sys.argv[1]
    max_videos = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    asyncio.run(scrape_youtube_for_brand(brand_id, max_videos))
