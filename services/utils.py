
from pathlib import Path


def scroll_page_visibly(page, role, scroll_count=4, scroll_pixels=600):
    """
    Reusable scrolling function for Admin, Originator,
    Investor, and User.

    Saves screenshots in result/<role>/dashboard/
    Replaces existing screenshots on every run.
    for every role use this method scroll_page_visibly(page, role="role name")

    Example: scroll_page_visibly(page, role="admin")
    """
    
    # Validate the role to avoid creating unintended folders
    valid_roles = {"admin", "originator", "investor", "user"}
    role = role.strip().lower()

    if role not in valid_roles:
        raise ValueError(
            f"Invalid role: {role}. Choose from {sorted(valid_roles)}"
        )

    print(f"Starting {role} dashboard scrolling...")

    # Project root: dev_testing/
    project_root = Path(__file__).resolve().parent.parent

    # Example: result/dashboard/admin/
    screenshot_dir = project_root / "result" / role / "dashboard" 
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    # Start at the top
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(4000)

    for step in range(1, scroll_count + 1):
        # Scroll downward
        page.mouse.wheel(0, scroll_pixels)
        page.wait_for_timeout(500)

        # Stable filename: overwrite on the next run
        screenshot_path = (
            screenshot_dir / f"dashboard_scroll_{step}.png"
        )

        page.screenshot(
            path=str(screenshot_path),
            full_page=False
        )

        print(
            f"{role.title()} scroll {step}/{scroll_count}: "
            f"window.scrollY={page.evaluate('window.scrollY')}px"
        )
        print(f"Screenshot saved: {screenshot_path}")

        page.wait_for_timeout(1000)

    print(f"Completed scrolling for {role.title()}.")
