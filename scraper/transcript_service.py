#!/usr/bin/env python3
"""
backrAI Transcript Service
Fetches YouTube video transcripts and metadata WITHOUT a browser.

Primary: youtube-transcript-api (fastest, no API key, no browser)
Secondary: yt-dlp for metadata (description, channel info — no browser)
"""

import json
import os
import shutil
import subprocess
import sys
import re
from typing import Optional, Dict, List


def _find_ytdlp() -> str:
    """Find yt-dlp binary. Checks venv bin dir first, then PATH."""
    # Check same directory as the running Python interpreter
    venv_bin = os.path.dirname(sys.executable)
    venv_ytdlp = os.path.join(venv_bin, "yt-dlp")
    if os.path.isfile(venv_ytdlp):
        return venv_ytdlp
    # Fall back to system PATH
    path = shutil.which("yt-dlp")
    if path:
        return path
    return "yt-dlp"  # Let subprocess handle the FileNotFoundError


# Resolve once at import time
_YTDLP_BIN = _find_ytdlp()


class TranscriptService:
    """
    Fetches YouTube video transcripts and metadata without a browser.
    All methods are static — no initialization, no cleanup needed.
    """

    @staticmethod
    def get_transcript(video_id: str) -> Optional[str]:
        """
        Get full transcript text for a YouTube video.
        Returns concatenated transcript string or None.

        Tries English first, falls back to auto-generated, then any language.
        Uses youtube-transcript-api (no browser, no API key).
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            # Try English (manual or auto-generated)
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=["en"]
                )
                return " ".join(
                    segment["text"] for segment in transcript_list
                )
            except Exception:
                pass

            # Try any available language
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                return " ".join(
                    segment["text"] for segment in transcript_list
                )
            except Exception:
                pass

            return None

        except ImportError:
            print("⚠️  youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
            return None
        except Exception as e:
            # Silently return None — caller will handle missing transcript
            return None

    @staticmethod
    def get_video_metadata(video_id: str) -> Optional[Dict]:
        """
        Get video metadata using yt-dlp (no browser).
        Returns dict with: title, description, channel_id, channel_name,
                          channel_url, upload_date, view_count, duration, tags.
        """
        try:
            result = subprocess.run(
                [
                    _YTDLP_BIN,
                    "--dump-json",
                    "--no-download",
                    "--no-warnings",
                    "--no-check-certificates",
                    f"https://www.youtube.com/watch?v={video_id}",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                return {
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "channel_id": data.get("channel_id", ""),
                    "channel_name": data.get("channel", "") or data.get("uploader", ""),
                    "channel_url": data.get("channel_url", ""),
                    "uploader_id": data.get("uploader_id", ""),
                    "upload_date": data.get("upload_date", ""),
                    "view_count": data.get("view_count", 0),
                    "duration": data.get("duration", 0),
                    "tags": data.get("tags", []),
                }
            return None
        except subprocess.TimeoutExpired:
            return None
        except FileNotFoundError:
            print("⚠️  yt-dlp not installed. Run: pip install yt-dlp")
            return None
        except Exception:
            return None

    @staticmethod
    def search_videos(query: str, max_results: int = 20) -> List[Dict]:
        """
        Search YouTube using yt-dlp (no API key needed).
        Returns list of video metadata dicts with video_id, title, channel info.
        """
        try:
            result = subprocess.run(
                [
                    _YTDLP_BIN,
                    "--dump-json",
                    "--no-download",
                    "--no-warnings",
                    "--no-check-certificates",
                    "--flat-playlist",
                    f"ytsearch{max_results}:{query}",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            videos = []
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        video_id = data.get("id", "")
                        if video_id:
                            videos.append({
                                "video_id": video_id,
                                "title": data.get("title", ""),
                                "channel_id": data.get("channel_id", ""),
                                "channel_name": (
                                    data.get("channel", "")
                                    or data.get("uploader", "")
                                    or ""
                                ),
                                "channel_url": data.get("channel_url", ""),
                                "url": data.get("url", f"https://www.youtube.com/watch?v={video_id}"),
                                "duration": data.get("duration"),
                                "view_count": data.get("view_count"),
                            })
                    except json.JSONDecodeError:
                        continue
            return videos
        except subprocess.TimeoutExpired:
            return []
        except FileNotFoundError:
            print("⚠️  yt-dlp not installed. Run: pip install yt-dlp")
            return []
        except Exception:
            return []

    @staticmethod
    def get_channel_video_ids(
        channel_url: str, max_videos: int = 50
    ) -> List[str]:
        """
        Get recent video IDs from a YouTube channel.
        Uses yt-dlp to list channel uploads without downloading.
        """
        # Ensure URL ends with /videos for upload listing
        url = channel_url.rstrip("/")
        if not url.endswith("/videos"):
            url = f"{url}/videos"

        try:
            result = subprocess.run(
                [
                    _YTDLP_BIN,
                    "--dump-json",
                    "--no-download",
                    "--no-warnings",
                    "--no-check-certificates",
                    "--flat-playlist",
                    "--playlist-end", str(max_videos),
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            video_ids = []
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        vid = data.get("id", "")
                        if vid:
                            video_ids.append(vid)
                    except json.JSONDecodeError:
                        continue
            return video_ids
        except subprocess.TimeoutExpired:
            return []
        except FileNotFoundError:
            print("⚠️  yt-dlp not installed. Run: pip install yt-dlp")
            return []
        except Exception:
            return []

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats.
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        # Maybe it's already just a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        return None
