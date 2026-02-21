#!/usr/bin/env python3
"""
backrAI SponsorBlock Service
Interface to the SponsorBlock crowdsourced API.
Identifies YouTube videos that contain sponsor segments (where discount codes
are most likely to appear).

Completely free, no API key required.
API docs: https://wiki.sponsor.ajay.app/w/API_Docs
"""

import hashlib
import time
from typing import List, Dict

import requests


SPONSORBLOCK_API = "https://sponsor.ajay.app/api"


class SponsorBlockService:
    """
    Interface to the SponsorBlock crowdsourced API.
    Identifies videos that contain sponsor segments.

    SponsorBlock is a browser extension with millions of users who
    crowdsource-label sponsor segments in YouTube videos. Their API
    lets us check if a video has known sponsor content — which means
    the creator was paid to promote something and likely shared a code.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "backrAI/1.0 (creator leverage engine)",
        })

    def has_sponsor_segments(self, video_id: str) -> bool:
        """Check if a video has known sponsor segments."""
        segments = self.get_sponsor_segments(video_id)
        return len(segments) > 0

    def get_sponsor_segments(self, video_id: str) -> List[Dict]:
        """
        Get sponsor segment timestamps for a video.
        Returns list of {start, end, category, duration} dicts.

        Categories include:
        - 'sponsor': Paid promotion segment
        - 'selfpromo': Creator promoting their own product/channel
        - 'interaction': Subscribe/like reminders

        Uses SponsorBlock's privacy-preserving hash prefix lookup.
        """
        try:
            # SponsorBlock uses SHA-256 hash prefix for privacy
            video_hash = hashlib.sha256(video_id.encode()).hexdigest()
            hash_prefix = video_hash[:4]

            response = self.session.get(
                f"{SPONSORBLOCK_API}/skipSegments/{hash_prefix}",
                params={
                    "categories": '["sponsor","selfpromo"]',
                },
                timeout=10,
            )

            if response.status_code == 200:
                results = response.json()
                # Filter to our specific video (hash prefix may match multiple)
                for result in results:
                    if result.get("videoID") == video_id:
                        return [
                            {
                                "start": seg["segment"][0],
                                "end": seg["segment"][1],
                                "category": seg.get("category", "sponsor"),
                                "duration": seg["segment"][1] - seg["segment"][0],
                            }
                            for seg in result.get("segments", [])
                        ]

            # 404 = no segments found (normal, not an error)
            return []

        except requests.exceptions.Timeout:
            return []
        except requests.exceptions.ConnectionError:
            return []
        except Exception:
            return []

    def batch_check_videos(
        self,
        video_ids: List[str],
        rate_limit_delay: float = 0.1,
    ) -> Dict[str, bool]:
        """
        Check multiple videos for sponsor segments.
        Returns {video_id: has_sponsors} mapping.

        Rate-limited to be a good API citizen (SponsorBlock is a
        community project — be respectful).
        """
        results = {}
        for vid in video_ids:
            results[vid] = self.has_sponsor_segments(vid)
            time.sleep(rate_limit_delay)
        return results

    def get_total_sponsor_time(self, video_id: str) -> float:
        """
        Get total seconds of sponsor content in a video.
        Returns 0.0 if no sponsor segments found.
        """
        segments = self.get_sponsor_segments(video_id)
        return sum(seg.get("duration", 0) for seg in segments)
