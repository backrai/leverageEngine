#!/usr/bin/env python3
"""
Quick test run of the scraper
Tests actual scraping functionality
"""

import asyncio
from scraper import CouponScraper, scrape_all_brands, validate_existing_offers

async def test_scrape_one_brand():
    """Test scraping for one brand"""
    print("=" * 60)
    print("🧪 Testing Scraper - Single Brand")
    print("=" * 60)
    
    scraper = CouponScraper()
    try:
        await scraper.initialize()
        print("✅ Browser initialized")
        
        # Test with Gymshark
        print("\n🔍 Testing code scraping for Gymshark...")
        codes = await scraper.scrape_coupon_sites("gymshark.com")
        
        print(f"✅ Found {len(codes)} potential codes")
        for code in codes[:5]:  # Show first 5
            print(f"   - {code.get('code', 'N/A')} ({code.get('discount', 'N/A')})")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await scraper.close()

async def test_validate_code():
    """Test code validation"""
    print("\n" + "=" * 60)
    print("🧪 Testing Code Validation")
    print("=" * 60)
    
    scraper = CouponScraper()
    try:
        await scraper.initialize()
        print("✅ Browser initialized")
        
        # Test validation (this will be slow)
        print("\n🔍 Testing code validation...")
        print("   (This may take a while as it visits the website)")
        
        # Test with a simple code (this might fail, but tests the function)
        test_code = "TEST123"
        is_valid = await scraper.validate_code("https://www.gymshark.com/checkout", test_code)
        
        print(f"✅ Validation test completed")
        print(f"   Code '{test_code}' validation result: {is_valid}")
        print("   (Note: This is just testing the function, not a real code)")
        
        return True
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False
    finally:
        await scraper.close()

def main():
    print("\n🚀 Running Scraper Tests\n")
    
    # Test 1: Scrape one brand
    result1 = asyncio.run(test_scrape_one_brand())
    
    # Test 2: Validate code (optional - can be slow)
    print("\n⚠️  Skipping validation test (can be slow)")
    print("   To test validation, uncomment the line below in the script")
    # result2 = asyncio.run(test_validate_code())
    
    print("\n" + "=" * 60)
    if result1:
        print("✅ Basic scraping test passed!")
        print("\n💡 Next steps:")
        print("   1. Run full scraper: python scraper.py")
        print("   2. Validate offers: python scraper.py validate")
    else:
        print("❌ Scraping test failed")
    print("=" * 60)

if __name__ == "__main__":
    main()

