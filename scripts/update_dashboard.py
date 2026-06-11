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
    'nisakorn_pui': 'https://www.tiktok.com/@nisakorn_pui/video/7630386912565480711',
}

# === KOLs ที่ยังไม่โพสต์ ===
NOT_POSTED_KOLS = set()  # ทุกคนโพสต์แล้ว

# === LOT 2 DATA ===
KOL_METADATA_LOT2 = {
    'kunofficial29':  {'followers': 245600,  'tier': 'Macro', 'category': 'หนุ่มสาวโรงงาน', 'product': 'Fiber',    'displayName': 'kunofficial29',  'gender': 'ช', 'budget': 15000},
    'aeaeyberry':     {'followers': 179100,  'tier': 'Macro', 'category': 'หนุ่มสาวโรงงาน', 'product': 'Fiber',    'displayName': 'aeaeyberry',     'gender': 'ญ', 'budget': 15000},
    'fymme_':         {'followers': 215400,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'fymme_',         'gender': 'ญ', 'budget': 10000},
    'bonuss_19':      {'followers': 1100000, 'tier': 'Mega',  'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'bonuss_19',      'gender': 'ญ', 'budget': 25000},
    'marumari141':    {'followers': 466300,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'marumari141',    'gender': 'ญ', 'budget': 20000},
    'yanisskkk':      {'followers': 75600,   'tier': 'Micro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'yanisskkk',      'gender': 'ญ', 'budget': 10000},
    'chanyanuch.hh':  {'followers': 287800,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'chanyanuch.hh',  'gender': 'ญ', 'budget': 10000},
    'natkritta_taew': {'followers': 534000,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'natkritta_taew', 'gender': 'ญ', 'budget': 13000},
    'pukjira45':      {'followers': 436700,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'pukjira45',      'gender': 'ญ', 'budget': 13000},
    'benz_benzzzz12': {'followers': 72000,   'tier': 'Micro', 'category': 'หนุ่มสาวโรงงาน', 'product': 'Fiber',    'displayName': 'benz_benzzzz12', 'gender': 'ช', 'budget': 10000},
    'pang_urw':       {'followers': 281900,  'tier': 'Macro', 'category': 'หนุ่มสาวโรงงาน', 'product': 'Collagen', 'displayName': 'pang_urw',       'gender': 'ญ', 'budget': 10000},
    'watermell':      {'followers': 251500,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'watermell',      'gender': 'ญ', 'budget': 14000},
    'mild.melody08':  {'followers': 1100000, 'tier': 'Mega',  'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'mild.melody08',  'gender': 'ญ', 'budget': 16000},
    'yoke1645':       {'followers': 326900,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Fiber',    'displayName': 'yoke1645',       'gender': 'ญ', 'budget': 10000},
    'zaiisivaporn':   {'followers': 933200,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'zaiisivaporn',   'gender': 'ญ', 'budget': 16000},
    'airfrostt_':     {'followers': 358500,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'airfrostt_',     'gender': 'ญ', 'budget': 10000},
    '_filmmwr':       {'followers': 128900,  'tier': 'Macro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': '_filmmwr',       'gender': 'ญ', 'budget': 10000},
    'kanyarat0640':   {'followers': 1100000, 'tier': 'Mega',  'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'kanyarat0640',   'gender': 'ญ', 'budget': 9000},
    'momelontt':      {'followers': 94100,   'tier': 'Micro', 'category': 'Heath & Beauty', 'product': 'Collagen', 'displayName': 'momelontt',      'gender': 'ญ', 'budget': 4500},
    'kuanpuantiew':   {'followers': 1200000, 'tier': 'Mega',  'category': 'ทำงานกลางแจ้ง', 'product': 'Collagen', 'displayName': 'kuanpuantiew',   'gender': 'ช', 'budget': 20000},
}

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
    'pang_urw': 'https://vt.tiktok.com/ZSQkQr1g5/',
}

NOT_POSTED_KOLS_LOT2 = set()  # ทุกคนโพสต์แล้ว


def build_kol_data_js(scrape_data, lot=1):
    """Build the KOL_DATA JavaScript array from scrape results + metadata."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%d %b %Y %H:%M')

    if lot == 1:
        metadata = KOL_METADATA
        links = KOL_LINKS
        not_posted = NOT_POSTED_KOLS
        var_name = 'KOL_DATA'
    else:
        metadata = KOL_METADATA_LOT2
        links = KOL_LINKS_LOT2
        not_posted = NOT_POSTED_KOLS_LOT2
        var_name = 'KOL_DATA_LOT2'

    lines = [f"let {var_name} = [  // auto-updated {timestamp}"]

    for username, meta in metadata.items():
        scraped = scrape_data.get(username, {})
        is_posted = username not in not_posted and username in links

        followers = scraped.get('followers', 0) or meta['followers']
        views = scraped.get('views', 0)
        likes = scraped.get('likes', 0)
        shares = scraped.get('shares', 0)
        comments = scraped.get('comments', 0)
        saves = scraped.get('saves', 0)
        posts = 1 if is_posted else 0
        link = links.get(username, '')

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


def build_kol_data_lot2_js(scrape_data):
    """Build the KOL_DATA_LOT2 JavaScript array."""
    return build_kol_data_js(scrape_data, lot=2)


def update_html(html_path, scrape_data, preserve_actual_use=True):
    """Replace KOL_DATA and KOL_DATA_LOT2 in the HTML file with updated data."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Preserve CAMPAIGN_ACTUAL_USE_DEFAULT
    actual_use_match = re.search(r'CAMPAIGN_ACTUAL_USE_DEFAULT\s*=\s*([\d.]+)', html)
    actual_use_val = actual_use_match.group(1) if actual_use_match else '0'

    # Replace KOL_DATA array (Lot 1) — use negative lookahead to avoid matching KOL_DATA_LOT2
    new_kol_data = build_kol_data_js(scrape_data, lot=1)
    pattern = r'let KOL_DATA(?!_LOT2)\s*=\s*\[.*?\];'
    html = re.sub(pattern, new_kol_data, html, flags=re.DOTALL)

    # Replace or insert KOL_DATA_LOT2 array (Lot 2)
    new_kol_data_lot2 = build_kol_data_lot2_js(scrape_data)
    pattern_lot2 = r'let KOL_DATA_LOT2\s*=\s*\[.*?\];'
    if re.search(pattern_lot2, html, flags=re.DOTALL):
        html = re.sub(pattern_lot2, new_kol_data_lot2, html, flags=re.DOTALL)
    else:
        # Insert after KOL_DATA's closing ];
        # Find the end of the KOL_DATA array we just inserted
        kol_data_match = re.search(r'(let KOL_DATA\s*=\s*\[.*?\];)', html, flags=re.DOTALL)
        if kol_data_match:
            insert_pos = kol_data_match.end()
            html = html[:insert_pos] + '\n\n' + new_kol_data_lot2 + html[insert_pos:]

    # Restore CAMPAIGN_ACTUAL_USE_DEFAULT if needed
    if preserve_actual_use:
        html = re.sub(
            r'CAMPAIGN_ACTUAL_USE_DEFAULT\s*=\s*[\d.]+',
            f'CAMPAIGN_ACTUAL_USE_DEFAULT = {actual_use_val}',
            html
        )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Updated {html_path} (Lot 1 + Lot 2)")


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
