#!/usr/bin/env python3
"""
backrAI Coupon Code Scraper
Crawls and validates coupon codes for brands in the database
"""

import asyncio
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
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


class CouponScraper:
    """Scrapes and validates coupon codes from various sources"""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def initialize(self):
        """Initialize browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()

    async def scrape_coupon_sites(self, brand_domain: str) -> List[Dict[str, str]]:
        """
        Scrape coupon codes from common coupon sites
        Returns list of {code: str, discount: str, source: str}
        """
        codes = []

        # Common coupon sites to check
        coupon_sites = [
            f"https://www.retailmenot.com/view/{brand_domain}",
            f"https://www.coupons.com/coupon-codes/{brand_domain}",
            f"https://www.honey.com/coupons/{brand_domain}",
        ]

        for site_url in coupon_sites:
            try:
                site_codes = await self._scrape_site(site_url, brand_domain)
                codes.extend(site_codes)
            except Exception as e:
                print(f"Error scraping {site_url}: {e}")
                continue

        return codes

    async def _scrape_site(self, url: str, brand: str) -> List[Dict[str, str]]:
        """Scrape a specific coupon site"""
        codes = []

        try:
            await self.page.goto(url, wait_until="networkidle", timeout=10000)
            await self.page.wait_for_timeout(2000)  # Wait for JS to load

            # Look for coupon code elements
            # Common selectors for coupon codes
            selectors = [
                'input[value*="CODE"]',
                '.coupon-code',
                '.code',
                '[data-code]',
                '.promo-code',
            ]

            for selector in selectors:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    code = await element.get_attribute("value") or await element.inner_text()
                    if code and self._is_valid_code(code):
                        discount = await self._extract_discount(element)
                        codes.append({
                            "code": code.strip(),
                            "discount": discount,
                            "source": url,
                        })

            # Also try to extract from page text
            page_text = await self.page.inner_text("body")
            text_codes = self._extract_codes_from_text(page_text)
            for code in text_codes:
                codes.append({
                    "code": code,
                    "discount": "Unknown",
                    "source": url,
                })

        except Exception as e:
            print(f"Error in _scrape_site for {url}: {e}")

        return codes

    def _is_valid_code(self, code: str) -> bool:
        """Check if a string looks like a valid coupon code"""
        if not code or len(code) < 3:
            return False

        # Remove common prefixes/suffixes
        code = code.upper().strip()
        code = re.sub(r"^(CODE|PROMO|COUPON)[:\s]*", "", code)
        code = re.sub(r"[:\s]*$", "", code)

        # Should be alphanumeric, possibly with dashes
        if not re.match(r"^[A-Z0-9\-]+$", code):
            return False

        # Should be reasonable length
        if len(code) < 3 or len(code) > 20:
            return False

        return True

    def _extract_codes_from_text(self, text: str) -> List[str]:
        """Extract potential coupon codes from text"""
        codes = []

        # Pattern for codes like "SAVE20", "CODE123", etc.
        patterns = [
            r"\b[A-Z]{2,}[0-9]{2,}\b",  # ALPHA123
            r"\b[0-9]{2,}[A-Z]{2,}\b",  # 123ALPHA
            r"\b[A-Z0-9]{4,}\b",  # General alphanumeric
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text.upper())
            for match in matches:
                if self._is_valid_code(match):
                    codes.append(match)

        return list(set(codes))  # Remove duplicates

    async def _extract_discount(self, element) -> str:
        """Extract discount information from element or nearby elements"""
        try:
            # Try to find discount text nearby
            parent = await element.evaluate_handle("el => el.parentElement")
            if parent:
                text = await parent.inner_text()
                # Look for percentage or dollar amounts
                percent_match = re.search(r"(\d+)%", text)
                if percent_match:
                    return f"{percent_match.group(1)}% OFF"

                dollar_match = re.search(r"\$(\d+)", text)
                if dollar_match:
                    return f"${dollar_match.group(1)} OFF"
        except:
            pass

        return "Unknown"

    async def validate_code(self, brand_url: str, code: str) -> bool:
        """
        Validate a coupon code by attempting to use it on the brand's site
        Returns True if code appears to be valid
        """
        try:
            # Navigate to brand's checkout or cart page
            await self.page.goto(brand_url, wait_until="networkidle")

            # Try to find and fill coupon input
            coupon_selectors = [
                'input[name*="coupon" i]',
                'input[name*="code" i]',
                'input[name*="promo" i]',
                'input[id*="coupon" i]',
                'input[id*="code" i]',
            ]

            for selector in coupon_selectors:
                try:
                    input_field = await self.page.query_selector(selector)
                    if input_field:
                        await input_field.fill(code)
                        await input_field.press("Enter")
                        await self.page.wait_for_timeout(2000)

                        # Check for success/error messages
                        page_text = await self.page.inner_text("body")
                        error_indicators = [
                            "invalid",
                            "expired",
                            "not found",
                            "does not exist",
                        ]
                        success_indicators = [
                            "applied",
                            "valid",
                            "discount",
                            "saved",
                        ]

                        # If we see error indicators, code is invalid
                        if any(
                            indicator in page_text.lower()
                            for indicator in error_indicators
                        ):
                            return False

                        # If we see success indicators, code might be valid
                        if any(
                            indicator in page_text.lower()
                            for indicator in success_indicators
                        ):
                            return True

                except:
                    continue

            # If we can't validate, assume it might be valid (conservative)
            return True

        except Exception as e:
            print(f"Error validating code {code} for {brand_url}: {e}")
            return False


async def update_offers_from_scraped_codes(
    creator_id: str, brand_id: str, codes: List[Dict[str, str]]
):
    """Update offers in database with scraped codes"""
    for code_data in codes:
        try:
            # Check if offer already exists
            existing = (
                supabase.table("offers")
                .select("id")
                .eq("creator_id", creator_id)
                .eq("brand_id", brand_id)
                .eq("code", code_data["code"])
                .execute()
            )

            if existing.data and len(existing.data) > 0:
                # Update existing offer
                supabase.table("offers").update(
                    {
                        "discount_amount": code_data["discount"],
                        "is_active": True,
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                ).eq("id", existing.data[0]["id"]).execute()
            else:
                # Create new offer
                supabase.table("offers").insert(
                    {
                        "creator_id": creator_id,
                        "brand_id": brand_id,
                        "code": code_data["code"],
                        "discount_amount": code_data["discount"],
                        "is_active": True,
                    }
                ).execute()

        except Exception as e:
            print(f"Error updating offer for code {code_data['code']}: {e}")


async def scrape_brand_by_id(brand_id: str, use_youtube: bool = True):
    """
    Scrape codes for a specific brand by ID
    Can use YouTube scraper or traditional coupon sites
    """
    # Get the specific brand
    brand_response = supabase.table("brands").select("id, name, domain_pattern").eq("id", brand_id).execute()
    
    if not brand_response.data or len(brand_response.data) == 0:
        print(f"Brand with ID {brand_id} not found")
        return []

    brand = brand_response.data[0]
    brand_name = brand['name']
    
    codes_found = []
    
    # Use YouTube scraper (primary method)
    if use_youtube:
        try:
            print(f"\n🎬 Using YouTube scraper for {brand_name}...")
            from youtube_scraper import scrape_youtube_for_brand
            await scrape_youtube_for_brand(brand_id, max_videos=50)
            codes_found.append("youtube")  # Mark as found
            return codes_found  # YouTube scraper handles everything
        except Exception as e:
            print(f"⚠️  YouTube scraper failed: {e}")
            print("🔄 Falling back to traditional coupon sites...")
    
    # Fallback to traditional coupon sites
    if not codes_found:
        scraper = CouponScraper()
        await scraper.initialize()

        try:
            print(f"Scraping coupon sites for {brand_name} ({brand['domain_pattern']})")

            # Extract domain from pattern
            domain = brand["domain_pattern"].replace("https://", "").replace("http://", "").split("/")[0]

            # Scrape codes
            codes = await scraper.scrape_coupon_sites(domain)
            print(f"Found {len(codes)} potential codes")

            if len(codes) == 0:
                print("No codes found for this brand")
                await scraper.close()
                return []

                # Get or create a default creator for unassigned codes
            # First, try to get the first creator in the system
            creators_response = supabase.table("creators").select("id").limit(1).execute()
            default_creator_id = None
            
            if creators_response.data and len(creators_response.data) > 0:
                default_creator_id = creators_response.data[0]["id"]
                print(f"Using default creator ID: {default_creator_id}")
            else:
                print("Warning: No creators found. Codes will be scraped but not assigned.")
                await scraper.close()
                return codes

            # Create offers for the found codes
            created_count = 0
            for code_data in codes:
                try:
                    # Check if offer already exists
                    existing = (
                        supabase.table("offers")
                        .select("id")
                        .eq("brand_id", brand_id)
                        .eq("code", code_data["code"])
                        .execute()
                    )

                    if existing.data and len(existing.data) > 0:
                        # Update existing offer
                        supabase.table("offers").update({
                            "discount_amount": code_data["discount"],
                            "is_active": True,
                            "updated_at": datetime.utcnow().isoformat(),
                        }).eq("id", existing.data[0]["id"]).execute()
                        print(f"Updated existing offer: {code_data['code']}")
                    else:
                        # Create new offer with default creator
                        supabase.table("offers").insert({
                            "creator_id": default_creator_id,
                            "brand_id": brand_id,
                            "code": code_data["code"],
                            "discount_amount": code_data["discount"],
                            "discount_type": "percentage",
                            "is_active": True,
                        }).execute()
                        created_count += 1
                        print(f"Created new offer: {code_data['code']} ({code_data['discount']})")
                except Exception as e:
                    print(f"Error creating offer for code {code_data['code']}: {e}")

            print(f"\n✅ Scraping complete: {created_count} new offers created, {len(codes)} total codes found")
            await scraper.close()
            return codes


async def scrape_all_brands():
    """Main function to scrape codes for all brands"""
    scraper = CouponScraper()
    await scraper.initialize()

    try:
        # Get all brands
        brands_response = supabase.table("brands").select("id, name, domain_pattern").execute()
        brands = brands_response.data

        print(f"Found {len(brands)} brands to scrape")

        for brand in brands:
            print(f"\nScraping codes for {brand['name']} ({brand['domain_pattern']})")

            # Extract domain from pattern
            domain = brand["domain_pattern"].replace("https://", "").replace("http://", "").split("/")[0]

            # Scrape codes
            codes = await scraper.scrape_coupon_sites(domain)
            print(f"Found {len(codes)} potential codes")

            # Validate codes (optional - can be slow)
            # For MVP, we'll skip validation and let the extension handle it
            # validated_codes = []
            # for code_data in codes:
            #     if await scraper.validate_code(f"https://{domain}", code_data["code"]):
            #         validated_codes.append(code_data)

            # For now, we'll create offers for a default creator or skip
            # In production, this would be more sophisticated
            print(f"Note: Codes found but not automatically assigned to creators")
            print(f"   Manual assignment required via dashboard")

    finally:
        await scraper.close()


async def validate_existing_offers():
    """Validate existing offers in database and mark expired ones as inactive"""
    scraper = CouponScraper()
    await scraper.initialize()

    try:
        # Get all active offers
        offers_response = (
            supabase.table("offers")
            .select("id, code, brand:brands(domain_pattern)")
            .eq("is_active", True)
            .execute()
        )
        offers = offers_response.data

        print(f"Validating {len(offers)} active offers")

        for offer in offers:
            brand = offer.get("brand", {})
            domain_pattern = brand.get("domain_pattern", "")

            if not domain_pattern:
                continue

            # Extract base URL
            base_url = domain_pattern
            if not base_url.startswith("http"):
                base_url = f"https://{base_url}"

            # Validate code
            is_valid = await scraper.validate_code(base_url, offer["code"])

            if not is_valid:
                print(f"Marking offer {offer['code']} as inactive (invalid)")
                supabase.table("offers").update({"is_active": False}).eq(
                    "id", offer["id"]
                ).execute()

    finally:
        await scraper.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "validate":
            asyncio.run(validate_existing_offers())
        elif sys.argv[1] == "--brand-id" and len(sys.argv) > 2:
            # Scrape specific brand by ID
            brand_id = sys.argv[2]
            asyncio.run(scrape_brand_by_id(brand_id))
        elif sys.argv[1] == "discover":
            # Run brand discovery only
            from brand_discovery import run_discovery
            asyncio.run(run_discovery(discovery_only=True))
        elif sys.argv[1] == "full-pipeline":
            # Run discovery then scrape all brands
            from brand_discovery import run_discovery
            asyncio.run(run_discovery())
            print("\n🔄 Now scraping all brands (including newly discovered)...")
            asyncio.run(scrape_all_brands())
        else:
            print("Usage:")
            print("  python scraper.py                    # Scrape all brands")
            print("  python scraper.py validate           # Validate existing offers")
            print("  python scraper.py --brand-id <id>    # Scrape specific brand")
            print("  python scraper.py discover           # Discover new brands only")
            print("  python scraper.py full-pipeline      # Discover brands + scrape all")
    else:
        asyncio.run(scrape_all_brands())

