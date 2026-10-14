from pathlib import Path


def scroll_page_visibly(page, role, scroll_count=None, scroll_pixels=500, max_scrolls=40):
    """
    Reusable dynamic auto-scrolling function for Admin, Originator,
    Investor, and User.

    Automatically detects whether the window or an internal container
    (e.g., overflow-y-auto) scrolls, and scrolls until the end/bottom is reached.
    Saves screenshots in result/<role>/dashboard/
    Replaces existing screenshots on every run.
    """

    # Validate the role to avoid creating unintended folders
    valid_roles = {"admin", "originator", "investor", "user"}
    role = role.strip().lower()

    if role not in valid_roles:
        raise ValueError(
            f"Invalid role: {role}. Choose from {sorted(valid_roles)}"
        )

    print(f"\nStarting {role.title()} dashboard auto-scrolling...")

    # Project root: dev_testing/
    project_root = Path(__file__).resolve().parent.parent

    # Example: result/originator/dashboard/
    screenshot_dir = project_root / "result" / role / "dashboard" 
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    # Clean previous screenshots in this folder to keep only latest run
    for old_file in screenshot_dir.glob("dashboard_scroll_*.png"):
        try:
            old_file.unlink()
        except Exception:
            pass

    # JavaScript helper to reset scroll position to top
    page.evaluate("""() => {
        window.scrollTo(0, 0);
        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
                el.scrollTop = 0;
            }
        });
    }""")
    page.wait_for_timeout(1000)

    # Position mouse in the center of the viewport so wheel events hit the main content
    viewport = page.viewport_size or {"width": 1280, "height": 720}
    page.mouse.move(viewport["width"] / 2, viewport["height"] / 2)

    # JavaScript helper to get current scroll metrics from either container or window
    get_scroll_metrics_js = """() => {
        const windowMax = Math.max(
            0,
            Math.max(document.documentElement.scrollHeight, document.body.scrollHeight) - window.innerHeight
        );

        const scrollable = [];
        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            if ((style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight + 10) {
                scrollable.push(el);
            }
        });

        scrollable.sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight));
        const target = scrollable[0];

        if (target && (target.scrollHeight - target.clientHeight) > windowMax) {
            return {
                target: 'container',
                scrollTop: Math.round(target.scrollTop),
                scrollHeight: target.scrollHeight,
                clientHeight: target.clientHeight,
                maxScroll: Math.max(0, target.scrollHeight - target.clientHeight),
                isBottom: target.scrollTop + target.clientHeight >= target.scrollHeight - 15
            };
        } else {
            const currentY = window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
            const totalHeight = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
            const viewHeight = window.innerHeight;
            return {
                target: 'window',
                scrollTop: Math.round(currentY),
                scrollHeight: totalHeight,
                clientHeight: viewHeight,
                maxScroll: Math.max(0, totalHeight - viewHeight),
                isBottom: currentY + viewHeight >= totalHeight - 15
            };
        }
    }"""

    # Programmatic fallback scroll in case wheel isn't captured by the container
    scroll_by_js = """(pixels) => {
        const windowMax = Math.max(
            0,
            Math.max(document.documentElement.scrollHeight, document.body.scrollHeight) - window.innerHeight
        );
        const scrollable = [];
        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            if ((style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight + 10) {
                scrollable.push(el);
            }
        });
        scrollable.sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight));
        const target = scrollable[0];

        if (target && (target.scrollHeight - target.clientHeight) > windowMax) {
            target.scrollTop += pixels;
        } else {
            window.scrollBy(0, pixels);
        }
    }"""

    step = 0
    effective_max = scroll_count if scroll_count is not None else max_scrolls
    page.wait_for_timeout(4000)
    while step < effective_max:
        step += 1
        prev_info = page.evaluate(get_scroll_metrics_js)

        # Scroll downward
        page.mouse.wheel(0, scroll_pixels)
        

        curr_info = page.evaluate(get_scroll_metrics_js)

        # If wheel didn't advance scrollTop, use JavaScript fallback
        if curr_info["scrollTop"] == prev_info["scrollTop"] and not curr_info["isBottom"]:
            page.evaluate(scroll_by_js, scroll_pixels)
            page.wait_for_timeout(800)
            curr_info = page.evaluate(get_scroll_metrics_js)

        # Save screenshot for current scroll step
        screenshot_path = screenshot_dir / f"dashboard_scroll_{step}.png"
        page.screenshot(
            path=str(screenshot_path),
            full_page=False
        )

        print(
            f"{role.title()} scroll step {step} ({curr_info['target']}): "
            f"position={curr_info['scrollTop']}px / {curr_info['maxScroll']}px"
        )
        print(f"Screenshot saved: {screenshot_path}")

        # Check if bottom of the page is reached
        if curr_info["isBottom"]:
            print(f"Reached the bottom of {role.title()} page ({curr_info['target']}).")
            break

        # Check if page cannot scroll further
        if curr_info["scrollTop"] == prev_info["scrollTop"]:
            print(f"Page reached the end (no further scrolling possible).")
            break

        page.wait_for_timeout(500)

    print(f"Completed auto-scrolling for {role.title()} in {step} step(s).\n")
