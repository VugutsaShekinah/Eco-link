"""
capture_screenshots.py — capture real screenshots of every ECO-LINK page.

These fill the report's Figure 8-21 UI placeholders. Requires Playwright + a
running dev server.

Usage (two terminals):
    1) ./venv/Scripts/python.exe manage.py runserver 127.0.0.1:8020
    2) ./venv/Scripts/python.exe docs/screenshots/capture_screenshots.py

Or let this script start its own server (default). Output: docs/screenshots/*.png
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8020"
OUT = Path(__file__).resolve().parent
ADMIN_EMAIL = "admin@ecolink.co.ke"
ADMIN_PASSWORD = "Admin@12345"


def shot(page, name):
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    print(f"  captured {name}.png")


def login(page, email, password):
    page.goto(f"{BASE}/login/")
    page.fill("input[name=username]", email)
    page.fill("input[name=password]", password)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # --- Public pages ---
        page.goto(f"{BASE}/")
        shot(page, "01_landing")
        page.goto(f"{BASE}/register/")
        shot(page, "02_register_role_tabs")
        page.goto(f"{BASE}/login/")
        shot(page, "03_login")

        # --- Logged-in (admin sees everything) ---
        login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
        page.goto(f"{BASE}/dashboard/");        shot(page, "04_dashboard")
        page.goto(f"{BASE}/dropoffs/log/");     shot(page, "05_log_dropoff")
        page.goto(f"{BASE}/dropoffs/mine/");    shot(page, "06_my_dropoffs")
        page.goto(f"{BASE}/rewards/");          shot(page, "07_rewards")
        page.goto(f"{BASE}/leaderboard/");      shot(page, "08_leaderboard")
        page.goto(f"{BASE}/manage/");           shot(page, "09_admin_dashboard")
        page.goto(f"{BASE}/manage/users/");     shot(page, "10_manage_users")
        page.goto(f"{BASE}/manage/collections/new/"); shot(page, "11_record_sale")

        browser.close()
    print("Done. Screenshots in docs/screenshots/")


if __name__ == "__main__":
    run()
