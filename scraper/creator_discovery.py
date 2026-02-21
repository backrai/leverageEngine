#!/usr/bin/env python3
"""
backrAI Creator Discovery Engine
=================================
Creator-centric discovery that finds content creators, extracts their
affiliate/discount codes from video transcripts and descriptions, and
links each code to the creator + brand.

This is the CORE of backrAI's value proposition:
Every code must trace back to a specific creator so the browser extension
can attribute the sale and the creator gets their commission.

Three Discovery Strategies:
  A) YouTube Search — find creators via sponsor-related search queries
  B) SponsorBlock Pre-filter — only process videos confirmed to have sponsors
  C) Channel Snowball — scrape known creators' recent videos for codes

Usage:
  python creator_discovery.py
  python creator_discovery.py --strategies search,channel --max-results 15
  python creator_discovery.py --strategies channel --seed-only
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime
from typing import Optional, Dict, List, Set, Tuple

from dotenv import load_dotenv
from supabase import create_client, Client

# Local imports (same directory)
from code_extractor import (
    extract_codes_from_text,
    extract_codes_with_context,
    extract_brand_indicators,
    match_code_to_brand,
)
from transcript_service import TranscriptService
from sponsorblock_service import SponsorBlockService


# ---------------------------------------------------------------------------
# Supabase setup
# ---------------------------------------------------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def _get_supabase() -> Client:
    """Create Supabase client. Raises if env vars missing."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment"
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------------------------------------------------------------------
# Creator-centric search queries (Strategy A)
# ---------------------------------------------------------------------------
CREATOR_SEARCH_QUERIES = [
    # Direct code mentions
    "my discount codes 2025",
    "my promo codes compilation",
    "all my discount codes",
    "creator discount codes haul",
    "my brand deals and codes",
    # Niche-specific (high sponsor density)
    "fitness influencer discount codes",
    "tech reviewer sponsor codes",
    "beauty guru discount codes 2025",
    "gaming setup discount codes",
    "fashion haul discount codes",
    # Sponsor-related
    "today's video is sponsored by",
    "use my code for percent off",
    "link in description discount",
    "affiliate codes I use",
    "brands that sponsor me",
    # Platform-specific
    "youtube sponsor segment codes",
    "best creator deals 2025",
    "influencer promo codes that work",
]


