#!/usr/bin/env python3
"""
Unit tests for code_extractor.py.
Pure-function tests — no network, no DB, no Playwright.
Should run in CI on every push.
"""

import sys
import os

# Ensure scraper directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from code_extractor import (
    extract_codes_from_text,
    extract_codes_with_context,
    extract_brand_indicators,
    match_code_to_brand,
)


def test_pattern_code_colon():
    """Pattern 1: 'code: ABC123' / 'promo code SAVE20'"""
    assert "ALEX15" in extract_codes_from_text("Use my code: ALEX15 for 15% off")
    assert "SUMMER2025" in extract_codes_from_text("Promo code SUMMER2025")
    assert "SAVE30" in extract_codes_from_text("discount code: SAVE30")
    assert "GYM50" in extract_codes_from_text("coupon GYM50 at checkout")
    print("  ✅ Pattern 1 (code colon): PASS")


def test_pattern_use_code():
    """Pattern 2: 'use code ABC123' / 'enter SAVE20'"""
    assert "MKBHD10" in extract_codes_from_text("Use code MKBHD10 for 10% off")
    assert "BEAST20" in extract_codes_from_text("enter BEAST20 at checkout")
    assert "GYMSHARK15" in extract_codes_from_text("try my code GYMSHARK15")
    assert "ALEX20" in extract_codes_from_text("apply code ALEX20")
    print("  ✅ Pattern 2 (use code): PASS")


def test_pattern_percent_off():
    """Pattern 3: '% off with CODE'"""
    assert "SARAH10" in extract_codes_from_text("Get 10% off with SARAH10")
    assert "FLAT50" in extract_codes_from_text("50% off using code FLAT50")
    print("  ✅ Pattern 3 (% off with): PASS")


def test_pattern_standalone():
    """Pattern 4: Standalone uppercase alphanumeric (must have letters+digits)"""
    codes = extract_codes_from_text("Check out the deal: NIKE20 is great")
    assert "NIKE20" in codes
    # Pure letters should NOT match pattern 4 (reduces false positives)
    codes2 = extract_codes_from_text("AMAZING deal today on PRODUCT items")
    assert "AMAZING" not in codes2
    assert "PRODUCT" not in codes2
    print("  ✅ Pattern 4 (standalone): PASS")


def test_false_positive_rejection():
    """Common words like HTTP, WWW, COM, SUBSCRIBE should be excluded."""
    text = "Visit HTTPS://WWW.example.COM and SUBSCRIBE for more AMAZING content"
    codes = extract_codes_from_text(text)
    for word in ["HTTPS", "WWW", "COM", "SUBSCRIBE", "AMAZING"]:
        assert word not in codes, f"False positive not rejected: {word}"
    print("  ✅ False positive rejection: PASS")


def test_deduplication():
    """Same code mentioned multiple times should only appear once."""
    text = "Use code ALEX15 for 15% off. Enter ALEX15 at checkout. ALEX15 works!"
    codes = extract_codes_from_text(text)
    assert codes.count("ALEX15") == 1
    print("  ✅ Deduplication: PASS")


def test_context_extraction():
    """extract_codes_with_context returns surrounding text."""
    text = "Hey everyone! I partnered with Gymshark and my code ALEX15 gets you 15% off everything on gymshark.com"
    results = extract_codes_with_context(text)
    assert len(results) > 0
    alex_result = next((r for r in results if r["code"] == "ALEX15"), None)
    assert alex_result is not None
    assert "gymshark" in alex_result["context"].lower()
    print("  ✅ Context extraction: PASS")


def test_brand_indicators():
    """extract_brand_indicators finds URLs and domains."""
    text = """
    Check out gymshark.com for the latest gear!
    Also visit https://www.myprotein.com/deals for protein.
    My link: https://nordvpn.com/creator?ref=alex
    Follow me on youtube.com and instagram.com
    """
    indicators = extract_brand_indicators(text)
    domains = [i["domain"] for i in indicators]
    # Should find brand domains but NOT social media
    assert "gymshark.com" in domains
    assert "myprotein.com" in domains
    assert "nordvpn.com" in domains
    # Should NOT include social media
    assert "youtube.com" not in domains
    assert "instagram.com" not in domains
    print("  ✅ Brand indicators: PASS")


