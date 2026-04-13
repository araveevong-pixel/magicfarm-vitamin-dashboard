#!/usr/bin/env python3
"""
TikTok Scraper for Magic Farm Vitamin 2026
Scrapes views, likes, shares, comments, saves from TikTok video pages.
Uses yt-dlp for accurate data (including saves/collectCount).
Falls back to urllib+regex if yt-dlp fails.
Output: JSON file with KOL metrics.
"""

import json
import re
import sys
import time
import subprocess
import urllib.request
import urllib.error
import ssl

# === KOL VIDEO LINKS ===
KOL_LINKS = {
    'janesaowaluk': 'https://vt.tiktok.com/ZSHjeYw5F/',
    'siriwan040541': 'https://vt.tiktok.com/ZSHMcUwyT/',
    'ntkling': 'https://vt.tiktok.com/ZSHhG79DT/',
    'jamjiramaoon': 'https://vt.tiktok.com/ZSH5hy7Tg/',
    'bbew_ddear': 'https://vt.tiktok.com/ZSHyyjQ7p/',
    'mildmint.1': 'https://vt.tiktok.com/ZSHmUc8ef/',
    'party_saran': 'https://vt.tiktok.com/ZSHmS59ap/',
    'pluemwattanathon': 'https://vt.tiktok.com/ZSHmAPang/',
    'bee112711': 'https://vt.tiktok.com/ZSHubfXt5/',
    'bass__inmeesub': 'https://vt.tiktok.com/ZSHmMEMu2/',
    'milin_wongsa': 'https://www.tiktok.com/@milin_wongsa/video/7627008489604369684',
    'on_supaporn': 'https://vt.tiktok.com/ZSHxQ3y1L/',
    'phanwasa.4': 'https://vt.tiktok.com/ZSHxh72uX/',
    'f52hz_': 'https://vt.tiktok.com/ZSHXMaYvL/',
    'somjeedna': 'https://vt.tiktok.com/ZSH4xYktY/',
    # เพิ่ม KOL ใหม่ที่โพสต์แล้วตรงนี้:
}


def scrape_with_ytdlp(url):
    """Scrape metrics using yt-dlp (gets saves/collectCount)."""
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', '--no-warnings', url],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            # Retry with --age-limit for age-restricted content
            if 'comfortable' in result.stderr or 'Log in' in result.stderr:
                print(f"    Age-restricted, retrying with --age-limit 99...")
                result = subprocess.run(
                    ['yt-dlp', '--dump-json', '--no-download', '--no-warnings',
                     '--age-limit', '99', url],
                    capture_output=True, text=True, timeout=60
                )
            if result.returncode != 0:
                return None

        info = json.loads(result.stdout)

        # Debug: show available count fields
        debug_keys = {k: v for k, v in info.items()
                      if any(word in k.lower() for word in ['count', 'save', 'collect', 'favorite', 'bookmark'])}
        if debug_keys:
            print(f"    [DEBUG] count fields: {debug_keys}")

        return {
            'views': int(info.get('view_count', 0) or 0),
            'likes': int(info.get('like_count', 0) or 0),
            'shares': int(info.get('repost_count', 0) or 0),
            'comments': int(info.get('comment_count', 0) or 0),
            'saves': int(info.get('save_count')
                        or info.get('collect_count')
                        or info.get('favorite_count')
                        or info.get('bookmark_count')
                        or 0),
            'followers': int(info.get('channel_follower_count', 0) or 0),
        }
    except Exception as e:
        print(f"  yt-dlp failed: {e}")
        return None


def scrape_with_urllib(url, retries=3):
    """Fallback: scrape metrics using urllib + regex."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            data = {}

            # Method 1: JSON-LD
            json_ld = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
            if json_ld:
                try:
                    ld = json.loads(json_ld.group(1))
                    data['views'] = int(ld.get('interactionStatistic', [{}])[0].get('userInteractionCount', 0)) if ld.get('interactionStatistic') else 0
                    data['likes'] = int(ld.get('interactionStatistic', [{}])[1].get('userInteractionCount', 0)) if len(ld.get('interactionStatistic', [])) > 1 else 0
                    data['comments'] = int(ld.get('commentCount', 0))
                except:
                    pass

            # Method 2: Regex patterns
            patterns = {
                'views': [r'"playCount"\s*:\s*(\d+)', r'"viewCount"\s*:\s*(\d+)'],
                'likes': [r'"diggCount"\s*:\s*(\d+)', r'"likeCount"\s*:\s*(\d+)'],
                'shares': [r'"shareCount"\s*:\s*(\d+)'],
                'comments': [r'"commentCount"\s*:\s*(\d+)'],
                'saves': [r'"collectCount"\s*:\s*(\d+)', r'"saveCount"\s*:\s*(\d+)'],
                'followers': [r'"followerCount"\s*:\s*(\d+)'],
            }

            for key, pats in patterns.items():
                if key not in data or data[key] == 0:
                    for pat in pats:
                        m = re.search(pat, html)
                        if m:
                            data[key] = int(m.group(1))
                            break

            return {
                'views': data.get('views', 0),
                'likes': data.get('likes', 0),
                'shares': data.get('shares', 0),
                'comments': data.get('comments', 0),
                'saves': data.get('saves', 0),
                'followers': data.get('followers', 0),
            }

        except Exception as e:
            print(f"  urllib attempt {attempt+1} failed: {e}")
            time.sleep(2)

    return None


def scrape_tiktok(url):
    """Scrape TikTok: try yt-dlp first, fall back to urllib."""
    # Try yt-dlp first (gets saves)
    data = scrape_with_ytdlp(url)
    if data and data['views'] > 0:
        print(f"  (yt-dlp)")
        return data

    # Fallback to urllib
    print(f"  (fallback to urllib)")
    data = scrape_with_urllib(url)
    return data


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'scrape_results.json'

    results = {}
    for username, link in KOL_LINKS.items():
        print(f"Scraping {username} ({link})...")
        data = scrape_tiktok(link)
        if data:
            results[username] = data
            print(f"  ✅ views={data['views']}, likes={data['likes']}, shares={data['shares']}, comments={data['comments']}, saves={data['saves']}")
        else:
            print(f"  ❌ Failed to scrape")
        time.sleep(1)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📁 Results saved to {output_file}")
    print(f"   {len(results)}/{len(KOL_LINKS)} KOLs scraped successfully")


if __name__ == '__main__':
    main()
