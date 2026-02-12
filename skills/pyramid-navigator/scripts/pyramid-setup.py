#!/usr/bin/env python3
"""pyramid-setup.py - Install and initialize pyramid-cli (cross-platform)

Usage:
  python pyramid-setup.py              # Check deps + init only
  python pyramid-setup.py --analyze    # Check deps + init + analyze current dir
  python pyramid-setup.py --analyze PATH  # Analyze specific path

Requirements: Python 3.8+, pip available in PATH
"""

import sys
import subprocess
import shutil
from pathlib import Path


REQUIRED_PACKAGES = [
    "click",
    "anthropic",
]

OPTIONAL_PACKAGES = {
    "tree_sitter_languages": "tree-sitter-languages",
}

SCRIPT_NAME = "pyramid_cli.py"


def find_cli_script() -> Path:
    """Locate pyramid_cli.py relative to this script."""
    here = Path(__file__).parent
    candidate = here / SCRIPT_NAME
    if candidate.exists():
        return candidate
    raise SystemExit(
        f"Error: {SCRIPT_NAME} not found in {here}\n"
        "Ensure pyramid_cli.py is in the same directory as this script."
    )


def check_package(import_name: str) -> bool:
    """Return True if a package is importable."""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_package(pip_name: str) -> bool:
    """Install a package via pip. Returns True on success."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", pip_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  Warning: pip install {pip_name} failed:\n  {result.stderr.strip()}")
        return False
    return True


def ensure_dependencies() -> None:
    """Install missing required packages."""
    missing = [pkg for pkg in REQUIRED_PACKAGES if not check_package(pkg)]

    if missing:
        print(f"Installing required packages: {', '.join(missing)}")
        for pkg in missing:
            print(f"  Installing {pkg}...", end=" ", flush=True)
            if install_package(pkg):
                print("OK")
            else:
                raise SystemExit(f"Failed to install {pkg}. Install manually: pip install {pkg}")
    else:
        print("Required packages: OK")

    # Optional packages (non-fatal)
    for import_name, pip_name in OPTIONAL_PACKAGES.items():
        if not check_package(import_name):
            print(f"Optional: {pip_name} not installed (enables multi-language parsing)")
            print(f"  To install: pip install {pip_name}")


def is_pyramid_initialized(directory: Path) -> bool:
    """Return True if .pyramid/ exists in directory."""
    return (directory / ".pyramid").exists()


def run_cli(cli_script: Path, args: list[str]) -> int:
    """Run pyramid_cli.py with given arguments."""
    result = subprocess.run(
        [sys.executable, str(cli_script)] + args,
        cwd=Path.cwd(),
    )
    return result.returncode


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Set up pyramid-cli for codebase navigation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pyramid-setup.py                 # init only
  python pyramid-setup.py --analyze       # init + analyze current dir
  python pyramid-setup.py --analyze src/  # init + analyze src/
        """,
    )
    parser.add_argument(
        "--analyze",
        nargs="?",
        const=".",
        metavar="PATH",
        help="Run pyramid analyze after init (default: current directory)",
    )
    parser.add_argument(
        "--api",
        choices=["anthropic", "openai"],
        default="anthropic",
        help="LLM provider (default: anthropic)",
    )
    args = parser.parse_args()

    cli_script = find_cli_script()
    cwd = Path.cwd()

    print("=== Pyramid CLI Setup ===\n")

    # Step 1: Dependencies
    print("Checking dependencies...")
    ensure_dependencies()
    print()

    # Step 2: Initialize
    if is_pyramid_initialized(cwd):
        print(f"Already initialized in {cwd} (.pyramid/ exists)")
    else:
        print(f"Initializing pyramid in {cwd}...")
        code = run_cli(cli_script, ["init", "--api", args.api])
        if code != 0:
            raise SystemExit("pyramid init failed.")

    print()

    # Step 3: Analyze (optional)
    if args.analyze is not None:
        analyze_path = Path(args.analyze).resolve()
        if not analyze_path.exists():
            raise SystemExit(f"Error: path does not exist: {analyze_path}")

        print(f"Analyzing {analyze_path}...")
        code = run_cli(cli_script, ["analyze", str(analyze_path)])
        if code != 0:
            raise SystemExit("pyramid analyze failed.")
    else:
        print("To index this codebase, run:")
        print(f"  python {cli_script.name} analyze .")
        print()
        print("Then navigate with:")
        print(f"  python {cli_script.name} list --level 4")
        print(f"  python {cli_script.name} query 'TOPIC' --level 8")

    print("\nDone.")


if __name__ == "__main__":
    main()