# ---------------------------------------------------------------------------
# Seed creators for Strategy C (channel snowball)
# ---------------------------------------------------------------------------
SEED_CREATORS = [
    # Tech
    {"name": "MKBHD", "channel_url": "https://www.youtube.com/@mkbhd"},
    {"name": "Linus Tech Tips", "channel_url": "https://www.youtube.com/@LinusTechTips"},
    {"name": "Unbox Therapy", "channel_url": "https://www.youtube.com/@UnboxTherapy"},
    {"name": "iJustine", "channel_url": "https://www.youtube.com/@ijustine"},
    {"name": "Dave2D", "channel_url": "https://www.youtube.com/@Dave2D"},
    {"name": "Mrwhosetheboss", "channel_url": "https://www.youtube.com/@Mrwhosetheboss"},
    {"name": "Austin Evans", "channel_url": "https://www.youtube.com/@austinevans"},
    {"name": "JerryRigEverything", "channel_url": "https://www.youtube.com/@JerryRigEverything"},
    # Fitness
    {"name": "Chris Bumstead", "channel_url": "https://www.youtube.com/@cbum"},
    {"name": "Jeff Nippard", "channel_url": "https://www.youtube.com/@JeffNippard"},
    {"name": "Natacha Oceane", "channel_url": "https://www.youtube.com/@natachaoceane"},
    {"name": "Will Tennyson", "channel_url": "https://www.youtube.com/@WillTennyson"},
    {"name": "Greg Doucette", "channel_url": "https://www.youtube.com/@GregDoucette"},
    {"name": "Sam Sulek", "channel_url": "https://www.youtube.com/@SamSulek"},
    # Beauty / Fashion
    {"name": "NikkieTutorials", "channel_url": "https://www.youtube.com/@NikkieTutorials"},
    {"name": "James Charles", "channel_url": "https://www.youtube.com/@jamescharles"},
    {"name": "Jackie Aina", "channel_url": "https://www.youtube.com/@jackieaina"},
    {"name": "Hyram", "channel_url": "https://www.youtube.com/@Hyram"},
    {"name": "Alexandra Anele", "channel_url": "https://www.youtube.com/@AlexandraAnele"},
    # Mega creators (high sponsor volume)
    {"name": "MrBeast", "channel_url": "https://www.youtube.com/@MrBeast"},
    {"name": "Mark Rober", "channel_url": "https://www.youtube.com/@MarkRober"},
    {"name": "Dude Perfect", "channel_url": "https://www.youtube.com/@DudePerfect"},
    {"name": "PewDiePie", "channel_url": "https://www.youtube.com/@PewDiePie"},
    {"name": "Logan Paul", "channel_url": "https://www.youtube.com/@loganpaulvlogs"},
    # Finance / Education
    {"name": "Graham Stephan", "channel_url": "https://www.youtube.com/@GrahamStephan"},
    {"name": "Andrei Jikh", "channel_url": "https://www.youtube.com/@AndreiJikh"},
    {"name": "Ali Abdaal", "channel_url": "https://www.youtube.com/@aliabdaal"},
    {"name": "Thomas Frank", "channel_url": "https://www.youtube.com/@Thomasfrank"},
    # Gaming
    {"name": "Jacksepticeye", "channel_url": "https://www.youtube.com/@jacksepticeye"},
    {"name": "Pokimane", "channel_url": "https://www.youtube.com/@pokimane"},
    {"name": "DrDisRespect", "channel_url": "https://www.youtube.com/@DrDisRespect"},
    {"name": "Valkyrae", "channel_url": "https://www.youtube.com/@Valkyrae"},
    # Lifestyle / Vlogs
    {"name": "Casey Neistat", "channel_url": "https://www.youtube.com/@casey"},
    {"name": "Emma Chamberlain", "channel_url": "https://www.youtube.com/@emmachamberlain"},
    {"name": "David Dobrik", "channel_url": "https://www.youtube.com/@daviddobrik"},
    # Food
    {"name": "Binging with Babish", "channel_url": "https://www.youtube.com/@baborish"},
    {"name": "Joshua Weissman", "channel_url": "https://www.youtube.com/@JoshuaWeissman"},
    # Podcasters
    {"name": "Joe Rogan", "channel_url": "https://www.youtube.com/@joerogan"},
    {"name": "Lex Fridman", "channel_url": "https://www.youtube.com/@lexfridman"},
    {"name": "Andrew Huberman", "channel_url": "https://www.youtube.com/@hubaboratoryclips"},
]


