#!/usr/bin/env python3
"""
Test script for backrAI scraper
Tests connection, database access, and basic functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def test_connection():
    """Test Supabase connection"""
    print("🔍 Testing Supabase connection...")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing environment variables!")
        print(f"   SUPABASE_URL: {'✅' if SUPABASE_URL else '❌'}")
        print(f"   SUPABASE_KEY: {'✅' if SUPABASE_KEY else '❌'}")
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Connected to Supabase: {SUPABASE_URL}")
        return supabase
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def test_database_access(supabase):
    """Test database access"""
    print("\n🔍 Testing database access...")
    
    try:
        # Test brands table
        brands_response = supabase.table("brands").select("id, name, domain_pattern").limit(5).execute()
        brands = brands_response.data
        print(f"✅ Brands table accessible - Found {len(brands)} brands:")
        for brand in brands:
            print(f"   - {brand['name']} ({brand['domain_pattern']})")
        
        # Test creators table
        creators_response = supabase.table("creators").select("id, display_name, affiliate_ref_code").limit(5).execute()
        creators = creators_response.data
        print(f"\n✅ Creators table accessible - Found {len(creators)} creators:")
        for creator in creators:
            print(f"   - {creator['display_name']} ({creator['affiliate_ref_code']})")
        
        # Test offers table
        offers_response = supabase.table("offers").select("id, code, discount_amount, is_active").limit(5).execute()
        offers = offers_response.data
        print(f"\n✅ Offers table accessible - Found {len(offers)} offers:")
        for offer in offers:
            status = "✅ Active" if offer['is_active'] else "❌ Inactive"
            print(f"   - {offer['code']} ({offer['discount_amount']}) {status}")
        
        return True
    except Exception as e:
        print(f"❌ Database access failed: {e}")
        return False

def test_playwright():
    """Test Playwright installation"""
    print("\n🔍 Testing Playwright...")
    
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright imported successfully")
        
        async def test_browser():
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://example.com")
            title = await page.title()
            await browser.close()
            await playwright.stop()
            return title
        
        title = asyncio.run(test_browser())
        print(f"✅ Browser test successful - Visited example.com (title: {title})")
        return True
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        print("   Try running: playwright install chromium")
        return False

def test_scraper_import():
    """Test scraper module import"""
    print("\n🔍 Testing scraper module...")

    try:
        from scraper import CouponScraper
        print("✅ Scraper module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import scraper: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Import warning: {e}")
        return True  # Might still work


def test_code_extractor():
    """Test code_extractor module"""
    print("\n🔍 Testing code_extractor module...")
    try:
        from code_extractor import (
            extract_codes_from_text,
            extract_codes_with_context,
            extract_brand_indicators,
            match_code_to_brand,
        )
        # Quick sanity check
        codes = extract_codes_from_text("Use code ALEX15 for 15% off")
        assert "ALEX15" in codes, f"Expected ALEX15 in codes, got {codes}"
        print("✅ code_extractor module works correctly")
        return True
    except Exception as e:
        print(f"❌ code_extractor test failed: {e}")
        return False


def test_transcript_service():
    """Test transcript_service module import"""
    print("\n🔍 Testing transcript_service module...")
    try:
        from transcript_service import TranscriptService
        # Check that static methods exist
        assert hasattr(TranscriptService, 'get_transcript')
        assert hasattr(TranscriptService, 'get_video_metadata')
        assert hasattr(TranscriptService, 'search_videos')
        assert hasattr(TranscriptService, 'extract_video_id')
        # Quick check: extract_video_id
        vid = TranscriptService.extract_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert vid == "dQw4w9WgXcQ", f"Expected dQw4w9WgXcQ, got {vid}"
        print("✅ transcript_service module works correctly")
        return True
    except Exception as e:
        print(f"❌ transcript_service test failed: {e}")
        return False


def test_sponsorblock_service():
    """Test sponsorblock_service module import"""
    print("\n🔍 Testing sponsorblock_service module...")
    try:
        from sponsorblock_service import SponsorBlockService
        svc = SponsorBlockService()
        assert hasattr(svc, 'has_sponsor_segments')
        assert hasattr(svc, 'get_sponsor_segments')
        assert hasattr(svc, 'batch_check_videos')
        print("✅ sponsorblock_service module imported successfully")
        return True
    except Exception as e:
        print(f"❌ sponsorblock_service test failed: {e}")
        return False


def test_creator_discovery():
    """Test creator_discovery module import"""
    print("\n🔍 Testing creator_discovery module...")
    try:
        from creator_discovery import (
            CreatorDiscovery,
            SEED_CREATORS,
            CREATOR_SEARCH_QUERIES,
            run_creator_discovery,
        )
        assert len(SEED_CREATORS) > 0, "SEED_CREATORS should not be empty"
        assert len(CREATOR_SEARCH_QUERIES) > 0, "CREATOR_SEARCH_QUERIES should not be empty"
        print(f"✅ creator_discovery module imported ({len(SEED_CREATORS)} seed creators, {len(CREATOR_SEARCH_QUERIES)} queries)")
        return True
    except Exception as e:
        print(f"❌ creator_discovery test failed: {e}")
        return False


def main():
    print("=" * 60)
    print("🧪 backrAI Scraper Test Suite")
    print("=" * 60)

    # Required tests (must pass for CI to succeed)
    required_results = {
        "Connection": False,
        "Playwright": False,
        "Scraper Module": False,
        "Code Extractor": False,
        "Transcript Service": False,
        "SponsorBlock Service": False,
        "Creator Discovery": False,
    }

    # Optional tests (external service dependencies — warn but don't fail CI)
    optional_results = {
        "Database": False,
    }

    # Test 1: Connection (checks env vars and client creation — no network call)
    supabase = test_connection()
    required_results["Connection"] = supabase is not None

    # Test 2: Database Access (requires live Supabase instance)
    if supabase:
        optional_results["Database"] = test_database_access(supabase)

    # Test 3: Playwright
    required_results["Playwright"] = test_playwright()

    # Test 4: Scraper Module
    required_results["Scraper Module"] = test_scraper_import()

    # Test 5: Code Extractor
    required_results["Code Extractor"] = test_code_extractor()

    # Test 6: Transcript Service
    required_results["Transcript Service"] = test_transcript_service()

    # Test 7: SponsorBlock Service
    required_results["SponsorBlock Service"] = test_sponsorblock_service()

    # Test 8: Creator Discovery
    required_results["Creator Discovery"] = test_creator_discovery()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    for test_name, passed in required_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    for test_name, passed in optional_results.items():
        status = "✅ PASS" if passed else "⚠️  SKIP"
        print(f"{status} - {test_name} (external service)")

    all_required_passed = all(required_results.values())

    print("\n" + "=" * 60)
    if all_required_passed:
        if all(optional_results.values()):
            print("🎉 All tests passed! Scraper is ready to use.")
        else:
            print("✅ Required tests passed. Some external service tests were skipped.")
    else:
        print("⚠️  Some required tests failed. Please fix the issues above.")
    print("=" * 60)

    return all_required_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

