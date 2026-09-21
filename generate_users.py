"""
Generate 10 Million Users and save to CSV
Fields: Username, Email, Password, Confirm Password
"""

import csv
import random
import string
import hashlib
import os
import time

# ── Configuration ─────────────────────────────────────────────
TOTAL_USERS   = 10_000_000
OUTPUT_FILE   = "users_10M.csv"
BATCH_SIZE    = 100_000          # write in batches to keep memory low
LOG_INTERVAL  = 500_000          # print progress every N users
# ──────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "james","john","robert","michael","william","david","richard","joseph",
    "thomas","charles","emma","olivia","ava","isabella","sophia","mia",
    "amelia","harper","evelyn","abigail","liam","noah","oliver","elijah",
    "lucas","mason","logan","ethan","aiden","caden","luna","aria","chloe",
    "penelope","layla","riley","zoey","nora","lily","eleanor","daniel",
    "henry","alexander","jackson","sebastian","aiden","mateo","jack","owen",
    "samuel","grace","victoria","aurora","savannah","audrey","bella","claire",
    "skylar","lucy","paisley","anna","caroline","genesis","aaliyah","kennedy"
]

LAST_NAMES = [
    "smith","johnson","williams","brown","jones","garcia","miller","davis",
    "rodriguez","martinez","hernandez","lopez","gonzalez","wilson","anderson",
    "thomas","taylor","moore","jackson","martin","lee","perez","thompson",
    "white","harris","sanchez","clark","ramirez","lewis","robinson","walker",
    "young","allen","king","wright","scott","torres","nguyen","hill","flores",
    "green","adams","nelson","baker","hall","rivera","campbell","mitchell",
    "carter","roberts","phillips","turner","parker","evans","edwards","collins"
]

DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "protonmail.com", "mail.com", "live.com", "msn.com", "aol.com",
    "zoho.com", "yandex.com", "gmx.com", "fastmail.com", "tutanota.com"
]

SPECIAL_CHARS = "!@#$%^&*"


def random_string(length: int, chars: str = string.ascii_lowercase + string.digits) -> str:
    return "".join(random.choices(chars, k=length))


def make_password(length: int = 12) -> str:
    """
    Generates a strong password with upper, lower, digit, and special char,
    then returns its SHA-256 hash (hex) as stored value.
    """
    upper   = random.choices(string.ascii_uppercase, k=2)
    lower   = random.choices(string.ascii_lowercase, k=4)
    digits  = random.choices(string.digits, k=3)
    special = random.choices(SPECIAL_CHARS, k=2)
    extra   = random.choices(string.ascii_letters + string.digits, k=length - 11)
    chars   = upper + lower + digits + special + extra
    random.shuffle(chars)
    plain   = "".join(chars)
    hashed  = hashlib.sha256(plain.encode()).hexdigest()
    return hashed


def generate_user(uid: int) -> list:
    first  = random.choice(FIRST_NAMES)
    last   = random.choice(LAST_NAMES)
    suffix = random.randint(1, 99999)
    sep    = random.choice(["", "_", "."])

    username = f"{first}{sep}{last}{suffix}"
    email    = f"{first}{sep}{last}{suffix}@{random.choice(DOMAINS)}"
    password = make_password(random.randint(12, 20))

    # confirm_password matches password (as would be validated server-side)
    return [username, email, password, password]


def main():
    print(f"Generating {TOTAL_USERS:,} users  →  {OUTPUT_FILE}")
    print(f"Batch size : {BATCH_SIZE:,}")
    print("-" * 50)

    start = time.time()
    count = 0

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Username", "Email", "Password", "Confirm Password"])

        while count < TOTAL_USERS:
            batch_end = min(count + BATCH_SIZE, TOTAL_USERS)
            batch = [generate_user(i) for i in range(count, batch_end)]
            writer.writerows(batch)
            count = batch_end

            if count % LOG_INTERVAL == 0 or count == TOTAL_USERS:
                elapsed  = time.time() - start
                speed    = count / elapsed if elapsed > 0 else 0
                pct      = count / TOTAL_USERS * 100
                size_mb  = os.path.getsize(OUTPUT_FILE) / 1_048_576
                print(
                    f"  {count:>12,} / {TOTAL_USERS:,}  "
                    f"({pct:5.1f}%)  "
                    f"{speed:>10,.0f} rows/s  "
                    f"file: {size_mb:,.1f} MB"
                )

    total_time = time.time() - start
    final_size = os.path.getsize(OUTPUT_FILE) / 1_048_576
    print("-" * 50)
    print(f"Done!  {TOTAL_USERS:,} users written in {total_time:.1f}s")
    print(f"Output file : {OUTPUT_FILE}  ({final_size:,.1f} MB)")


if __name__ == "__main__":
    main()
