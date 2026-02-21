#!/usr/bin/env python3
"""
backrAI Brand Discovery Module (LEGACY — use creator_discovery.py instead)
==========================================================================
This module discovers brands from coupon aggregator sites (RetailMeNot,
Coupons.com) and YouTube search. It's kept for backward compatibility but
the creator-centric approach in creator_discovery.py is preferred.

DEPRECATED: Codes from coupon sites credit the coupon site, not creators.
Use `creator_discovery.py` for creator-attributed codes.

New usage:
  python scraper.py discover-creators            # Creator-centric discovery
  python scraper.py discover-creators --search-only
  python scraper.py scrape-creator <channel_url>
"""

import asyncio
import os
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional, Set
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, Page
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Curated search categories for brand discovery
DISCOVERY_CATEGORIES = {
    "fitness": [
        "best fitness discount codes",
        "gym supplement promo codes",
        "workout gear coupon codes",
        "activewear discount codes",
    ],
    "beauty": [
        "best beauty discount codes",
        "skincare promo codes",
        "makeup coupon codes",
        "haircare discount codes",
    ],
    "tech": [
        "best tech discount codes",
        "gadget promo codes",
        "electronics coupon codes",
        "software discount codes",
    ],
    "fashion": [
        "best fashion discount codes",
        "clothing promo codes",
        "streetwear coupon codes",
        "shoe discount codes",
    ],
    "food_supplements": [
        "best supplement discount codes",
        "protein powder promo codes",
        "vitamin coupon codes",
        "meal kit discount codes",
    ],
    "lifestyle": [
        "best lifestyle discount codes",
        "home goods promo codes",
        "wellness coupon codes",
        "subscription box discount codes",
    ],
}

# Well-known brands to seed if DB is nearly empty (bootstrap list)
SEED_BRANDS = [
    {"name": "Gymshark", "domain_pattern": "gymshark.com"},
    {"name": "Athletic Greens", "domain_pattern": "athleticgreens.com"},
    {"name": "MyProtein", "domain_pattern": "myprotein.com"},
    {"name": "Nike", "domain_pattern": "nike.com"},
    {"name": "Adidas", "domain_pattern": "adidas.com"},
    {"name": "Lululemon", "domain_pattern": "lululemon.com"},
    {"name": "Glossier", "domain_pattern": "glossier.com"},
    {"name": "Sephora", "domain_pattern": "sephora.com"},
    {"name": "HelloFresh", "domain_pattern": "hellofresh.com"},
    {"name": "Dollar Shave Club", "domain_pattern": "dollarshaveclub.com"},
    {"name": "Squarespace", "domain_pattern": "squarespace.com"},
    {"name": "NordVPN", "domain_pattern": "nordvpn.com"},
    {"name": "ExpressVPN", "domain_pattern": "expressvpn.com"},
    {"name": "Skillshare", "domain_pattern": "skillshare.com"},
    {"name": "Audible", "domain_pattern": "audible.com"},
    {"name": "Ridge Wallet", "domain_pattern": "ridge.com"},
    {"name": "Manscaped", "domain_pattern": "manscaped.com"},
    {"name": "MVMT Watches", "domain_pattern": "mvmt.com"},
    {"name": "Raycon", "domain_pattern": "rayconglobal.com"},
    {"name": "BetterHelp", "domain_pattern": "betterhelp.com"},
    {"name": "Liquid IV", "domain_pattern": "liquid-iv.com"},
    {"name": "AG1", "domain_pattern": "drinkag1.com"},
    {"name": "Cuts Clothing", "domain_pattern": "cutsclothing.com"},
    {"name": "True Classic", "domain_pattern": "trueclassictees.com"},
    {"name": "Alo Yoga", "domain_pattern": "aloyoga.com"},
    {"name": "NOCTA", "domain_pattern": "nocta.com"},
    {"name": "Transparent Labs", "domain_pattern": "transparentlabs.com"},
    {"name": "Ghost Lifestyle", "domain_pattern": "ghostlifestyle.com"},
    {"name": "Gorilla Mind", "domain_pattern": "gorillamind.com"},
    {"name": "Bloom Nutrition", "domain_pattern": "bloomnu.com"},
]


