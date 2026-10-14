import re
import sys
from pathlib import Path
from playwright.sync_api import Page, expect, sync_playwright

# Ensure services directory and project root are in sys.path
SERVICES_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICES_DIR.parent
for path in (SERVICES_DIR, PROJECT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from utils import scroll_page_visibly
from config import ADMIN_USER, APP_URL


def test_admin_login(page: Page):
    """Test Admin login flow using pytest-playwright.
    
    Logs in with credentials from config.py and verifies redirection to the admin area.
    """
    # 1. Navigate to the login page
    login_url = f"{APP_URL.rstrip('/')}/login"
    page.goto(login_url)

    # 2. Wait for the email field to become visible (allowing splash animation to finish)
    email_field = page.locator("#email")
    email_field.wait_for(state="visible", timeout=10000)

    # 3. Fill in Admin credentials from config.py
    email_field.fill(ADMIN_USER["email"])
    page.locator("#password").fill(ADMIN_USER["password"])

    # 4. Click the Form Submit button (scoped to avoid navbar collision)
    page.locator("form button[type='submit']").click()

    # 5. Handle 'Active Session Detected' popup if an active session exists
    try:
        popup_btn = page.get_by_role("button", name="Login Here")
        popup_btn.wait_for(state="visible", timeout=3000)
        popup_btn.click()
    except Exception:
        # Proceed if no active session prompt was triggered
        pass

    # 6. Verify URL transition to /admin/dashboard (or /admin/home if redirected by the app)
    expect(page).to_have_url(re.compile(r"/admin/(dashboard|home)"), timeout=10000)
    page.wait_for_timeout(4000)
    page.screenshot(path="result/admin/dashboard/dash_0.png")
    scroll_page_visibly(page, role="admin")


if __name__ == "__main__":
    # Support direct execution via: python services/test_login.py
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        try:
            test_admin_login(page)
            print("\n>>> Admin login test PASSED successfully! <<<\n")
        finally:
            page.wait_for_timeout(5000)
            context.close()
            browser.close()
