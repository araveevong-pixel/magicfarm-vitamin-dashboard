#!/usr/bin/env python3
"""
Update Dashboard — Magic Farm Vitamin 2026
Reads scrape_results.json and injects updated metrics into index.html KOL_DATA.
"""

import json
import re
import sys
import os

# === KOL METADATA FALLBACK ===
# ถ้า scraper return followers=0 จะใช้ค่าจากนี้แทน
KOL_METADATA = {
    'siriwan040541':    {'followers': 6400000, 'tier': 'Mega',  'category': 'ทำงานกลางแจ้ง', 'product': 'VitC',     'displayName': 'น้องจอย สมศรี',    'gender': 'ญ', 'budget': 25000},
    'janesaowaluk':     {'followers': 782800,  'tier': 'Macro', 'category': 'ทำงานกลางแจ้ง', 'product': 'Collagen', 'displayName': 'janesaowaluk',     'gender': 'ญ', 'budget': 20000},
    'nisakorn_pui':     {'followers': 898800,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Fiber',    'displayName': 'ปุ๋ย นิศา',        'gender': 'ญ', 'budget': 16000},
    'mildmint.1':       {'followers': 456400,  'tier': 'Macro', 'category': 'ทำงานกลางแจ้ง', 'product': 'Fiber',    'displayName': 'อรอุมา มายมินท์',  'gender': 'ญ', 'budget': 19000},
    'party_saran':      {'followers': 284800,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'party_saran',      'gender': 'ญ', 'budget': 18000},
    'pluemwattanathon':{'followers': 161100,  'tier': 'Macro', 'category': 'หนุ่มสาวโรงงาน', 'product': 'VitC',     'displayName': 'ผมชื่อปลื้ม',      'gender': 'ช', 'budget': 15000},
    'ntkling':          {'followers': 72700,   'tier': 'Micro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'ntkling',          'gender': 'ญ', 'budget': 18000},
    'jamjiramaoon':     {'followers': 585200,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Fiber',    'displayName': 'jamjiramaoon',     'gender': 'ญ', 'budget': 10000},
    'bbew_ddear':       {'followers': 630800,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'bbew_ddear',       'gender': 'ญ', 'budget': 10000},
    'bee112711':        {'followers': 458700,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'bee112711',        'gender': 'ช', 'budget': 10000},
    'bass__inmeesub':   {'followers': 506700,  'tier': 'Macro', 'category': 'ทำงานกลางแจ้ง', 'product': 'Collagen', 'displayName': 'บอสเบลไนติงเจล',  'gender': 'ช', 'budget': 26000},
    'milin_wongsa':     {'followers': 160600,  'tier': 'Macro', 'category': 'ทำงานกลางแจ้ง', 'product': 'Collagen', 'displayName': 'เจ้าพ่อพันล้าน',  'gender': 'ช', 'budget': 28000},
    'on_supaporn':      {'followers': 327700,  'tier': 'Macro', 'category': 'หนุ่มสาวโรงงาน', 'product': 'Fiber',    'displayName': 'on_supaporn',      'gender': 'ญ', 'budget': 10000},
    'f52hz_':           {'followers': 437800,  'tier': 'Macro', 'category': 'ทำงานกลางแจ้ง', 'product': 'Collagen', 'displayName': 'f52hz_',           'gender': 'ญ', 'budget': 10000},
    'somjeedna':        {'followers': 258600,  'tier': 'Macro', 'category': 'หนุ่มสาวโรงงาน', 'product': 'Collagen', 'displayName': 'Soomjeedna',       'gender': 'ญ', 'budget': 10000},
    'phanwasa.4':       {'followers': 96200,   'tier': 'Micro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'phanwasa.4',       'gender': 'ญ', 'budget': 10000},
}

# === KOL LINKS ===
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
}

# === KOLs ที่ยังไม่โพสต์ ===
NOT_POSTED_KOLS = {
    'nisakorn_pui',
}


def build_kol_data_js(scrape_data):
    """Build the KOL_DATA JavaScript array from scrape results + metadata."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%d %b %Y %H:%M')

    lines = [f"let KOL_DATA = [  // auto-updated {timestamp}"]

    for username, meta in KOL_METADATA.items():
        scraped = scrape_data.get(username, {})
        is_posted = username not in NOT_POSTED_KOLS and username in KOL_LINKS

        followers = scraped.get('followers', 0) or meta['followers']
        views = scraped.get('views', 0)
        likes = scraped.get('likes', 0)
        shares = scraped.get('shares', 0)
        comments = scraped.get('comments', 0)
        saves = scraped.get('saves', 0)
        posts = 1 if is_posted else 0
        link = KOL_LINKS.get(username, '')

        line = (
            f"  {{username:'{username}',"
            f"displayName:'{meta['displayName']}',"
            f"tier:'{meta['tier']}',"
            f"platform:'TikTok',"
            f"category:'{meta['category']}',"
            f"product:'{meta['product']}',"
            f"gender:'{meta['gender']}',"
            f"followers:{followers},"
            f"views:{views},"
            f"likes:{likes},"
            f"shares:{shares},"
            f"comments:{comments},"
            f"saves:{saves},"
            f"posts:{posts},"
            f"kpi_views:0,"
            f"posted:{'true' if is_posted else 'false'},"
            f"link:'{link}',"
            f"budget:{meta['budget']}}},"
        )
        lines.append(line)

    lines.append("];")
    return "\n".join(lines)


def update_html(html_path, scrape_data, preserve_actual_use=True):
    """Replace KOL_DATA in the HTML file with updated data."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Preserve CAMPAIGN_ACTUAL_USE_DEFAULT
    actual_use_match = re.search(r'CAMPAIGN_ACTUAL_USE_DEFAULT\s*=\s*([\d.]+)', html)
    actual_use_val = actual_use_match.group(1) if actual_use_match else '0'

    # Replace KOL_DATA array
    new_kol_data = build_kol_data_js(scrape_data)
    pattern = r'let KOL_DATA\s*=\s*\[.*?\];'
    html = re.sub(pattern, new_kol_data, html, flags=re.DOTALL)

    # Restore CAMPAIGN_ACTUAL_USE_DEFAULT if needed
    if preserve_actual_use:
        html = re.sub(
            r'CAMPAIGN_ACTUAL_USE_DEFAULT\s*=\s*[\d.]+',
            f'CAMPAIGN_ACTUAL_USE_DEFAULT = {actual_use_val}',
            html
        )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Updated {html_path}")


def main():
    scrape_file = sys.argv[1] if len(sys.argv) > 1 else 'scrape_results.json'
    html_file = sys.argv[2] if len(sys.argv) > 2 else 'index.html'

    if os.path.exists(scrape_file):
        with open(scrape_file, 'r') as f:
            scrape_data = json.load(f)
        print(f"📂 Loaded {len(scrape_data)} KOLs from {scrape_file}")
    else:
        print(f"⚠️ No scrape file found at {scrape_file}, using empty data")
        scrape_data = {}

    update_html(html_file, scrape_data)


if __name__ == '__main__':
    main()
