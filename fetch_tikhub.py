#!/usr/bin/env python3
"""
Fetch trending TikTok data via TikHub API.
Replaces the old TikTokApi-based comments.py with a more reliable solution.
"""

import os
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter
import re

# Configuration
BASE_URL = "https://api.tikhub.io"

def get_headers():
    """Get API headers with the current API key."""
    api_key = os.environ.get("TIKHUB_API_KEY", "")
    return {"Authorization": f"Bearer {api_key}"}

# Paths
SCRIPT_DIR = Path(__file__).parent
COVERS_DIR = SCRIPT_DIR / "images" / "covers"
AVATARS_DIR = SCRIPT_DIR / "images" / "avatars"
DATA_FILE = SCRIPT_DIR / "dashboard_data.json"


def fetch_explore_videos(count: int = 30) -> List[Dict]:
    """Fetch trending/explore videos from TikHub."""
    url = f"{BASE_URL}/api/v1/tiktok/web/fetch_explore_post"
    params = {"count": count}
    
    try:
        resp = requests.get(url, headers=get_headers(), params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") == 200:
            items = data.get("data", {}).get("itemList", [])
            print(f"✅ Fetched {len(items)} trending videos")
            return items
        else:
            print(f"❌ API error: {data.get('message')}")
            return []
    except Exception as e:
        print(f"❌ Error fetching videos: {e}")
        return []


def fetch_video_comments(video_id: str, count: int = 20) -> List[Dict]:
    """Fetch comments for a specific video."""
    url = f"{BASE_URL}/api/v1/tiktok/web/fetch_post_comment"
    params = {"aweme_id": video_id, "count": count}
    
    try:
        resp = requests.get(url, headers=get_headers(), params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") == 200:
            comments = data.get("data", {}).get("comments", [])
            return comments if comments else []
        return []
    except Exception as e:
        print(f"  ⚠️ Error fetching comments for {video_id}: {e}")
        return []


def download_image(url: str, dest_dir: Path, prefix: str = "") -> Optional[str]:
    """Download an image and return the local filename."""
    if not url:
        return None
    
    # Create a hash-based filename to avoid duplicates
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    ext = ".jpg"  # TikTok images are typically JPEG
    filename = f"{prefix}{url_hash}{ext}"
    filepath = dest_dir / filename
    
    # Skip if already exists
    if filepath.exists():
        return filename
    
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(resp.content)
        return filename
    except Exception as e:
        print(f"  ⚠️ Failed to download image: {e}")
        return None


def extract_phrases(comments: List[str], limit: int = 30) -> List[Dict]:
    """Extract common 2-4 word phrases from comments."""
    stopwords = set([
        'the', 'and', 'for', 'that', 'with', 'this', 'you', 'your', 'are', 'was',
        'but', 'not', 'have', 'has', 'just', 'like', 'get', 'got', 'all', 'out',
        'too', 'can', 'she', 'him', 'her', 'his', 'our', 'they', 'from', 'who',
        'had', 'did', 'its', 'i', 'me', 'my', 'we', 'he', 'it', 'to', 'of', 'in',
        'on', 'is', 'a', 'an', 'at', 'as', 'so', 'be', 'by', 'or', 'if', 'do',
        'no', 'yes', 'up', 'down', 'off', 'lol', 'lmao', 'omg', 'im', 'u', 'ur'
    ])
    
    def clean_text(text):
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()
    
    def get_ngrams(words, n):
        return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    
    phrase_counter = Counter()
    for comment in comments:
        if not comment or len(comment.strip()) < 4:
            continue
        cleaned = clean_text(comment)
        words = [w for w in cleaned.split() if w not in stopwords and len(w) > 1]
        if len(words) < 2:
            continue
        for n in range(2, 5):
            ngrams = get_ngrams(words, n)
            for ng in ngrams:
                if len(ng.split()) == n:
                    phrase_counter[ng] += 1
    
    # Filter low-frequency phrases
    filtered = [(p, c) for p, c in phrase_counter.most_common(limit * 2) if c >= 2]
    return [{"phrase": p, "count": c} for p, c in filtered[:limit]]


def main():
    """Main function to fetch data and build dashboard JSON."""
    print("🚀 TikHub Data Fetcher")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    if not os.environ.get("TIKHUB_API_KEY"):
        print("❌ TIKHUB_API_KEY environment variable not set!")
        return False
    
    # Fetch trending videos (max ~30 per request)
    videos = fetch_explore_videos(count=30)
    if not videos:
        print("❌ No videos fetched, aborting.")
        return False
    
    # Process videos and fetch comments
    processed_videos = []
    all_comments = []
    all_hashtags = []
    top_comments = []
    
    for i, video in enumerate(videos):
        video_id = video.get("id")
        author = video.get("author", {})
        stats = video.get("stats", {})
        video_data = video.get("video", {})
        
        print(f"\n📹 [{i+1}/{len(videos)}] Processing {video_id}...")
        print(f"   Author: @{author.get('uniqueId', 'unknown')}")
        print(f"   Likes: {stats.get('diggCount', 0):,}")
        
        # Download cover image
        cover_url = video_data.get("cover") or video_data.get("originCover")
        cover_file = download_image(cover_url, COVERS_DIR, f"cover_{video_id}_")
        
        # Download avatar
        avatar_url = author.get("avatarMedium")
        avatar_file = download_image(avatar_url, AVATARS_DIR, f"avatar_")
        
        # Fetch comments
        comments = fetch_video_comments(video_id, count=20) or []
        print(f"   Comments fetched: {len(comments)}")
        
        for comment in comments:
            text = comment.get("text", "")
            likes = comment.get("digg_count", 0)
            comment_author = comment.get("user", {}).get("unique_id", "unknown")
            
            if text:
                all_comments.append(text)
                top_comments.append({
                    "text": text,
                    "author": comment_author,
                    "likes_count": likes,
                    "video_id": video_id
                })
        
        # Extract hashtags
        challenges = video.get("challenges", [])
        for challenge in challenges:
            tag = challenge.get("title")
            if tag:
                all_hashtags.append(tag)
        
        # Build processed video entry
        processed_videos.append({
            "video_id": video_id,
            "author": author.get("uniqueId", "unknown"),
            "author_avatar_local": f"images/avatars/{avatar_file}" if avatar_file else None,
            "cover_local": f"images/covers/{cover_file}" if cover_file else None,
            "likes_count": stats.get("diggCount", 0),
            "comment_count": stats.get("commentCount", 0),
            "play_count": stats.get("playCount", 0),
            "share_count": stats.get("shareCount", 0),
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Build dashboard data
    print("\n📊 Building dashboard data...")
    
    # Sort top comments by likes
    top_comments.sort(key=lambda x: x["likes_count"], reverse=True)
    
    # Count hashtags
    hashtag_counts = Counter(all_hashtags)
    trending_hashtags = [{"hashtag": h, "count": c} for h, c in hashtag_counts.most_common(20)]
    
    # Calculate stats
    total_likes = sum(v["likes_count"] for v in processed_videos)
    total_comments = sum(v["comment_count"] for v in processed_videos)
    
    dashboard_data = {
        "stats": {
            "total_videos": len(processed_videos),
            "total_comments": len(all_comments),
            "total_hashtags": len(all_hashtags),
            "avg_likes_per_video": round(total_likes / len(processed_videos), 2) if processed_videos else 0,
            "avg_comments_per_video": round(total_comments / len(processed_videos), 2) if processed_videos else 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "hashtags": trending_hashtags,
        "top_phrases": extract_phrases(all_comments, limit=30),
        "top_comments": top_comments[:10],
        "recent_videos": processed_videos[:10]
    }
    
    # Write to file
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dashboard data saved to {DATA_FILE}")
    print(f"   Videos: {len(processed_videos)}")
    print(f"   Comments: {len(all_comments)}")
    print(f"   Hashtags: {len(trending_hashtags)}")
    print(f"   Images cached: {len(list(COVERS_DIR.glob('*.jpg')))} covers, {len(list(AVATARS_DIR.glob('*.jpg')))} avatars")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
