# Magic Farm Vitamin 2026 — Setup Guide

## 1. สร้าง GitHub Repo + Deploy

รันคำสั่งนี้บนเครื่องของคุณ (Terminal):

```bash
# ไปที่โฟลเดอร์โปรเจกต์
cd ~/Desktop/magicfarm-vitamin-dashboard

# Init git
git init
git branch -m main

# Add all files
git add .
git commit -m "Initial commit: Magic Farm Vitamin 2026 KOL Dashboard"

# สร้าง repo บน GitHub แล้ว push
git remote add origin https://github.com/araveevong-pixel/magicfarm-vitamin-dashboard.git
git push -u origin main
```

## 2. Enable GitHub Pages

1. ไปที่ https://github.com/araveevong-pixel/magicfarm-vitamin-dashboard/settings/pages
2. Source → เลือก **Deploy from a branch**
3. Branch → เลือก **main** → folder **/ (root)**
4. กด **Save**
5. รอ 1-2 นาที → เข้าได้ที่: https://araveevong-pixel.github.io/magicfarm-vitamin-dashboard/

## 3. GitHub Actions — Auto Update

Workflow จะรันอัตโนมัติ **ทุกวัน 09:00 AM เวลาไทย**

### รัน Manual:
1. ไปที่ https://github.com/araveevong-pixel/magicfarm-vitamin-dashboard/actions
2. เลือก **Auto Update Dashboard**
3. กด **Run workflow**
4. ถ้าต้องการอัพเดท Actual Use ใส่ตัวเลขในช่อง

### อัพเดท Actual Use จาก Terminal:
```bash
cd ~/Desktop/magicfarm-vitamin-dashboard
python3 scripts/update_actual_use.py 130000
git add index.html && git commit -m "Update actual use: 130,000" && git push
```

## 4. เพิ่ม KOL ที่โพสต์แล้ว

เมื่อ KOL โพสต์ใหม่ ต้องแก้ 2 ไฟล์:

### 4.1 เพิ่มลิงก์ใน `scripts/tiktok_scraper.py`
```python
KOL_LINKS = {
    'janesaowaluk': 'https://vt.tiktok.com/ZSHjeYw5F/',
    'nisakorn_pui': 'https://vt.tiktok.com/NEW_LINK/',  # ← เพิ่มใหม่
}
```

### 4.2 ย้ายออกจาก NOT_POSTED ใน `scripts/update_dashboard.py`
```python
NOT_POSTED_KOLS = {
    'siriwan040541', 'mildmint.1', ...
    # ลบ 'nisakorn_pui' ออก
}

KOL_LINKS = {
    'janesaowaluk': 'https://vt.tiktok.com/ZSHjeYw5F/',
    'nisakorn_pui': 'https://vt.tiktok.com/NEW_LINK/',  # ← เพิ่มใหม่
}
```

แล้ว commit + push:
```bash
git add . && git commit -m "Add nisakorn_pui post link" && git push
```

## 5. รัน Scraper Manual (บนเครื่อง)

```bash
cd ~/Desktop/magicfarm-vitamin-dashboard

# Scrape
python3 scripts/tiktok_scraper.py scrape_results.json

# Update dashboard
python3 scripts/update_dashboard.py scrape_results.json index.html

# Push
git add . && git commit -m "Manual update $(date +%Y-%m-%d)" && git push
```

## โครงสร้างไฟล์

```
magicfarm-vitamin-dashboard/
├── index.html                          ← Dashboard หลัก (GitHub Pages)
├── scripts/
│   ├── tiktok_scraper.py              ← Scrape TikTok metrics
│   ├── update_dashboard.py            ← Inject data เข้า HTML
│   └── update_actual_use.py           ← อัพเดท Actual Use
├── .github/
│   └── workflows/
│       └── auto-update.yml            ← GitHub Actions (ทุกวัน 9AM)
└── SETUP.md                           ← ไฟล์นี้
```
