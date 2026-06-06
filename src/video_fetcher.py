"""Fetch video subtitles/transcripts from B站 and YouTube."""

from __future__ import annotations

import os
import re
from pathlib import Path
import requests
from dataclasses import dataclass, field


@dataclass
class VideoTranscript:
    title: str
    platform: str  # "bilibili" | "youtube"
    full_text: str
    segments: list[dict] = field(default_factory=list)  # [{start, text}, ...]
    error: str = ""


# ── Public API ──────────────────────────────────────────────────────────

def fetch_transcript(url: str) -> VideoTranscript:
    """Fetch transcript from a B站 or YouTube video URL.

    Returns VideoTranscript with full_text populated on success,
    or error message set on failure.
    """
    # B站
    bv = _extract_bv(url)
    if bv:
        return _fetch_bilibili(bv)

    # YouTube
    video_id = _extract_youtube_id(url)
    if video_id:
        return _fetch_youtube(video_id)

    return VideoTranscript(
        title="",
        platform="",
        full_text="",
        error="无法识别的视频链接。请粘贴 B站 或 YouTube 视频链接。",
    )


# ── URL Parsing ─────────────────────────────────────────────────────────

def _extract_bv(url: str) -> str | None:
    """Extract BV号 from B站 URL."""
    # Direct BV号 extraction: look for BV followed by 10 alphanumeric chars
    m = re.search(r"BV[a-zA-Z0-9]{10}", url)
    if m:
        return m.group(0)
    return None


def _extract_youtube_id(url: str) -> str | None:
    """Extract video ID from YouTube URL."""
    m = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})", url)
    if m:
        return m.group(1)
    # Raw ID
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url.strip()):
        return url.strip()
    return None


# ── Bilibili ────────────────────────────────────────────────────────────

COOKIE_FILE = Path(__file__).resolve().parent.parent / "data" / "cookies" / "bilibili.txt"


