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
    'nisakorn_pui': 'https://www.tiktok.com/@nisakorn_pui/video/7630386912565480711',
    # เพิ่ม KOL ใหม่ที่โพสต์แล้วตรงนี้:
}

# === LOT 2 KOL VIDEO LINKS ===
KOL_LINKS_LOT2 = {
    'kunofficial29': 'https://vt.tiktok.com/ZSxRPx9qL/',
    'aeaeyberry': 'https://vt.tiktok.com/ZSxy2KAd4/',
    'fymme_': 'https://vt.tiktok.com/ZSxMPH2fk/',
    'bonuss_19': 'https://vt.tiktok.com/ZS9cyHrXx/',
    'marumari141': 'https://vt.tiktok.com/ZSxR6R5sx/',
    'yanisskkk': 'https://vt.tiktok.com/ZSxRPpV8s/',
    'chanyanuch.hh': 'https://vt.tiktok.com/ZSxyj69dG/',
    'natkritta_taew': 'https://vt.tiktok.com/ZSxkTuPMM/',
    'pukjira45': 'https://vt.tiktok.com/ZSxQT9AJ5/',
    'benz_benzzzz12': 'https://vt.tiktok.com/ZSxgQkmQQ/',
    'mild.melody08': 'https://vt.tiktok.com/ZSxQC85Rk/',
    'yoke1645': 'https://vt.tiktok.com/ZSxQQKLTM/',
    'zaiisivaporn': 'https://vt.tiktok.com/ZSx3cjWLk/',
    'airfrostt_': 'https://vt.tiktok.com/ZSxc2wAPw/',
    'watermell': 'https://vt.tiktok.com/ZSQRFEPyK/',
    '_filmmwr': 'https://vt.tiktok.com/ZSQdTsv7j/',
    'kanyarat0640': 'https://vt.tiktok.com/ZSQJ8qRD3/',
    'momelontt': 'https://vt.tiktok.com/ZSQReyxar/',
    'kuanpuantiew': 'https://vt.tiktok.com/ZSQ8NrkFd/',
    'pang_urw': 'https://www.tiktok.com/@pang_urw/video/7649314817748077831',
}

