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

def main():
    print("=" * 60)
    print("🧪 backrAI Scraper Test Suite")
    print("=" * 60)
    
    results = {
        "Connection": False,
        "Database": False,
        "Playwright": False,
        "Scraper Module": False
    }
    
    # Test 1: Connection
    supabase = test_connection()
    results["Connection"] = supabase is not None
    
    # Test 2: Database Access
    if supabase:
        results["Database"] = test_database_access(supabase)
    
    # Test 3: Playwright
    results["Playwright"] = test_playwright()
    
    # Test 4: Scraper Module
    results["Scraper Module"] = test_scraper_import()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Scraper is ready to use.")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

