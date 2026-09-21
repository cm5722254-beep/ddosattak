"""
Dry-Run Preview
===============
Shows the first 10 rows that WOULD be submitted to your website.
Run this FIRST to confirm everything looks correct before
running submit_users.py for real.

Usage:
  python preview_submit.py
"""

import csv
import json

INPUT_FILE = "users_10M.csv"
PREVIEW    = 10

FIELD_MAP = {
    "Username":         "username",
    "Email":            "email",
    "Password":         "password",
    "Confirm Password": "confirm_password",
}

EXTRA_FIELDS = {
    # "agree_terms": "1",
}

print("=" * 55)
print("  DRY RUN — first 10 payloads that will be POSTed")
print("=" * 55)

with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= PREVIEW:
            break
        payload = {FIELD_MAP[k]: v for k, v in row.items() if k in FIELD_MAP}
        payload.update(EXTRA_FIELDS)
        print(f"\n  User #{i+1}")
        print(json.dumps(payload, indent=4))

print("\n" + "=" * 55)
print("  Looks correct? Run submit_users.py to submit all 10M")
print("=" * 55)
