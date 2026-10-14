import re
import sys
from pathlib import Path
from playwright.sync_api import Page, expect, sync_playwright
from utils import scroll_page_visibly
# Ensure services directory is in sys.path
SERVICES_DIR = Path(__file__).resolve().parent
if str(SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICES_DIR))

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
    scroll_page_visibly(page, role="admin")


# def scroll_page_visibly(page):
    """Scroll slowly from top to bottom, then back to top."""

    print("Starting visible scroll automation...")

    # Start at the top
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    # Scroll down gradually
    while True:
        previous_position = page.evaluate("window.scrollY")
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(500)

        current_position = page.evaluate("window.scrollY")
        scroll_height = page.evaluate(
            "() => document.documentElement.scrollHeight"
        )
        viewport_height = page.evaluate(
            "() => window.innerHeight"
        )

        print(f"Scrolling down: {current_position}px")

        # Stop when the bottom is reached
        if current_position + viewport_height >= scroll_height - 5:
            break

        # Prevent an infinite loop if the page cannot scroll
        if current_position == previous_position:
            break

    print("Reached the bottom. Scrolling back to the top...")

    # Scroll up gradually
    while True:
        previous_position = page.evaluate("window.scrollY")
        page.mouse.wheel(0, -300)
        page.wait_for_timeout(500)

        current_position = page.evaluate("window.scrollY")
        print(f"Scrolling up: {current_position}px")

        if current_position <= 0 or current_position == previous_position:
            break

    print("Scrolling automation completed.")


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
