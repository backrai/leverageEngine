#!/usr/bin/env python3
"""
backrAI Code Extractor
Standalone text-processing utilities for extracting discount codes,
brand indicators, and matching codes to brands.

No Playwright, no Supabase dependency — pure text processing.
Extracted and enhanced from youtube_scraper.py lines 266-298.
"""

import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse

# -------------------------------------------------------------------
# False positives — common uppercase strings that are NOT discount codes
# -------------------------------------------------------------------
FALSE_POSITIVES = {
    # Technical
    "HTTP", "HTTPS", "WWW", "COM", "ORG", "NET", "HTML", "CSS", "JSON",
    "API", "SDK", "URL", "URI", "PDF", "PNG", "JPG", "GIF", "SVG",
    "MP4", "MP3", "USB", "CPU", "GPU", "RAM", "SSD", "HDD", "IOS",
    "VPN", "DNS", "FTP", "SSH", "SQL", "PHP", "XML", "TXT", "DOC",
    "EDU", "GOV", "APP", "APK",
    # YouTube / social media
    "SUBSCRIBE", "LIKE", "SHARE", "VIDEO", "VIDEOS", "COMMENT", "FOLLOW",
    "CHECK", "BELOW", "HERE", "MORE", "INFO", "ABOUT", "WATCH",
    "LIVE", "LINK", "CLICK", "LINKS", "CHANNEL", "PLAYLIST",
    "CONTENT", "CREATOR", "UPLOAD", "STREAM", "EPISODE", "PODCAST",
    "INTRO", "OUTRO", "TIMESTAMPS", "CHAPTERS",
    # Generic words (common in transcripts/descriptions)
    "FREE", "SALE", "SHOP", "BEST", "TRUE", "FALSE", "NULL", "NONE",
    "SELF", "THANKS", "THANK", "LOVE", "AMAZING", "GREAT", "GOOD",
    "THIS", "THAT", "WITH", "FROM", "YOUR", "HAVE", "BEEN", "WILL",
    "THEY", "THEM", "THAN", "THEN", "JUST", "ALSO", "ONLY", "VERY",
    "BACK", "MUCH", "SOME", "TIME", "WHAT", "WHEN", "WHERE", "WHICH",
    "MAKE", "MADE", "EACH", "MOST", "BOTH", "WELL", "LONG", "HIGH",
    "OVER", "SUCH", "TAKE", "LAST", "FIRST", "NEXT", "OPEN", "FULL",
    "SAVE", "MONEY", "DEAL", "DEALS", "OFFER", "OFFERS",
    "WORK", "WORKING", "WORKS", "STILL", "TODAY", "NEW", "TOP",
    "CODE", "CODES", "PROMO", "DISCOUNT", "COUPON", "COUPONS",
    "BOOK", "BOOKS", "SUPPORT", "HELP", "FIND", "SHOW", "LOOK",
    "NEED", "WANT", "KNOW", "THINK", "FEEL", "SURE", "REAL",
    "PART", "THING", "THINGS", "EVERY", "REALLY", "ACTUALLY",
    "PEOPLE", "WORLD", "PLACE", "YEAR", "YEARS", "LIFE",
    "RIGHT", "LEFT", "DOWN", "GOING", "COME", "CAME", "LOOK",
    "KEEP", "GIVE", "TALK", "TELL", "TOLD", "SAID", "SAYS",
    "BODY", "FOOD", "DIET", "MEAL", "WEIGHT", "TRAIN", "TRAINING",
    "WORKOUT", "FITNESS", "HEALTH", "HEALTHY", "MUSCLE", "PROTEIN",
    "SKIN", "HAIR", "FACE", "PRODUCT", "PRODUCTS", "REVIEW", "REVIEWS",
    "BRAND", "BRANDS", "COMPANY", "BUSINESS", "MARKET", "PRICE",
    "START", "STOP", "PLAY", "GAME", "GAMES", "LEVEL",
    "TEAM", "GROUP", "JOIN", "MEMBER", "SIGN",
    "EXPOSED", "TRUTH", "REAL", "FAKE", "SCAM", "LEGIT",
    "TEST", "TESTED", "TESTING", "RESULTS", "RESULT",
    "EDIT", "PHOTO", "CAMERA", "PHONE", "SCREEN",
    "DAY", "DAYS", "WEEK", "WEEKS", "MONTH", "MONTHS",
    "CALL", "TEXT", "EMAIL", "SEND", "POST", "SITE",
    # Short common words that slip through
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
    "CAN", "HER", "HIS", "ONE", "OUR", "OUT", "HAD", "HAS",
    "HOW", "ITS", "LET", "MAY", "OLD", "SEE", "WAY", "WHO",
    "DID", "GET", "GOT", "HIM", "SET", "TWO", "TEN",
    "RUN", "SAY", "SHE", "TOO", "USE", "DAD", "MOM",
    "BIG", "END", "FAR", "FEW", "OWN", "PUT", "RED", "TRY",
    "KEN", "KENNY", "BEN", "DAN", "BOB", "TOM", "JIM",
    # Country/currency codes
    "USD", "EUR", "GBP", "CAD", "AUD", "NZD",
    "USA", "UK",
}