# === MANUAL OVERRIDES ===
# For KOLs whose videos can't be scraped (e.g. age-restricted content),
# manually set their stats here. These are used as fallback when scraping returns 0.
# Update these values periodically by checking TikTok directly.
# Format: 'username': {'views': N, 'likes': N, 'shares': N, 'comments': N, 'saves': N, 'followers': N}
MANUAL_OVERRIDES = {
    'pang_urw': {
        'views': 543000,
        'likes': 944,
        'shares': 11,
        'comments': 8,
        'saves': 26,
        'followers': 283000,
        '_note': 'Age-restricted video, stats from 2026-06-22'
    },
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


def extract_video_id(url):
    """Extract TikTok video ID from URL."""
    m = re.search(r'/video/(\d+)', url)
    return m.group(1) if m else None


def scrape_with_tiktok_api(url, retries=3):
    """Fallback for age-restricted: use TikTok's web API endpoint."""
    video_id = extract_video_id(url)
    if not video_id:
        # Try to resolve short URL first to get video ID
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
            })
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                resolved = resp.url
            video_id = extract_video_id(resolved)
        except:
            pass
    if not video_id:
        print(f"  Could not extract video ID from {url}")
        return None

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Try TikTok web API
    api_url = f'https://www.tiktok.com/api/item/detail/?itemId={video_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.tiktok.com/',
    }

    for attempt in range(retries):
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8', errors='ignore'))

            item = data.get('itemInfo', {}).get('itemStruct', {})
            stats = item.get('stats', {})
            author = item.get('authorStats', {})

            if stats.get('playCount', 0) > 0:
                return {
                    'views': int(stats.get('playCount', 0)),
                    'likes': int(stats.get('diggCount', 0)),
                    'shares': int(stats.get('shareCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'saves': int(stats.get('collectCount', 0)),
                    'followers': int(author.get('followerCount', 0)),
                }
        except Exception as e:
            print(f"  TikTok API attempt {attempt+1} failed: {e}")
            time.sleep(2)

    # Try oEmbed as last resort (only gets basic info)
    try:
        oembed_url = f'https://www.tiktok.com/oembed?url=https://www.tiktok.com/@placeholder/video/{video_id}'
        req = urllib.request.Request(oembed_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            oembed = json.loads(resp.read().decode('utf-8', errors='ignore'))
        # oEmbed doesn't have counts, but confirms video exists
        print(f"  oEmbed found: {oembed.get('title', 'unknown')[:50]}")
    except:
        pass

    return None


def scrape_with_ytdlp_mobile(url):
    """Try yt-dlp with mobile extractor args for age-restricted content."""
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', '--no-warnings',
             '--extractor-args', 'tiktok:api_hostname=api16-normal-c-useast1a.tiktokv.com',
             url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return None

        info = json.loads(result.stdout)
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
        print(f"  yt-dlp mobile failed: {e}")
        return None


def scrape_tiktok(url):
    """Scrape TikTok: try yt-dlp first, then mobile API, then web API, then urllib."""
    # Try yt-dlp first (gets saves)
    data = scrape_with_ytdlp(url)
    if data and data['views'] > 0:
        print(f"  (yt-dlp)")
        return data

    # Try yt-dlp with mobile API endpoint (for age-restricted)
    print(f"  (trying yt-dlp mobile API...)")
    data = scrape_with_ytdlp_mobile(url)
    if data and data['views'] > 0:
        print(f"  (yt-dlp mobile)")
        return data

    # Try TikTok web API (for age-restricted)
    print(f"  (trying TikTok web API...)")
    data = scrape_with_tiktok_api(url)
    if data and data['views'] > 0:
        print(f"  (TikTok API)")
        return data

    # Final fallback to urllib
    print(f"  (fallback to urllib)")
    data = scrape_with_urllib(url)
    return data


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'scrape_results.json'

    results = {}

    # Scrape Lot 1
    print("=== Scraping Lot 1 ===")
    for username, link in KOL_LINKS.items():
        print(f"Scraping {username} ({link})...")
        data = scrape_tiktok(link)
        # Apply manual override if scraping returned 0 views
        if (not data or data.get('views', 0) == 0) and username in MANUAL_OVERRIDES:
            override = {k: v for k, v in MANUAL_OVERRIDES[username].items() if not k.startswith('_')}
            data = override
            print(f"  ⚠️ Using manual override (scraping failed/age-restricted)")
        if data:
            results[username] = data
            print(f"  ✅ views={data['views']}, likes={data['likes']}, shares={data['shares']}, comments={data['comments']}, saves={data['saves']}")
        else:
            print(f"  ❌ Failed to scrape")
        time.sleep(1)

    # Scrape Lot 2
    print("\n=== Scraping Lot 2 ===")
    for username, link in KOL_LINKS_LOT2.items():
        print(f"Scraping {username} ({link})...")
        data = scrape_tiktok(link)
        # Apply manual override if scraping returned 0 views
        if (not data or data.get('views', 0) == 0) and username in MANUAL_OVERRIDES:
            override = {k: v for k, v in MANUAL_OVERRIDES[username].items() if not k.startswith('_')}
            data = override
            print(f"  ⚠️ Using manual override (scraping failed/age-restricted)")
        if data:
            results[username] = data
            print(f"  ✅ views={data['views']}, likes={data['likes']}, shares={data['shares']}, comments={data['comments']}, saves={data['saves']}")
        else:
            print(f"  ❌ Failed to scrape")
        time.sleep(1)

    all_links = {**KOL_LINKS, **KOL_LINKS_LOT2}
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📁 Results saved to {output_file}")
    print(f"   {len(results)}/{len(all_links)} KOLs scraped successfully (Lot 1 + Lot 2)")


if __name__ == '__main__':
    main()
