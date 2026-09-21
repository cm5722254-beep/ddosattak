"""
Bulk User Auto-Submitter
========================
Reads users from users_10M.csv and POSTs each one to your website's
registration endpoint. Runs with multi-threading for speed.

SETUP:
  pip install requests

USAGE:
  1. Set TARGET_URL  → your website's register API endpoint
  2. Set FIELD_MAP   → match your website's form field names
  3. Run: python submit_users.py
"""

import csv
import time
import threading
import requests
from queue import Queue

# ══════════════════════════════════════════════════════════════
#  ★  CONFIGURE THESE  ★
# ══════════════════════════════════════════════════════════════

TARGET_URL   = "https://piphopmovies.com/wp-login.php?action=register"   # ← your register endpoint
INPUT_FILE   = "usersG_10M.csv"                          # ← generated CSV file
TOTAL_SUBMIT = 10_000_000                               # how many users to submit
THREADS      = 20                                       # concurrent threads (increase for speed)
TIMEOUT      = 10                                       # seconds per request
DELAY        = 0.0                                      # delay between requests per thread (0 = max speed)

# Map CSV columns → your website's form field names
# Left  = CSV column name (do not change)
# Right = your website's input field name (change these to match your form)
FIELD_MAP = {
    "Username":         "username",
    "Email":            "email",
    "Password":         "password",
    "Confirm Password": "confirm_password",
}

# Optional: extra fields your form requires (e.g. CSRF token, agree checkbox)
EXTRA_FIELDS = {
    # "agree_terms": "1",
    # "role": "user",
}

# ══════════════════════════════════════════════════════════════

# ── Counters (thread-safe) ──
lock        = threading.Lock()
success     = 0
failed      = 0
processed   = 0
start_time  = None

LOG_INTERVAL = 10_000   # print progress every N submissions


def submit_user(session: requests.Session, row: dict) -> bool:
    """POST one user to the website. Returns True on success."""
    payload = {FIELD_MAP[k]: v for k, v in row.items() if k in FIELD_MAP}
    payload.update(EXTRA_FIELDS)

    try:
        resp = session.post(TARGET_URL, data=payload, timeout=TIMEOUT)
        # Treat 2xx as success; adjust if your site returns differently
        return resp.status_code in (200, 201, 204)
    except requests.exceptions.RequestException:
        return False


def worker(queue: Queue):
    global success, failed, processed
    session = requests.Session()   # reuse TCP connection per thread

    while True:
        row = queue.get()
        if row is None:   # poison pill → thread exits
            queue.task_done()
            break

        ok = submit_user(session, row)

        with lock:
            if ok:
                success += 1
            else:
                failed += 1
            processed += 1

            if processed % LOG_INTERVAL == 0:
                elapsed = time.time() - start_time
                speed   = processed / elapsed if elapsed > 0 else 0
                pct     = processed / TOTAL_SUBMIT * 100
                print(
                    f"  [{pct:5.1f}%]  "
                    f"processed: {processed:>10,}  "
                    f"✅ ok: {success:>10,}  "
                    f"❌ fail: {failed:>8,}  "
                    f"speed: {speed:>8,.0f}/s"
                )

        queue.task_done()

        if DELAY > 0:
            time.sleep(DELAY)


def main():
    global start_time

    print("=" * 60)
    print("  Bulk User Submitter")
    print("=" * 60)
    print(f"  Target URL : {TARGET_URL}")
    print(f"  Input file : {INPUT_FILE}")
    print(f"  Total      : {TOTAL_SUBMIT:,}")
    print(f"  Threads    : {THREADS}")
    print("=" * 60)

    # Validate URL is configured
    if "yourwebsite.com" in TARGET_URL:
        print("\n⚠️  ERROR: Please set TARGET_URL to your actual website endpoint.")
        print("   Open submit_users.py and change the TARGET_URL variable.\n")
        return

    queue = Queue(maxsize=THREADS * 4)

    # Start worker threads
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(queue,), daemon=True)
        t.start()
        threads.append(t)

    start_time = time.time()
    count = 0

    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if count >= TOTAL_SUBMIT:
                break
            queue.put(row)
            count += 1

    # Send poison pills to stop threads
    for _ in range(THREADS):
        queue.put(None)

    queue.join()

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"  Finished!")
    print(f"  Total submitted : {count:,}")
    print(f"  ✅ Success       : {success:,}")
    print(f"  ❌ Failed        : {failed:,}")
    print(f"  Time elapsed    : {elapsed:.1f}s")
    print(f"  Avg speed       : {count/elapsed:,.0f} users/s")
    print("=" * 60)


if __name__ == "__main__":
    main()