# Known brand name patterns in codes (e.g., NIKE20 → Nike)
# This list helps match codes to brands when the code itself contains the brand name
BRAND_CODE_PREFIXES = [
    "NIKE", "ADIDAS", "GYMSHARK", "MYPROTEIN", "SEPHORA", "GLOSSIER",
    "HELLOFRESH", "NORDVPN", "EXPRESSVPN", "SURFSHARK", "SQUARESPACE",
    "SKILLSHARE", "AUDIBLE", "RIDGE", "MANSCAPED", "RAYCON", "MVMT",
    "CUTS", "ALO", "LULU", "GHOST", "GORILLA", "BLOOM", "LIQUID",
    "TRANSPARENT", "DBRAND", "AG1",
]


def _looks_like_real_code(code: str) -> bool:
    """
    Heuristic: does this look like a real discount code vs a random hash?

    Real codes look like: NIKE20, ALEX15, GYMSHARK10, SAVE50
    Random hashes look like: 0IMKOU, 8OR56J, XF4GQMHKLUZM1VIG7

    Rules:
    - Must start with a letter (not a digit)
    - Must not be all consonants (real codes have vowels: NIKE, ALEX, etc.)
    - Must not look like a base64/hex hash (high digit ratio with no pattern)
    """
    if not code or len(code) < 4:
        return False

    # Must start with a letter
    if not code[0].isalpha():
        return False

    # If it has both letters and digits, check the pattern
    has_letters = any(c.isalpha() for c in code)
    has_digits = any(c.isdigit() for c in code)

    if has_letters and has_digits:
        # Real codes typically end with digits: NIKE20, ALEX15
        # Or have a clear brand prefix: GYMSHARK10
        # Random hashes have digits interspersed: 0IM6KOU, 8OR56J
        letters = sum(1 for c in code if c.isalpha())
        digits = sum(1 for c in code if c.isdigit())

        # If more than 50% digits and code is 6+ chars, likely a hash
        if len(code) >= 6 and digits > letters:
            return False

        # If code has digits scattered in the middle of letters, likely a hash
        # Real codes: NAME + DIGITS pattern (e.g., ALEX15, NIKE20)
        # Check if digits are grouped at the end
        digit_positions = [i for i, c in enumerate(code) if c.isdigit()]
        if digit_positions:
            # All digits should be in the last N characters
            first_digit = digit_positions[0]
            letter_chars_after_digits = sum(
                1 for c in code[first_digit:] if c.isalpha()
            )
            # Allow at most 1 letter after the first digit (e.g., SAVE50X)
            if letter_chars_after_digits > 2 and len(code) >= 8:
                return False

    # Pure letter codes of 4+ chars are fine if they passed other filters
    return True


