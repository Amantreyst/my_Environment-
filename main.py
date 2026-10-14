
import subprocess
import sys
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent
TESTS_DIR = PROJECT_ROOT / "tests"


# Available test files
TEST_OPTIONS = {
    "1": ("Admin Login", "test_admin_login.py"),
    "2": ("Originator Login", "test_originator_login.py"),
    "3": ("Investor Login", "test_investor_login.py"),
}


def run_tests(test_files):
    """Execute selected test files using pytest."""

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        *[str(TESTS_DIR / name) for name in test_files],
    ]

    print("\nStarting selected tests...\n")

    result = subprocess.run(command, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        print("\nAll selected tests passed.")
    elif result.returncode == 1:
        print("\nTests failed. Check the pytest report above.")
    else:
        print(
            f"\nPytest exited with code {result.returncode}. "
            "Check the error output above."
        )


def main():
    while True:
        print("\n========== POOLGURU TEST MENU ==========")
        print("1. Admin Login Test")
        print("2. Originator Login Test")
        print("3. Investor Login Test")
        print("4. Run All Login Tests")
        print("5. Exit")
        print("========================================")

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            run_tests([TEST_OPTIONS["1"][1]])

        elif choice == "2":
            run_tests([TEST_OPTIONS["2"][1]])

        elif choice == "3":
            run_tests([TEST_OPTIONS["3"][1]])

        elif choice == "4":
            run_tests(
                [filename for _, filename in TEST_OPTIONS.values()]
            )

        elif choice == "5":
            print("Exiting the test runner.")
            break

        else:
            print("Invalid option. Please select 1-5.")


if __name__ == "__main__":
    main()