class BrandDiscovery:
    """Discovers new e-commerce brands from coupon sites and YouTube"""

    def __init__(self):
        self._playwright = None
        self.browser: Optional[Browser] = None
        self.existing_domains: Set[str] = set()
        self.discovered_brands: List[Dict[str, str]] = []

    async def initialize(self):
        """Initialize browser and load existing brands from DB"""
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=True)

        # Pre-load existing domain patterns for deduplication
        await self._load_existing_brands()

    async def _ensure_browser(self):
        """Ensure the browser is connected, relaunch if crashed"""
        if not self.browser or not self.browser.is_connected():
            if self.browser:
                try:
                    await self.browser.close()
                except Exception:
                    pass
            self.browser = await self._playwright.chromium.launch(headless=True)

    async def _new_page(self) -> Page:
        """Create a fresh page with custom user agent (relaunches browser if needed)"""
        await self._ensure_browser()
        page = await self.browser.new_page()
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        return page

    async def close(self):
        """Close browser and Playwright"""
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def _load_existing_brands(self):
        """Load existing brand domain patterns from the database"""
        try:
            response = supabase.table("brands").select("domain_pattern").execute()
            self.existing_domains = {
                row["domain_pattern"].lower().strip()
                for row in response.data
                if row.get("domain_pattern")
            }
            print(f"📦 Loaded {len(self.existing_domains)} existing brands from database")
        except Exception as e:
            print(f"⚠️  Error loading existing brands: {e}")
            self.existing_domains = set()

    def _normalize_domain(self, domain: str) -> str:
        """Normalize a domain string for comparison"""
        domain = domain.lower().strip()
        domain = re.sub(r"^https?://", "", domain)
        domain = re.sub(r"^www\.", "", domain)
        domain = domain.split("/")[0]
        return domain

    def _is_new_brand(self, domain_pattern: str) -> bool:
        """Check if a brand domain is not yet in the database"""
        normalized = self._normalize_domain(domain_pattern)
        return normalized not in self.existing_domains and len(normalized) > 3

    def _brand_name_to_domain(self, name: str) -> str:
        """Heuristic: convert a brand name to a likely .com domain"""
        # Remove common suffixes like "Inc", "LLC", etc.
        clean = re.sub(r"\s+(inc|llc|ltd|co|corp)\.?$", "", name, flags=re.IGNORECASE)
        # Remove special characters and spaces
        domain = re.sub(r"[^a-z0-9]", "", clean.lower())
        return f"{domain}.com"

    # -------------------------------------------------------------------------
    # Strategy 1: RetailMeNot brand listings
    # -------------------------------------------------------------------------
    async def discover_from_retailmenot(self) -> List[Dict[str, str]]:
        """Discover brands from RetailMeNot's popular stores"""
        brands = []
        urls = [
            "https://www.retailmenot.com/coupons/health-beauty",
            "https://www.retailmenot.com/coupons/clothing",
            "https://www.retailmenot.com/coupons/food-dining",
            "https://www.retailmenot.com/coupons/electronics",
            "https://www.retailmenot.com/coupons/sports-fitness",
        ]

        for url in urls:
            page = None
            try:
                print(f"  🔍 Scanning {url}...")
                page = await self._new_page()
                await page.goto(url, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(2000)

                # Extract store links — RetailMeNot lists stores as links
                store_data = await page.evaluate("""
                    () => {
                        const stores = [];
                        // Look for store/merchant links
                        const links = document.querySelectorAll(
                            'a[href*="/view/"], a[href*="/coupons/"]'
                        );
                        links.forEach(a => {
                            const href = a.getAttribute('href') || '';
                            const text = a.textContent.trim();
                            // Extract domain from /view/domain.com pattern
                            const viewMatch = href.match(/\\/view\\/([a-z0-9.-]+\\.[a-z]{2,})/i);
                            if (viewMatch && text.length > 1 && text.length < 60) {
                                stores.push({
                                    name: text,
                                    domain: viewMatch[1]
                                });
                            }
                        });
                        return stores.slice(0, 30);
                    }
                """)

                for store in store_data:
                    domain = self._normalize_domain(store["domain"])
                    if self._is_new_brand(domain):
                        brands.append({
                            "name": store["name"],
                            "domain_pattern": domain,
                            "source": "retailmenot",
                        })

                await asyncio.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"  ⚠️  Error scraping RetailMeNot {url}: {e}")
                continue
            finally:
                if page:
                    await page.close()

        return brands

    # -------------------------------------------------------------------------
    # Strategy 2: Coupons.com brand listings
    # -------------------------------------------------------------------------
    async def discover_from_coupons_com(self) -> List[Dict[str, str]]:
        """Discover brands from Coupons.com popular stores"""
        brands = []
        urls = [
            "https://www.coupons.com/coupon-codes/stores",
            "https://www.coupons.com/coupon-codes/trending",
        ]

        for url in urls:
            page = None
            try:
                print(f"  🔍 Scanning {url}...")
                page = await self._new_page()
                await page.goto(url, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(2000)

                store_data = await page.evaluate("""
                    () => {
                        const stores = [];
                        const links = document.querySelectorAll(
                            'a[href*="/coupon-codes/"]'
                        );
                        links.forEach(a => {
                            const href = a.getAttribute('href') || '';
                            const text = a.textContent.trim();
                            // Extract store slug from /coupon-codes/storename
                            const storeMatch = href.match(
                                /\\/coupon-codes\\/([a-z0-9-]+)$/i
                            );
                            if (storeMatch && text.length > 1 && text.length < 60) {
                                const slug = storeMatch[1];
                                // Skip category pages
                                if (!['stores', 'trending', 'popular', 'new', 'top'].includes(slug)) {
                                    stores.push({
                                        name: text,
                                        slug: slug
                                    });
                                }
                            }
                        });
                        return stores.slice(0, 30);
                    }
                """)

                for store in store_data:
                    # Convert slug to domain heuristic
                    domain = f"{store['slug'].replace('-', '')}.com"
                    if self._is_new_brand(domain):
                        brands.append({
                            "name": store["name"],
                            "domain_pattern": domain,
                            "source": "coupons.com",
                        })

                await asyncio.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"  ⚠️  Error scraping Coupons.com {url}: {e}")
                continue
            finally:
                if page:
                    await page.close()

        return brands

    # -------------------------------------------------------------------------
    # Strategy 3: YouTube generic search for brands mentioned in code videos
    # -------------------------------------------------------------------------
    async def discover_from_youtube(
        self, categories: List[str] = None
    ) -> List[Dict[str, str]]:
        """Discover brands mentioned in YouTube discount-code videos"""
        brands = []

        if categories is None:
            categories = list(DISCOVERY_CATEGORIES.keys())

        # Collect search queries from selected categories
        search_queries = []
        for cat in categories:
            if cat in DISCOVERY_CATEGORIES:
                search_queries.extend(DISCOVERY_CATEGORIES[cat])

        for query in search_queries:
            page = None
            try:
                print(f"  🔍 YouTube search: \"{query}\"...")
                search_url = (
                    f"https://www.youtube.com/results?search_query="
                    f"{query.replace(' ', '+')}"
                )
                page = await self._new_page()
                await page.goto(
                    search_url, wait_until="networkidle", timeout=30000
                )
                await page.wait_for_timeout(3000)

                # Scroll to load more results
                for _ in range(2):
                    await page.evaluate(
                        "window.scrollTo(0, document.documentElement.scrollHeight)"
                    )
                    await page.wait_for_timeout(2000)

                # Extract video titles — brand names are often mentioned
                titles = await page.evaluate("""
                    () => {
                        const titles = [];
                        document.querySelectorAll(
                            'a#video-title, h3 a'
                        ).forEach(el => {
                            const text = el.textContent.trim();
                            if (text.length > 5) titles.push(text);
                        });
                        return titles.slice(0, 20);
                    }
                """)

                # Extract potential brand names from titles
                for title in titles:
                    extracted = self._extract_brands_from_title(title)
                    for brand in extracted:
                        domain = self._brand_name_to_domain(brand)
                        if self._is_new_brand(domain):
                            brands.append({
                                "name": brand,
                                "domain_pattern": domain,
                                "source": "youtube",
                            })

                await asyncio.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"  ⚠️  Error searching YouTube for \"{query}\": {e}")
                continue
            finally:
                if page:
                    await page.close()

        return brands

    def _extract_brands_from_title(self, title: str) -> List[str]:
        """
        Extract brand names from a YouTube video title.
        Looks for patterns like "BRAND discount code" or "Best BRAND promo codes"
        """
        brands = []

        # Pattern: "BRAND discount/promo/coupon code"
        pattern1 = re.compile(
            r"([A-Z][A-Za-z0-9\s]{2,25}?)\s+(?:discount|promo|coupon)\s+code",
            re.IGNORECASE,
        )
        matches = pattern1.findall(title)
        brands.extend([m.strip() for m in matches])

        # Pattern: "code for BRAND" or "codes for BRAND"
        pattern2 = re.compile(
            r"codes?\s+(?:for|at|on)\s+([A-Z][A-Za-z0-9\s]{2,25})",
            re.IGNORECASE,
        )
        matches = pattern2.findall(title)
        brands.extend([m.strip() for m in matches])

        # Filter out generic words that aren't brands
        generic_words = {
            "best", "top", "new", "free", "working", "latest", "updated",
            "save", "money", "off", "the", "all", "any", "every", "how",
            "get", "these", "that", "this", "your", "you", "my", "our",
        }

        cleaned = []
        for brand in brands:
            words = brand.lower().split()
            # Keep only if the brand name has meaningful words
            if len(words) <= 4 and not all(w in generic_words for w in words):
                cleaned.append(brand.strip())

        return cleaned

    # -------------------------------------------------------------------------
    # Seed brands (bootstrap from curated list)
    # -------------------------------------------------------------------------
    async def seed_from_curated_list(self) -> List[Dict[str, str]]:
        """Insert brands from the curated SEED_BRANDS list that don't exist yet"""
        new_brands = []
        for brand in SEED_BRANDS:
            domain = self._normalize_domain(brand["domain_pattern"])
            if self._is_new_brand(domain):
                new_brands.append({
                    "name": brand["name"],
                    "domain_pattern": domain,
                    "source": "curated_seed",
                })
        return new_brands

    # -------------------------------------------------------------------------
    # Insert discovered brands into database
    # -------------------------------------------------------------------------
    async def insert_new_brands(
        self, brands: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Insert discovered brands into the database.
        Returns list of successfully inserted brands with their IDs.
        """
        inserted = []

        # Deduplicate within the batch by domain_pattern
        seen_domains = set()
        unique_brands = []
        for brand in brands:
            domain = self._normalize_domain(brand["domain_pattern"])
            if domain not in seen_domains and domain not in self.existing_domains:
                seen_domains.add(domain)
                unique_brands.append(brand)

        print(f"\n💾 Inserting {len(unique_brands)} new brands into database...")

        for brand in unique_brands:
            try:
                result = supabase.table("brands").insert({
                    "name": brand["name"],
                    "domain_pattern": brand["domain_pattern"],
                }).execute()

                if result.data and len(result.data) > 0:
                    brand_with_id = {
                        **brand,
                        "id": result.data[0]["id"],
                    }
                    inserted.append(brand_with_id)
                    # Update local cache
                    self.existing_domains.add(brand["domain_pattern"])
                    print(f"  ✅ Inserted: {brand['name']} ({brand['domain_pattern']})")

            except Exception as e:
                # UNIQUE constraint violation is expected for duplicates
                if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                    print(f"  ⏭️  Already exists: {brand['name']} ({brand['domain_pattern']})")
                else:
                    print(f"  ❌ Error inserting {brand['name']}: {e}")

        return inserted


async def run_discovery(
    categories: List[str] = None,
    skip_youtube: bool = False,
    discovery_only: bool = False,
):
    """
    Main orchestration function:
    1. Seed from curated list
    2. Discover brands from RetailMeNot, Coupons.com, and YouTube
    3. Deduplicate and insert new brands
    4. Trigger scraper for each new brand (unless discovery_only)
    """
    print("\n" + "=" * 60)
    print("🔎 backrAI Brand Discovery")
    print("=" * 60)

    discovery = BrandDiscovery()
    await discovery.initialize()

    all_discovered: List[Dict[str, str]] = []

    try:
        # Step 1: Seed from curated list
        print("\n📋 Step 1: Seeding from curated brand list...")
        curated = await discovery.seed_from_curated_list()
        all_discovered.extend(curated)
        print(f"  Found {len(curated)} new brands from curated list")

        # Step 2: RetailMeNot
        print("\n🛍️  Step 2: Discovering brands from RetailMeNot...")
        try:
            rmn_brands = await discovery.discover_from_retailmenot()
            all_discovered.extend(rmn_brands)
            print(f"  Found {len(rmn_brands)} new brands from RetailMeNot")
        except Exception as e:
            print(f"  ⚠️  RetailMeNot discovery failed: {e}")

        # Step 3: Coupons.com
        print("\n🏷️  Step 3: Discovering brands from Coupons.com...")
        try:
            coupons_brands = await discovery.discover_from_coupons_com()
            all_discovered.extend(coupons_brands)
            print(f"  Found {len(coupons_brands)} new brands from Coupons.com")
        except Exception as e:
            print(f"  ⚠️  Coupons.com discovery failed: {e}")

        # Step 4: YouTube (optional)
        if not skip_youtube:
            print("\n🎬 Step 4: Discovering brands from YouTube...")
            try:
                yt_brands = await discovery.discover_from_youtube(categories)
                all_discovered.extend(yt_brands)
                print(f"  Found {len(yt_brands)} new brands from YouTube")
            except Exception as e:
                print(f"  ⚠️  YouTube discovery failed: {e}")
        else:
            print("\n⏭️  Step 4: Skipping YouTube discovery (--skip-youtube)")

        # Step 5: Insert into database
        print(f"\n📊 Total new brands discovered: {len(all_discovered)}")
        inserted = await discovery.insert_new_brands(all_discovered)
        print(f"✅ Successfully inserted: {len(inserted)} brands")

        # Step 6: Trigger scraper for each new brand (unless discovery_only)
        if not discovery_only and inserted:
            print(f"\n🚀 Step 5: Triggering scraper for {len(inserted)} new brands...")
            from scraper import scrape_brand_by_id

            for i, brand in enumerate(inserted, 1):
                brand_id = brand.get("id")
                if brand_id:
                    print(f"\n[{i}/{len(inserted)}] Scraping: {brand['name']}...")
                    try:
                        await scrape_brand_by_id(brand_id, use_youtube=not skip_youtube)
                    except Exception as e:
                        print(f"  ❌ Scraper failed for {brand['name']}: {e}")
                    await asyncio.sleep(2)  # Rate limiting between brands
        elif discovery_only:
            print("\n⏭️  Skipping scraper (--discovery-only mode)")
        else:
            print("\nℹ️  No new brands to scrape")

        # Summary
        print("\n" + "=" * 60)
        print("📋 Discovery Summary")
        print("=" * 60)
        print(f"  Brands discovered: {len(all_discovered)}")
        print(f"  Brands inserted:   {len(inserted)}")
        print(f"  Sources: curated={len(curated)}", end="")
        if 'rmn_brands' in dir():
            print(f", retailmenot={len(rmn_brands)}", end="")
        if 'coupons_brands' in dir():
            print(f", coupons.com={len(coupons_brands)}", end="")
        if not skip_youtube and 'yt_brands' in dir():
            print(f", youtube={len(yt_brands)}", end="")
        print()  # Newline
        print("=" * 60)

    finally:
        await discovery.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="backrAI Brand Discovery")
    parser.add_argument(
        "--categories",
        type=str,
        default=None,
        help="Comma-separated list of categories to search (e.g., fitness,beauty,tech)",
    )
    parser.add_argument(
        "--skip-youtube",
        action="store_true",
        help="Skip YouTube discovery (faster, coupon sites + curated list only)",
    )
    parser.add_argument(
        "--discovery-only",
        action="store_true",
        help="Only discover and insert brands, don't trigger the scraper",
    )

    args = parser.parse_args()

    categories = None
    if args.categories:
        categories = [c.strip() for c in args.categories.split(",")]

    asyncio.run(
        run_discovery(
            categories=categories,
            skip_youtube=args.skip_youtube,
            discovery_only=args.discovery_only,
        )
    )
