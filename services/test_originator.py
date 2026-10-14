import re
import sys
from pathlib import Path
from playwright.sync_api import Page, expect, sync_playwright
from utils import scroll_page_visibly

# Ensure services directory and project root are in sys.path
SERVICES_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICES_DIR.parent
for path in (SERVICES_DIR, PROJECT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from config import TEST_ORIGINATOR_2, APP_URL
# from utils import scroll_page_visibly


def test_originator_login(page: Page):
    """Test Originator login flow using pytest-playwright.
    
    Logs in with credentials from config.py and verifies redirection to the originator area.
    """
    # 1. Navigate to the login page
    login_url = f"{APP_URL.rstrip('/')}/login"
    page.goto(login_url)

    # 2. Wait for the email field to become visible (allowing splash animation to finish)
    email_field = page.locator("#email")
    email_field.wait_for(state="visible", timeout=10000)

    # 3. Fill in   Originator credentials from config.py
    email_field.fill(TEST_ORIGINATOR_2["email"])
    page.locator("#password").fill(TEST_ORIGINATOR_2["password"])

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

    # 6. Verify URL transition to /originator/dashboard (or /originator/home if redirected by the app)
    expect(page).to_have_url(re.compile(r"/originator/(dashboard|home)"), timeout=10000)
   
    scroll_page_visibly(page, role="originator")



if __name__ == "__main__":
    # Support direct execution via: python services/test_originator.py
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        try:
            test_originator_login(page)
            print("\n>>> Originator login test PASSED successfully! <<<\n")
        finally:
            page.wait_for_timeout(5000)
            context.close()
            browser.close()