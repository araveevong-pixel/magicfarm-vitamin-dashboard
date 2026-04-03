#!/usr/bin/env python3
"""
TikTok Scraper for Magic Farm Vitamin 2026
Scrapes views, likes, shares, comments, saves from TikTok video pages.
Output: JSON file with KOL metrics.
"""

import json
import re
import sys
import time
import urllib.request
import urllib.error
import ssl

# === KOL VIDEO LINKS ===
KOL_LINKS = {
    'janesaowaluk': 'https://vt.tiktok.com/ZSHjeYw5F/',
    'siriwan040541': 'https://vt.tiktok.com/ZSHMcUwyT/',
    'ntkling': 'https://vt.tiktok.com/ZSHhj6w1E/',
    # เพิ่ม KOL ใหม่ที่โพสต์แล้วตรงนี้:
}

def scrape_tiktok(url, retries=3):
    """Scrape metrics from a TikTok video URL."""
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

            # Try to find SIGI_STATE or __UNIVERSAL_DATA
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

            # Method 2: Regex patterns from page source
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
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(2)

    return None


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
