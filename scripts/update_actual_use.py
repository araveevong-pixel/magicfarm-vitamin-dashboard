#!/usr/bin/env python3
"""
Update Actual Use — Magic Farm Vitamin 2026
Updates CAMPAIGN_ACTUAL_USE_DEFAULT value in index.html.
Usage: python3 update_actual_use.py <amount> [html_path]
"""

import re
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update_actual_use.py <amount> [html_path]")
        print("Example: python3 update_actual_use.py 130000")
        sys.exit(1)

    amount = float(sys.argv[1])
    html_path = sys.argv[2] if len(sys.argv) > 2 else 'index.html'

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    old_match = re.search(r'CAMPAIGN_ACTUAL_USE_DEFAULT\s*=\s*([\d.]+)', html)
    old_val = old_match.group(1) if old_match else '0'

    html = re.sub(
        r'CAMPAIGN_ACTUAL_USE_DEFAULT\s*=\s*[\d.]+',
        f'CAMPAIGN_ACTUAL_USE_DEFAULT = {int(amount)}',
        html
    )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Updated Actual Use: {old_val} → {int(amount)}")


if __name__ == '__main__':
    main()