def _load_bilibili_cookies() -> str:
    """Load Bilibili cookies from env var or Netscape-format file."""
    # 1. Environment variable (for deployment)
    env_cookie = os.environ.get("BILIBILI_COOKIE", "")
    if env_cookie:
        return env_cookie

    # 2. Cookie file (for local dev)
    if not COOKIE_FILE.exists():
        return ""
    cookies = {}
    for line in COOKIE_FILE.read_text().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 7:
            cookies[parts[5]] = parts[6]
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def _fetch_bilibili(bv: str) -> VideoTranscript:
    """Fetch subtitles from B站 video.

    Two paths:
    1. Player API (no cookies) — user-uploaded subtitles. Fast, always works.
    2. Wbi player API (with cookies) — AI-generated subtitles. Needs login.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.bilibili.com/",
    }

    try:
        # Step 1: Get video info + cid
        info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv}"
        resp = requests.get(info_url, headers=headers, timeout=15)
        data = resp.json()
        if data["code"] != 0:
            return VideoTranscript(
                title="", platform="bilibili",
                full_text="", error=f"无法获取视频信息 (code={data['code']})",
            )

        title = data["data"]["title"]
        cid = data["data"]["cid"]

        # Step 2: Try player API for user-uploaded subtitles (no cookies needed)
        subtitles = _get_subtitle_list(bv, cid, headers)

        # Step 3: No user subtitles — try Wbi API with cookies for AI字幕
        if not subtitles:
            cookie_str = _load_bilibili_cookies()
            if cookie_str:
                headers_with_auth = {**headers, "Cookie": cookie_str}
                subtitles = _get_subtitle_list_wbi(bv, cid, headers_with_auth)

        if not subtitles:
            has_cookies = COOKIE_FILE.exists()
            return VideoTranscript(
                title=title, platform="bilibili", full_text="",
                error=(
                    f"该视频没有可用字幕。\n\n"
                    f"「{title}」未开启 CC 字幕，"
                    + ("AI 字幕也未生成。" if has_cookies else "且未配置 B站 Cookie，无法获取 AI 字幕。")
                    + "\n建议：尝试另一个视频，或使用内置视频。"
                ),
            )

        # Step 4: Download and parse the best subtitle track
        best = _pick_best_subtitle(subtitles)
        sub_url = best.get("subtitle_url", "")
        if sub_url.startswith("//"):
            sub_url = "https:" + sub_url

        resp3 = requests.get(sub_url, headers=headers, timeout=15)
        sub_data = resp3.json()
        body = sub_data.get("body", [])

        if not body:
            return VideoTranscript(
                title=title, platform="bilibili", full_text="",
                error="字幕数据为空。",
            )

        segments = []
        lines = []
        for item in body:
            text = item.get("content", "").strip()
            start = item.get("from", 0)
            if text:
                segments.append({"start": start, "text": text})
                lines.append(text)

        return VideoTranscript(
            title=title,
            platform="bilibili",
            full_text="\n".join(lines),
            segments=segments,
        )

    except requests.RequestException as e:
        return VideoTranscript(
            title="", platform="bilibili",
            full_text="", error=f"网络请求失败：{e}",
        )
    except Exception as e:
        return VideoTranscript(
            title="", platform="bilibili",
            full_text="", error=f"解析失败：{e}",
        )


def _get_subtitle_list(bv: str, cid: int, headers: dict) -> list[dict]:
    """Get user-uploaded subtitles via public player API."""
    url = f"https://api.bilibili.com/x/player/v2?bvid={bv}&cid={cid}&fnver=0&fnval=4048"
    resp = requests.get(url, headers=headers, timeout=15)
    return (
        resp.json()
        .get("data", {})
        .get("subtitle", {})
        .get("subtitles", [])
    )


def _get_subtitle_list_wbi(bv: str, cid: int, headers: dict) -> list[dict]:
    """Get AI-generated subtitles via Wbi player API (requires cookie auth)."""
    url = f"https://api.bilibili.com/x/player/wbi/v2?bvid={bv}&cid={cid}&fnver=0&fnval=4048"
    resp = requests.get(url, headers=headers, timeout=15)
    return (
        resp.json()
        .get("data", {})
        .get("subtitle", {})
        .get("subtitles", [])
    )


def _pick_best_subtitle(subtitles: list[dict]) -> dict:
    """Pick the best subtitle track (prefer Chinese, then longest)."""
    # Priority: Chinese (zh) > any available
    for key in ["zh-Hans", "zh-CN", "zh", "ai-zh", "zh-Hant"]:
        for s in subtitles:
            lan = s.get("lan", "")
            if lan == key:
                return s
    # Fallback: first available
    return subtitles[0]


# ── YouTube ─────────────────────────────────────────────────────────────

def _fetch_youtube(video_id: str) -> VideoTranscript:
    """Fetch transcript from YouTube video."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=("zh-Hans", "zh-CN", "zh", "en"))
        data = transcript.to_raw_data()

        if not data:
            return VideoTranscript(
                title="", platform="youtube", full_text="",
                error="该视频没有可用的字幕/CC。",
            )

        segments = []
        lines = []
        for item in data:
            text = item.get("text", "").strip()
            start = item.get("start", 0)
            if text:
                segments.append({"start": start, "text": text})
                lines.append(text)

        full_text = "\n".join(lines)

        return VideoTranscript(
            title=f"YouTube {video_id}",
            platform="youtube",
            full_text=full_text,
            segments=segments,
        )

    except ImportError:
        return VideoTranscript(
            title="", platform="youtube", full_text="",
            error="youtube-transcript-api 未安装。",
        )
    except Exception as e:
        msg = str(e)
        if "TranscriptsDisabled" in msg or "subtitles are disabled" in msg.lower():
            return VideoTranscript(
                title="", platform="youtube", full_text="",
                error="该视频未开启字幕功能。",
            )
        if "NoTranscriptFound" in msg:
            return VideoTranscript(
                title="", platform="youtube", full_text="",
                error="该视频没有中文或英文字幕。",
            )
        return VideoTranscript(
            title="", platform="youtube",
            full_text="", error=f"获取 YouTube 字幕失败：{msg[:200]}",
        )