def extract_codes_from_text(text: str) -> List[str]:
    """
    Extract discount codes from text using multiple regex patterns.
    Enhanced version of YouTubeScraper._extract_codes_from_text.

    Returns deduplicated list of uppercase codes found.
    """
    if not text:
        return []

    codes = []

    # Pattern 1: "code: ABC123" / "promo code ABC123" / "discount code: SAVE20"
    pattern1 = re.compile(
        r'(?:code|promo|discount|coupon)[\s:]*["\']?([A-Z0-9]{3,25})["\']?',
        re.IGNORECASE,
    )
    codes.extend(pattern1.findall(text))

    # Pattern 2: "use code ABC123" / "enter ABC123" / "try code SAVE20"
    pattern2 = re.compile(
        r'(?:use|enter|try|apply|redeem)[\s]+(?:code|promo|my\s+code)?[\s:]*["\']?([A-Z0-9]{3,25})["\']?',
        re.IGNORECASE,
    )
    codes.extend(pattern2.findall(text))

    # Pattern 3: "% off with CODE" / "$10 off with CODE"
    pattern3 = re.compile(
        r'(?:\d+%?\s*off|discount)\s+(?:with|using|code)\s+["\']?([A-Z0-9]{3,25})["\']?',
        re.IGNORECASE,
    )
    codes.extend(pattern3.findall(text))

    # Pattern 4: Standalone codes (all caps, 4-20 chars, mixed letters+digits)
    # Only pick up codes that have both letters AND digits to reduce false positives
    pattern4 = re.compile(r'\b([A-Z]{2,}[0-9]+[A-Z0-9]*)\b')
    potential_codes = pattern4.findall(text.upper())
    codes.extend(potential_codes)

    # Pattern 5: "link.com/CODE" or URL-embedded codes
    # Only match codes that look like real promo codes (letters+digits, readable)
    # NOT random hashes or URL parameters
    pattern5 = re.compile(
        r'(?:https?://)?[\w.-]+\.[\w]+/([A-Z][A-Z0-9]{3,15})\b',
        re.IGNORECASE,
    )
    url_codes = pattern5.findall(text)
    for code in url_codes:
        upper = code.upper()
        if upper not in FALSE_POSITIVES and len(code) >= 4:
            # Skip if it looks like a random hash (high entropy)
            if not _looks_like_real_code(upper):
                continue
            codes.append(code)

    # Deduplicate, uppercase, filter
    unique_codes = set()
    result = []
    for code in codes:
        cleaned = code.upper().strip().strip("'\"")
        if not cleaned or cleaned in unique_codes or cleaned in FALSE_POSITIVES:
            continue
        # Length filter: real discount codes are 4-20 chars
        if not (4 <= len(cleaned) <= 20):
            continue
        if not cleaned.isalnum():
            continue
        # Skip codes that look like random hashes/IDs
        if not _looks_like_real_code(cleaned):
            continue
        # Skip pure-letter codes from Pattern 4 (already filtered by regex, but
        # Patterns 1-3 might still pick them up). Only skip if no digits AND
        # not captured by a strong context pattern (Patterns 1-3).
        # We allow pure-letter codes only if they have a known brand prefix.
        if cleaned.isalpha() and len(cleaned) <= 6:
            # Short all-letter codes are almost always false positives
            # unless matched by brand prefix
            is_brand_prefix = any(
                cleaned.startswith(p) for p in BRAND_CODE_PREFIXES
            )
            if not is_brand_prefix:
                continue
        unique_codes.add(cleaned)
        result.append(cleaned)

    return result


def extract_codes_with_context(text: str) -> List[Dict[str, str]]:
    """
    Enhanced extraction that captures surrounding context for each code.
    Returns list of {code, context, probable_brand} dicts.
    The 'context' is ~150 chars around the code match.
    The 'probable_brand' is a guess from context (may be None).
    """
    if not text:
        return []

    codes = extract_codes_from_text(text)
    results = []
    text_upper = text.upper()

    for code in codes:
        # Find code position in text for context extraction
        idx = text_upper.find(code)
        if idx == -1:
            # Try case-insensitive search
            idx = text.upper().find(code.upper())

        if idx >= 0:
            start = max(0, idx - 150)
            end = min(len(text), idx + len(code) + 150)
            context = text[start:end].strip()
        else:
            context = ""

        # Try to guess brand from code and context
        probable_brand = _guess_brand_from_code(code, context)

        results.append({
            "code": code,
            "context": context,
            "probable_brand": probable_brand,
        })

    return results


