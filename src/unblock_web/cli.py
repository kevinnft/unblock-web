"""CLI entrypoint for unblock-web.

Usage:
    unblock-web verify [--verbose]
    unblock-web heal [--platform <override>] [--python <path>]
    unblock-web fetch <url> [--tier T0|T1|T2|T3] [--proxy CC]
                          [--wait MS] [--no-cf-solve] [--html]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from unblock_web import __version__, fetch, verify_stack


def cmd_verify(args: argparse.Namespace) -> int:
    ok = verify_stack(verbose=args.verbose, skip_tier2=args.skip_tier2)
    return 0 if ok else 1


def cmd_heal(args: argparse.Namespace) -> int:
    """Re-install Patchright + Playwright Chromium with platform override."""
    py = args.python or sys.executable
    platform = args.platform or _default_platform_override()

    print(f"Using Python: {py}")
    if platform:
        print(f"Platform override: {platform}\n")
    else:
        print("Platform: auto-detected (no override needed)\n")

    env = os.environ.copy()
    if platform:
        env["PLAYWRIGHT_HOST_PLATFORM_OVERRIDE"] = platform

    for module in ("playwright", "patchright"):
        print(f"Installing Chromium for {module}...")
        try:
            subprocess.run(
                [py, "-m", module, "install", "chromium"],
                env=env, check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"FAIL: {module} install exited {e.returncode}", file=sys.stderr)
            print(
                f"Hint: try a different parent platform via --platform "
                f"(e.g. ubuntu22.04-x64)",
                file=sys.stderr,
            )
            return 1

    cache = Path.home() / ".cache/ms-playwright"
    chromium = list(cache.glob("chromium-*")) + list(cache.glob("chromium_headless_shell-*"))
    if chromium:
        print(f"\nOK: Chromium installed at {cache}")
        for d in chromium[:3]:
            print(f"  - {d.name}")
        return 0
    print(f"\nFAIL: no chromium under {cache}", file=sys.stderr)
    return 1


def _default_platform_override() -> str:
    """Pick a sensible PLAYWRIGHT_HOST_PLATFORM_OVERRIDE value per host OS.

    Returns empty string when no override is needed (most platforms).
    Only Ubuntu 25.10+ / 26.04+ need the override (Playwright's allowlist
    doesn't include them yet as of May 2026).
    """
    import platform

    system = platform.system().lower()
    if system != "linux":
        return ""  # macOS, Windows: native install works

    # Read /etc/os-release to detect Ubuntu version
    try:
        with open("/etc/os-release") as f:
            content = f.read()
        if "Ubuntu" not in content and "ubuntu" not in content:
            return ""  # Non-Ubuntu Linux: try native first
        # Extract VERSION_ID
        for line in content.splitlines():
            if line.startswith("VERSION_ID="):
                version = line.split("=", 1)[1].strip().strip('"')
                # Override needed for Ubuntu 25+ (post-24.04)
                if version >= "25":
                    return "ubuntu24.04-x64"
                return ""  # Ubuntu 24.04 or older — native install works
    except Exception:
        pass
    return ""


def cmd_fetch(args: argparse.Namespace) -> int:
    """Fetch a URL using the right tier (or forced tier)."""
    try:
        result = fetch(
            url=args.url,
            tier=args.tier,
            proxy_country=args.proxy,
            wait=args.wait,
            solve_cloudflare=not args.no_cf_solve,
            timeout=args.timeout,
        )
    except ImportError as e:
        print(f"Missing dependency: {e}", file=sys.stderr)
        print("Run: pip install 'unblock-web[stealth]'", file=sys.stderr)
        return 1

    if result.error:
        print(f"ERROR ({result.tier}): {result.error}", file=sys.stderr)
        return 2

    # Plain output: tier on stderr, content on stdout (pipeable)
    print(f"[{result.tier}] {result.status} — {result.final_url or result.url}", file=sys.stderr)
    if result.title:
        print(f"Title: {result.title}", file=sys.stderr)
    print()  # stderr blank line

    if args.html and result.html:
        sys.stdout.write(result.html)
    else:
        sys.stdout.write(result.text)
    if not (args.html and result.html):
        sys.stdout.write("\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="unblock-web",
        description="Anti-blok web scraping stack (4-tier decision tree)",
    )
    parser.add_argument("--version", action="version", version=f"unblock-web {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # verify
    p_verify = sub.add_parser("verify", help="Run 3-tier health canary")
    p_verify.add_argument("-v", "--verbose", action="store_true", help="Show per-tier output")
    p_verify.add_argument(
        "--skip-tier2", action="store_true",
        help="Soft-fail Tier 2 if TINYFISH_API_KEY not set (CI-friendly)",
    )
    p_verify.set_defaults(func=cmd_verify)

    # heal
    p_heal = sub.add_parser("heal", help="Reinstall Chromium with platform override")
    p_heal.add_argument("--platform", help="Override (default: ubuntu24.04-x64)")
    p_heal.add_argument("--python", help="Python interpreter to install into (default: current)")
    p_heal.set_defaults(func=cmd_heal)

    # fetch
    p_fetch = sub.add_parser("fetch", help="Fetch a URL using the best tier")
    p_fetch.add_argument("url", help="URL to fetch")
    p_fetch.add_argument("--tier", default="auto",
                         choices=["auto", "T0", "T1", "T2", "T3"],
                         help="Force a specific tier (default: auto)")
    p_fetch.add_argument("--proxy", default=None, help="Country code for Tier 2 (e.g. US, JP)")
    p_fetch.add_argument("--wait", type=int, default=5000, help="ms to wait after load (Tier 1)")
    p_fetch.add_argument("--no-cf-solve", action="store_true",
                         help="Skip Cloudflare Turnstile solver (faster if no CF expected)")
    p_fetch.add_argument("--html", action="store_true",
                         help="Output raw HTML instead of extracted text")
    p_fetch.add_argument("--timeout", type=int, default=30, help="Seconds")
    p_fetch.set_defaults(func=cmd_fetch)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