# ---------------------------------------------------------------------------
# CreatorDiscovery
# ---------------------------------------------------------------------------
class CreatorDiscovery:
    """
    Creator-centric discovery engine.
    Finds creators → extracts their codes → links to brands → saves to DB.
    """

    def __init__(self, supabase_client: Optional[Client] = None):
        self.supabase = supabase_client or _get_supabase()
        self.transcript_svc = TranscriptService
        self.sponsorblock_svc = SponsorBlockService()
        self._known_brands_cache: Optional[List[Dict]] = None
        self._known_creator_ids: Optional[Set[str]] = None

        # Stats
        self.stats = {
            "videos_processed": 0,
            "creators_found": 0,
            "creators_new": 0,
            "codes_found": 0,
            "codes_saved": 0,
            "brands_matched": 0,
            "brands_created": 0,
            "errors": 0,
        }

    # ------------------------------------------------------------------
    # Brand cache (loaded once, used for code→brand matching)
    # ------------------------------------------------------------------
    def _load_known_brands(self) -> List[Dict]:
        """Load all brands from DB for code matching."""
        if self._known_brands_cache is not None:
            return self._known_brands_cache
        try:
            result = (
                self.supabase.table("brands")
                .select("id, name, domain_pattern")
                .execute()
            )
            self._known_brands_cache = result.data or []
            print(f"   Loaded {len(self._known_brands_cache)} known brands from DB")
        except Exception as e:
            print(f"   Warning: Could not load brands: {e}")
            self._known_brands_cache = []
        return self._known_brands_cache

    def _load_known_creator_channel_ids(self) -> Set[str]:
        """Load known creator YouTube channel IDs for dedup."""
        if self._known_creator_ids is not None:
            return self._known_creator_ids
        try:
            result = (
                self.supabase.table("creators")
                .select("youtube_channel_id")
                .not_.is_("youtube_channel_id", "null")
                .execute()
            )
            self._known_creator_ids = {
                row["youtube_channel_id"]
                for row in (result.data or [])
                if row.get("youtube_channel_id")
            }
            print(f"   Loaded {len(self._known_creator_ids)} known creator channel IDs")
        except Exception as e:
            print(f"   Warning: Could not load creators: {e}")
            self._known_creator_ids = set()
        return self._known_creator_ids

    # ==================================================================
    # STRATEGY A — YouTube Search Discovery
    # ==================================================================
    def discover_via_search(
        self,
        queries: Optional[List[str]] = None,
        max_results_per_query: int = 10,
    ) -> List[Dict]:
        """
        Search YouTube for creator content with discount codes.
        Returns list of discovery dicts ready for save_discoveries().
        """
        queries = queries or CREATOR_SEARCH_QUERIES
        all_discoveries = []
        seen_video_ids: Set[str] = set()

        print(f"\n{'='*60}")
        print(f"Strategy A: YouTube Search Discovery")
        print(f"  Queries: {len(queries)}")
        print(f"  Max results per query: {max_results_per_query}")
        print(f"{'='*60}")

        for i, query in enumerate(queries):
            print(f"\n  [{i+1}/{len(queries)}] Searching: \"{query}\"")
            try:
                videos = self.transcript_svc.search_videos(
                    query, max_results=max_results_per_query
                )
                print(f"    Found {len(videos)} videos")

                for video in videos:
                    video_id = video.get("video_id", "")
                    if not video_id or video_id in seen_video_ids:
                        continue
                    seen_video_ids.add(video_id)

                    discovery = self._process_video(video_id, video)
                    if discovery and discovery.get("codes"):
                        all_discoveries.append(discovery)
                        print(
                            f"    ✅ {discovery['creator_name']}: "
                            f"{len(discovery['codes'])} codes "
                            f"({', '.join(c['code'] for c in discovery['codes'][:3])})"
                        )

                # Be respectful with rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"    Error on query '{query}': {e}")
                self.stats["errors"] += 1

        print(f"\n  Search complete: {len(all_discoveries)} videos with codes")
        return all_discoveries

    # ==================================================================
    # STRATEGY B — SponsorBlock Pre-filtered Discovery
    # ==================================================================
    def discover_via_sponsorblock(
        self,
        video_ids: List[str],
    ) -> List[Dict]:
        """
        Check videos via SponsorBlock and only process those with sponsors.
        More targeted than search — higher yield per video processed.
        """
        print(f"\n{'='*60}")
        print(f"Strategy B: SponsorBlock Pre-filtered Discovery")
        print(f"  Videos to check: {len(video_ids)}")
        print(f"{'='*60}")

        # Batch check for sponsor segments
        print("  Checking SponsorBlock for sponsor segments...")
        sponsor_map = self.sponsorblock_svc.batch_check_videos(video_ids)
        sponsored_ids = [vid for vid, has in sponsor_map.items() if has]
        print(f"  {len(sponsored_ids)}/{len(video_ids)} have sponsor segments")

        all_discoveries = []
        for i, video_id in enumerate(sponsored_ids):
            print(f"\n  [{i+1}/{len(sponsored_ids)}] Processing sponsored video: {video_id}")
            discovery = self._process_video(video_id)
            if discovery and discovery.get("codes"):
                all_discoveries.append(discovery)
                print(
                    f"    ✅ {discovery['creator_name']}: "
                    f"{len(discovery['codes'])} codes"
                )
            time.sleep(0.3)

        print(f"\n  SponsorBlock strategy: {len(all_discoveries)} videos with codes")
        return all_discoveries

    # ==================================================================
    # STRATEGY C — Channel-Based Snowball Discovery
    # ==================================================================
    def discover_from_channel(
        self,
        channel_url: str,
        channel_name: str = "",
        max_videos: int = 20,
    ) -> List[Dict]:
        """
        Scrape a known creator's channel for codes in their recent videos.
        """
        print(f"\n  Channel: {channel_name or channel_url}")
        print(f"  Fetching up to {max_videos} recent videos...")

        try:
            video_ids = self.transcript_svc.get_channel_video_ids(
                channel_url, max_videos=max_videos
            )
        except Exception as e:
            print(f"  Error fetching channel videos: {e}")
            self.stats["errors"] += 1
            return []

        if not video_ids:
            print(f"  No videos found for channel")
            return []

        print(f"  Found {len(video_ids)} videos")

        all_discoveries = []
        for i, video_id in enumerate(video_ids):
            discovery = self._process_video(video_id)
            if discovery and discovery.get("codes"):
                all_discoveries.append(discovery)
                codes_str = ", ".join(c["code"] for c in discovery["codes"][:5])
                print(f"    [{i+1}] ✅ {len(discovery['codes'])} codes: {codes_str}")
            time.sleep(0.3)

        print(f"  Channel total: {len(all_discoveries)} videos with codes")
        return all_discoveries

    def discover_from_seed_creators(
        self,
        max_videos_per_creator: int = 10,
    ) -> List[Dict]:
        """
        Run Strategy C on the curated seed creator list.
        """
        print(f"\n{'='*60}")
        print(f"Strategy C: Channel Snowball (Seed Creators)")
        print(f"  Seed creators: {len(SEED_CREATORS)}")
        print(f"  Max videos per creator: {max_videos_per_creator}")
        print(f"{'='*60}")

        known_ids = self._load_known_creator_channel_ids()
        all_discoveries = []

        for i, creator in enumerate(SEED_CREATORS):
            name = creator["name"]
            url = creator["channel_url"]
            print(f"\n  [{i+1}/{len(SEED_CREATORS)}] {name}")

            discoveries = self.discover_from_channel(
                channel_url=url,
                channel_name=name,
                max_videos=max_videos_per_creator,
            )
            all_discoveries.extend(discoveries)

            # Rate limit between creators
            time.sleep(1.0)

        print(f"\n  Seed creators complete: {len(all_discoveries)} videos with codes")
        return all_discoveries

    # ==================================================================
    # CORE: Video Processing Pipeline
    # ==================================================================
    def _process_video(
        self,
        video_id: str,
        search_metadata: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """
        Core processing pipeline for a single video:
        1. Get metadata via yt-dlp (title, description, channel info)
        2. Get transcript via youtube-transcript-api
        3. Extract codes with context
        4. Extract brand indicators
        5. Match codes to brands

        Returns a discovery dict or None if no codes found.
        """
        self.stats["videos_processed"] += 1

        try:
            # Step 1: Get video metadata
            metadata = self.transcript_svc.get_video_metadata(video_id)
            if not metadata:
                # Fall back to search metadata if available
                if search_metadata:
                    metadata = {
                        "title": search_metadata.get("title", ""),
                        "description": "",
                        "channel_id": search_metadata.get("channel_id", ""),
                        "channel_name": search_metadata.get("channel_name", ""),
                        "channel_url": search_metadata.get("channel_url", ""),
                        "upload_date": "",
                        "view_count": search_metadata.get("view_count", 0),
                        "duration": search_metadata.get("duration", 0),
                        "tags": [],
                    }
                else:
                    return None

            description = metadata.get("description", "") or ""
            title = metadata.get("title", "") or ""

            # Step 2: Get transcript
            transcript = self.transcript_svc.get_transcript(video_id)

            # Step 3: Combine all text sources
            combined_text = "\n\n".join(
                filter(None, [title, description, transcript])
            )

            if not combined_text.strip():
                return None

            # Step 4: Extract codes with context
            codes_with_context = extract_codes_with_context(combined_text)
            if not codes_with_context:
                return None

            self.stats["codes_found"] += len(codes_with_context)

            # Step 5: Extract brand indicators from description
            brand_indicators = extract_brand_indicators(description)

            # Step 6: Match codes to brands
            known_brands = self._load_known_brands()
            matched_codes = []
            for code_info in codes_with_context:
                brand = match_code_to_brand(
                    code_info["code"],
                    code_info["context"],
                    known_brands,
                )
                matched_codes.append({
                    "code": code_info["code"],
                    "context": code_info["context"],
                    "probable_brand": code_info.get("probable_brand"),
                    "matched_brand": brand,
                })

            # Build discovery result
            creator_name = metadata.get("channel_name", "") or ""
            channel_id = metadata.get("channel_id", "") or ""

            if creator_name:
                self.stats["creators_found"] += 1

            return {
                "video_id": video_id,
                "video_title": title,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "creator_name": creator_name,
                "creator_channel_id": channel_id,
                "creator_channel_url": metadata.get("channel_url", ""),
                "upload_date": metadata.get("upload_date", ""),
                "view_count": metadata.get("view_count", 0),
                "codes": matched_codes,
                "brand_indicators": brand_indicators,
                "had_transcript": transcript is not None,
                "had_sponsor_segments": False,  # Set by caller if applicable
            }

        except Exception as e:
            print(f"    Error processing video {video_id}: {e}")
            self.stats["errors"] += 1
            return None

    # ==================================================================
    # DATABASE PERSISTENCE
    # ==================================================================
    def save_discoveries(self, discoveries: List[Dict]) -> Dict[str, int]:
        """
        Save discovery results to Supabase.
        Upserts creators, resolves brands, creates offers.

        Returns summary stats dict.
        """
        print(f"\n{'='*60}")
        print(f"Saving {len(discoveries)} discoveries to database")
        print(f"{'='*60}")

        saved_stats = {
            "creators_upserted": 0,
            "brands_resolved": 0,
            "brands_created": 0,
            "offers_created": 0,
            "offers_updated": 0,
        }

        for disc in discoveries:
            try:
                # 1. Upsert creator
                creator_id = self._upsert_creator(
                    channel_id=disc.get("creator_channel_id"),
                    channel_name=disc.get("creator_name"),
                    channel_url=disc.get("creator_channel_url"),
                    discovery_source="creator_discovery",
                )
                if creator_id:
                    saved_stats["creators_upserted"] += 1

                # 2. Process each code
                for code_info in disc.get("codes", []):
                    code = code_info["code"]
                    matched_brand = code_info.get("matched_brand")

                    # Resolve brand
                    brand_id = None
                    if matched_brand:
                        brand_id = matched_brand.get("id")
                        saved_stats["brands_resolved"] += 1
                    else:
                        # Try to create brand from indicators
                        brand_id = self._resolve_brand_from_context(
                            code_info, disc.get("brand_indicators", [])
                        )
                        if brand_id:
                            saved_stats["brands_created"] += 1

                    if not creator_id:
                        continue

                    # 3. Upsert offer
                    result = self._upsert_offer(
                        creator_id=creator_id,
                        brand_id=brand_id,
                        code=code,
                        source_video_id=disc.get("video_id"),
                    )
                    if result == "created":
                        saved_stats["offers_created"] += 1
                    elif result == "updated":
                        saved_stats["offers_updated"] += 1

            except Exception as e:
                print(f"  Error saving discovery for {disc.get('creator_name')}: {e}")
                self.stats["errors"] += 1

        self.stats["codes_saved"] = saved_stats["offers_created"]
        self.stats["creators_new"] = saved_stats["creators_upserted"]
        self.stats["brands_matched"] = saved_stats["brands_resolved"]
        self.stats["brands_created"] = saved_stats["brands_created"]

        print(f"\n  Creators upserted: {saved_stats['creators_upserted']}")
        print(f"  Brands resolved:   {saved_stats['brands_resolved']}")
        print(f"  Brands created:    {saved_stats['brands_created']}")
        print(f"  Offers created:    {saved_stats['offers_created']}")
        print(f"  Offers updated:    {saved_stats['offers_updated']}")

        return saved_stats

    def _upsert_creator(
        self,
        channel_id: Optional[str],
        channel_name: Optional[str],
        channel_url: Optional[str] = None,
        discovery_source: str = "creator_discovery",
    ) -> Optional[str]:
        """
        Find or create a creator in the database.
        Returns creator_id or None.
        """
        if not channel_name and not channel_id:
            return None

        try:
            # Try to find existing creator
            existing_id = self._match_creator(channel_id, channel_name)
            if existing_id:
                # Update last_scraped_at if the column exists
                try:
                    self.supabase.table("creators").update({
                        "updated_at": datetime.now().isoformat(),
                    }).eq("id", existing_id).execute()
                except Exception:
                    pass  # Column might not exist yet
                return existing_id

            # Create new creator
            display_name = channel_name or "Unknown"

            # Generate ref code from channel name
            ref_code = re.sub(r"[^a-z0-9]", "", display_name.lower())[:20]

            # Extract username from channel URL (@username)
            username = None
            if channel_url:
                username_match = re.search(r"@([A-Za-z0-9_-]+)", channel_url)
                if username_match:
                    username = username_match.group(1)

            creator_data = {
                "display_name": display_name,
                "youtube_channel_id": channel_id or None,
                "youtube_username": username,
                "youtube_channel_url": channel_url or None,
                "affiliate_ref_code": ref_code,
            }
            # Remove None values (Supabase doesn't like explicit nulls on insert)
            creator_data = {k: v for k, v in creator_data.items() if v is not None}

            result = (
                self.supabase.table("creators").insert(creator_data).execute()
            )
            if result.data:
                new_id = result.data[0]["id"]
                print(f"    + New creator: {display_name} ({new_id[:8]}...)")
                return new_id

        except Exception as e:
            # If insert fails (e.g. duplicate), try to find again
            print(f"    Warning creating creator '{channel_name}': {e}")
            try:
                existing_id = self._match_creator(channel_id, channel_name)
                if existing_id:
                    return existing_id
            except Exception:
                pass

        return None

    def _match_creator(
        self,
        channel_id: Optional[str],
        display_name: Optional[str],
    ) -> Optional[str]:
        """Match an existing creator by channel_id or display_name."""
        # Try by channel ID (most reliable)
        if channel_id:
            result = (
                self.supabase.table("creators")
                .select("id")
                .eq("youtube_channel_id", channel_id)
                .execute()
            )
            if result.data:
                return result.data[0]["id"]

        # Try by display name (fuzzy)
        if display_name and len(display_name) >= 3:
            result = (
                self.supabase.table("creators")
                .select("id")
                .ilike("display_name", f"%{display_name}%")
                .execute()
            )
            if result.data:
                return result.data[0]["id"]

        return None

    def _resolve_brand_from_context(
        self,
        code_info: Dict,
        brand_indicators: List[Dict],
    ) -> Optional[str]:
        """
        Try to resolve a brand from code context and brand indicators.
        If we're confident enough, auto-create the brand.

        Returns brand_id or None.
        """
        probable = code_info.get("probable_brand")
        if not probable:
            return None

        # Check if brand already exists by name
        try:
            result = (
                self.supabase.table("brands")
                .select("id")
                .ilike("name", f"%{probable}%")
                .execute()
            )
            if result.data:
                return result.data[0]["id"]
        except Exception:
            pass

        # Look for a matching brand indicator (URL) for higher confidence
        matching_indicator = None
        for indicator in brand_indicators:
            if probable.lower() in indicator.get("name", "").lower():
                matching_indicator = indicator
                break
            if probable.lower() in indicator.get("domain", "").lower():
                matching_indicator = indicator
                break

        # Only auto-create if we have a domain indicator (higher confidence)
        if matching_indicator:
            domain = matching_indicator.get("domain", "")
            brand_name = matching_indicator.get("name", probable)
            try:
                result = (
                    self.supabase.table("brands")
                    .insert({
                        "name": brand_name,
                        "domain_pattern": domain,
                    })
                    .execute()
                )
                if result.data:
                    new_id = result.data[0]["id"]
                    print(f"    + New brand: {brand_name} ({domain})")
                    # Refresh brand cache
                    self._known_brands_cache = None
                    return new_id
            except Exception as e:
                print(f"    Warning creating brand '{brand_name}': {e}")
                # Might already exist (race condition), try to find it
                try:
                    result = (
                        self.supabase.table("brands")
                        .select("id")
                        .ilike("name", f"%{brand_name}%")
                        .execute()
                    )
                    if result.data:
                        return result.data[0]["id"]
                except Exception:
                    pass

        return None

    def _upsert_offer(
        self,
        creator_id: str,
        brand_id: Optional[str],
        code: str,
        source_video_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create or update an offer in the database.
        Returns 'created', 'updated', or None.
        """
        try:
            # Check if offer already exists (same creator + code)
            query = (
                self.supabase.table("offers")
                .select("id")
                .eq("creator_id", creator_id)
                .eq("code", code)
            )
            if brand_id:
                query = query.eq("brand_id", brand_id)

            existing = query.execute()

            if existing.data and len(existing.data) > 0:
                # Update existing offer
                update_data = {
                    "is_active": True,
                    "updated_at": datetime.now().isoformat(),
                }
                self.supabase.table("offers").update(update_data).eq(
                    "id", existing.data[0]["id"]
                ).execute()
                return "updated"
            else:
                # Create new offer
                offer_data = {
                    "creator_id": creator_id,
                    "code": code,
                    "discount_amount": "Found on YouTube",
                    "discount_type": "percentage",
                    "is_active": True,
                }
                if brand_id:
                    offer_data["brand_id"] = brand_id

                self.supabase.table("offers").insert(offer_data).execute()
                return "created"

        except Exception as e:
            print(f"    Warning upserting offer '{code}': {e}")
            return None

    # ==================================================================
    # PRINT STATS
    # ==================================================================
    def print_stats(self):
        """Print final discovery statistics."""
        print(f"\n{'='*60}")
        print("Creator Discovery — Final Stats")
        print(f"{'='*60}")
        for key, val in self.stats.items():
            label = key.replace("_", " ").title()
            print(f"  {label:.<30} {val}")
        print(f"{'='*60}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run_creator_discovery(
    strategies: Optional[List[str]] = None,
    max_results: int = 10,
    max_videos_per_creator: int = 10,
) -> Dict[str, int]:
    """
    Run creator discovery with specified strategies.
    Returns stats dict.

    Strategies:
      - 'search': YouTube search (Strategy A)
      - 'sponsorblock': SponsorBlock pre-filter (Strategy B)
      - 'channel': Channel snowball from seed creators (Strategy C)
    """
    strategies = strategies or ["search", "channel"]

    print("\n" + "=" * 60)
    print("backrAI Creator Discovery Engine")
    print(f"  Strategies: {', '.join(strategies)}")
    print(f"  Max results per query: {max_results}")
    print(f"  Max videos per creator: {max_videos_per_creator}")
    print("=" * 60)

    engine = CreatorDiscovery()
    all_discoveries = []

    # Strategy A: YouTube Search
    if "search" in strategies:
        search_discoveries = engine.discover_via_search(
            max_results_per_query=max_results,
        )
        all_discoveries.extend(search_discoveries)

    # Strategy B: SponsorBlock (needs video IDs from Strategy A or C)
    if "sponsorblock" in strategies:
        # Use video IDs from search results if available
        video_ids = [d["video_id"] for d in all_discoveries if d.get("video_id")]
        if video_ids:
            sb_discoveries = engine.discover_via_sponsorblock(video_ids)
            # Only add new discoveries (not already found)
            existing_ids = {d["video_id"] for d in all_discoveries}
            for disc in sb_discoveries:
                if disc["video_id"] not in existing_ids:
                    disc["had_sponsor_segments"] = True
                    all_discoveries.append(disc)

    # Strategy C: Channel Snowball
    if "channel" in strategies:
        channel_discoveries = engine.discover_from_seed_creators(
            max_videos_per_creator=max_videos_per_creator,
        )
        all_discoveries.extend(channel_discoveries)

    # Deduplicate by video_id
    seen_ids = set()
    unique_discoveries = []
    for disc in all_discoveries:
        vid = disc.get("video_id")
        if vid and vid not in seen_ids:
            seen_ids.add(vid)
            unique_discoveries.append(disc)

    print(f"\n  Total unique discoveries: {len(unique_discoveries)}")

    # Save to database
    if unique_discoveries:
        engine.save_discoveries(unique_discoveries)

    engine.print_stats()
    return engine.stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="backrAI Creator Discovery Engine"
    )
    parser.add_argument(
        "--strategies",
        type=str,
        default="search,channel",
        help="Comma-separated strategies: search, sponsorblock, channel (default: search,channel)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Max results per search query (default: 10)",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=10,
        help="Max videos per creator channel (default: 10)",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Only run channel strategy with seed creators (skip search)",
    )
    parser.add_argument(
        "--search-only",
        action="store_true",
        help="Only run search strategy (skip channel snowball)",
    )

    args = parser.parse_args()

    if args.seed_only:
        strategy_list = ["channel"]
    elif args.search_only:
        strategy_list = ["search"]
    else:
        strategy_list = [s.strip() for s in args.strategies.split(",")]

    run_creator_discovery(
        strategies=strategy_list,
        max_results=args.max_results,
        max_videos_per_creator=args.max_videos,
    )