def extract_brand_indicators(text: str) -> List[Dict[str, str]]:
    """
    Find brand mentions in text: URLs, @mentions, domain references.
    Returns list of {name, domain, source_type} dicts.
    """
    if not text:
        return []

    indicators = []
    seen_domains = set()

    # Pattern: URLs with domains (http://brand.com or www.brand.com)
    url_pattern = re.compile(
        r'(?:https?://)?(?:www\.)?([a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.(?:com|co|io|net|org|shop|store|xyz))\b',
        re.IGNORECASE,
    )
    for match in url_pattern.finditer(text):
        domain = match.group(1).lower()
        if domain not in seen_domains and len(domain) > 4:
            # Skip common non-brand domains
            skip_domains = {
                "youtube.com", "youtu.be", "twitter.com", "x.com",
                "instagram.com", "tiktok.com", "facebook.com", "reddit.com",
                "google.com", "amazon.com", "linktr.ee", "bit.ly",
                "patreon.com", "paypal.com", "ko-fi.com", "gofundme.com",
                "discord.gg", "discord.com", "twitch.tv", "spotify.com",
                "apple.com", "github.com", "linkedin.com", "pinterest.com",
            }
            if domain not in skip_domains:
                name = domain.split(".")[0].title()
                seen_domains.add(domain)
                indicators.append({
                    "name": name,
                    "domain": domain,
                    "source_type": "url",
                })

    # Pattern: Affiliate/sponsor links with tracking params
    aff_pattern = re.compile(
        r'(?:https?://)?[\w.-]+\.[\w]+/[\w/-]*\?[^"\s]*(?:ref|aff|utm|code|coupon)=[^"\s&]+',
        re.IGNORECASE,
    )
    for match in aff_pattern.finditer(text):
        try:
            parsed = urlparse(match.group(0) if "://" in match.group(0) else f"http://{match.group(0)}")
            domain = parsed.netloc.lower().replace("www.", "")
            if domain and domain not in seen_domains:
                name = domain.split(".")[0].title()
                seen_domains.add(domain)
                indicators.append({
                    "name": name,
                    "domain": domain,
                    "source_type": "affiliate_url",
                })
        except Exception:
            pass

    return indicators


def match_code_to_brand(
    code: str,
    context: str,
    known_brands: List[Dict[str, str]],
) -> Optional[Dict[str, str]]:
    """
    Given a code and its surrounding context, determine which brand it belongs to.

    Strategy (priority order):
    1. Code contains brand name (e.g., NIKE20 → Nike)
    2. Context mentions a known brand domain (e.g., "gymshark.com")
    3. Context mentions a known brand name

    Args:
        code: The discount code (e.g., "NIKE20")
        context: ~150 chars surrounding the code in source text
        known_brands: List of dicts with 'id', 'name', 'domain_pattern'

    Returns:
        Matched brand dict or None
    """
    if not known_brands:
        return None

    code_upper = code.upper()
    context_lower = context.lower() if context else ""

    # Strategy 1: Code contains brand name
    for brand in known_brands:
        brand_name = brand.get("name", "")
        brand_name_clean = re.sub(r"[^a-z0-9]", "", brand_name.lower())
        if len(brand_name_clean) >= 3 and brand_name_clean in code_upper.lower():
            return brand

    # Also check known brand code prefixes
    for prefix in BRAND_CODE_PREFIXES:
        if code_upper.startswith(prefix):
            for brand in known_brands:
                brand_name_clean = re.sub(
                    r"[^a-z0-9]", "", brand.get("name", "").lower()
                )
                if prefix.lower().startswith(brand_name_clean[:4]):
                    return brand

    # Strategy 2: Context mentions a brand domain
    for brand in known_brands:
        domain = brand.get("domain_pattern", "").lower()
        if domain and domain in context_lower:
            return brand

    # Strategy 3: Context mentions a brand name (case-insensitive)
    for brand in known_brands:
        brand_name = brand.get("name", "")
        if len(brand_name) >= 3 and brand_name.lower() in context_lower:
            return brand

    return None


def _guess_brand_from_code(code: str, context: str) -> Optional[str]:
    """
    Heuristic: guess a brand name from a discount code and its context.
    Returns a brand name string or None.
    """
    code_upper = code.upper()

    # Check known prefixes
    for prefix in BRAND_CODE_PREFIXES:
        if code_upper.startswith(prefix):
            return prefix.title()

    # Try to extract brand from context around the code
    if context:
        # Look for "at BRAND" / "for BRAND" / "from BRAND" near the code
        brand_pattern = re.compile(
            r'(?:at|for|from|on)\s+([A-Z][A-Za-z0-9\s]{2,20}?)(?:\s+|[,.\-!])',
            re.IGNORECASE,
        )
        match = brand_pattern.search(context)
        if match:
            brand_guess = match.group(1).strip()
            # Filter out generic words
            if brand_guess.upper() not in FALSE_POSITIVES and len(brand_guess) >= 3:
                return brand_guess

    return None