def test_brand_matching_code_contains_name():
    """match_code_to_brand: code contains brand name (NIKE20 → Nike)."""
    known_brands = [
        {"id": "1", "name": "Nike", "domain_pattern": "nike.com"},
        {"id": "2", "name": "Adidas", "domain_pattern": "adidas.com"},
        {"id": "3", "name": "Gymshark", "domain_pattern": "gymshark.com"},
    ]
    match = match_code_to_brand("NIKE20", "", known_brands)
    assert match is not None
    assert match["name"] == "Nike"

    match2 = match_code_to_brand("GYMSHARK15", "", known_brands)
    assert match2 is not None
    assert match2["name"] == "Gymshark"
    print("  ✅ Brand matching (code contains name): PASS")


def test_brand_matching_context_domain():
    """match_code_to_brand: context mentions brand domain."""
    known_brands = [
        {"id": "1", "name": "Gymshark", "domain_pattern": "gymshark.com"},
        {"id": "2", "name": "MyProtein", "domain_pattern": "myprotein.com"},
    ]
    match = match_code_to_brand(
        "ALEX15",
        "Get 15% off at gymshark.com with my code",
        known_brands,
    )
    assert match is not None
    assert match["name"] == "Gymshark"
    print("  ✅ Brand matching (context domain): PASS")


def test_brand_matching_context_name():
    """match_code_to_brand: context mentions brand name."""
    known_brands = [
        {"id": "1", "name": "HelloFresh", "domain_pattern": "hellofresh.com"},
    ]
    match = match_code_to_brand(
        "COOK50",
        "Use my code at HelloFresh for $50 off your first box",
        known_brands,
    )
    assert match is not None
    assert match["name"] == "HelloFresh"
    print("  ✅ Brand matching (context name): PASS")


def test_brand_matching_no_match():
    """match_code_to_brand: returns None when no match found."""
    known_brands = [
        {"id": "1", "name": "Nike", "domain_pattern": "nike.com"},
    ]
    match = match_code_to_brand("RANDOM123", "some random context", known_brands)
    assert match is None
    print("  ✅ Brand matching (no match): PASS")


def test_empty_input():
    """All functions handle empty input gracefully."""
    assert extract_codes_from_text("") == []
    assert extract_codes_from_text(None) == []
    assert extract_codes_with_context("") == []
    assert extract_brand_indicators("") == []
    assert match_code_to_brand("CODE", "", []) is None
    print("  ✅ Empty input handling: PASS")


def test_real_world_description():
    """Test with a realistic YouTube video description."""
    description = """
    Thanks to Gymshark for sponsoring this video!
    Use code CHRIS20 for 20% off everything at https://www.gymshark.com

    Also check out AG1 - use my link: https://drinkag1.com/chris

    🏋️ My Training Program: https://cbum.com/training
    📱 Follow me on Instagram: @cbum

    Timestamps:
    0:00 - Intro
    1:30 - Workout starts
    15:00 - Meal prep
    20:00 - Outro

    Other codes:
    - NordVPN: use code CHRIS for 60% off at nordvpn.com/chris
    - MyProtein: CBUM25 for 25% off
    """
    codes = extract_codes_from_text(description)
    assert "CHRIS20" in codes
    assert "CBUM25" in codes

    indicators = extract_brand_indicators(description)
    domains = [i["domain"] for i in indicators]
    assert "gymshark.com" in domains
    assert "drinkag1.com" in domains
    assert "nordvpn.com" in domains

    # Context extraction should link CHRIS20 to Gymshark
    results = extract_codes_with_context(description)
    chris_result = next((r for r in results if r["code"] == "CHRIS20"), None)
    assert chris_result is not None
    assert "gymshark" in chris_result["context"].lower()

    print("  ✅ Real-world description: PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Code Extractor Unit Tests")
    print("=" * 60)

    tests = [
        test_pattern_code_colon,
        test_pattern_use_code,
        test_pattern_percent_off,
        test_pattern_standalone,
        test_false_positive_rejection,
        test_deduplication,
        test_context_extraction,
        test_brand_indicators,
        test_brand_matching_code_contains_name,
        test_brand_matching_context_domain,
        test_brand_matching_context_name,
        test_brand_matching_no_match,
        test_empty_input,
        test_real_world_description,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ {test.__name__}: FAIL - {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
