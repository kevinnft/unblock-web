#!/usr/bin/env python3
"""Web scraping stack canary — verifies Tier 1 (Scrapling) and Tier 2 (TinyFish).

Exits 0 = stack healthy, prints a one-line summary.
Exits 1 = at least one tier broken, prints failure details.

Designed for cron / CI / session-start hooks: silent on success-with-no-changes,
alert on regression.

Usage:
  python3 verify-stack.py [--verbose]

Setup TINYFISH_API_KEY (free): https://tinyfish.ai → set as env var or in .env file.
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

VERBOSE = "--verbose" in sys.argv

# ---- Tier 1: Scrapling stealthy_fetch via Patchright ----
def check_scrapling():
    """Sanity check — chromium binary exists + patchright importable."""
    # Common Playwright cache locations
    home_cache = Path.home() / ".cache/ms-playwright"
    chromium_dirs = list(home_cache.glob("chromium-*")) + list(home_cache.glob("chromium_headless_shell-*"))
    if not chromium_dirs:
        return False, "Chromium not installed — run scripts/heal-chromium.sh"
    try:
        import patchright  # noqa
        import scrapling  # noqa
    except ImportError as e:
        return False, f"missing dep: {e} — run: pip install scrapling patchright"
    return True, f"patchright + scrapling importable, chromium at {home_cache}"


# ---- Tier 2: TinyFish API ping ----
def check_tinyfish():
    """Live API check — search endpoint costs nothing and is fastest probe."""
    # Look for key in env first, then standard dotenv locations
    api_key = os.environ.get("TINYFISH_API_KEY")
    if not api_key:
        for env_file in [Path(".env"), Path.home() / ".env", Path.home() / ".hermes/.env"]:
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith("TINYFISH_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
            if api_key:
                break
    if not api_key:
        return False, "TINYFISH_API_KEY not set (env var or .env). Get free key: https://tinyfish.ai"
    req = urllib.request.Request(
        "https://api.search.tinyfish.ai/?query=hello",
        headers={"X-API-Key": api_key},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        if "results" in data:
            return True, f"search API live ({len(data['results'])} results for 'hello')"
        return False, f"unexpected response shape: {list(data.keys())[:5]}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode()[:120]}"
    except Exception as e:
        return False, f"exception: {e}"


# ---- Tier 3: aggregator mirror reachable (DNS only, doesn't validate content) ----
def check_aggregator():
    """Just verify xcancel.com resolves + responds (Cloudflare 503 is OK,
    means the host is up; we'd use Tier 1 to actually fetch content)."""
    try:
        req = urllib.request.Request("https://xcancel.com/", method="HEAD")
        urllib.request.urlopen(req, timeout=10)
        return True, "xcancel.com reachable"
    except urllib.error.HTTPError as e:
        # 4xx/5xx with body == Cloudflare challenge response, host is up
        # (Tier 1 stealthy_fetch is what actually gets through; this is a liveness check)
        if e.code in (403, 503) or 500 <= e.code < 600:
            return True, f"xcancel.com up (HTTP {e.code} — CF anti-bot expected, Tier 1 bypasses it)"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, f"unreachable: {e}"


def main():
    # Tier 2 is optional in CI / fresh installs (TinyFish key takes
    # 30 seconds to register, and forks won't have it). Allow soft-fail
    # via env var so CI on PRs from forks doesn't break.
    skip_tier2 = os.environ.get("UNBLOCK_WEB_SKIP_TIER2") == "1"

    checks = [
        ("Tier 1: Scrapling+Patchright", check_scrapling),
        ("Tier 2: TinyFish API", check_tinyfish),
        ("Tier 3: xcancel mirror", check_aggregator),
    ]
    results = []
    for name, fn in checks:
        ok, msg = fn()
        results.append((name, ok, msg))
        if VERBOSE:
            mark = "OK " if ok else ("SKIP" if (name.startswith("Tier 2") and skip_tier2) else "FAIL")
            print(f"[{mark}] {name}: {msg}")

    # Tier 2 failures are downgraded to warnings when skip flag is set
    failed = []
    for name, ok, msg in results:
        if ok:
            continue
        if name.startswith("Tier 2") and skip_tier2:
            continue  # downgraded to warning above, don't fail the run
        failed.append((name, ok, msg))
    if failed:
        # Cron-friendly: only emit on regression
        print("WEB SCRAPING STACK REGRESSION:")
        for name, _, msg in failed:
            print(f"  - {name}: {msg}")
        print("Fix: see scripts/heal-chromium.sh and README.md")
        sys.exit(1)
    if VERBOSE:
        print("\nAll tiers healthy.")
    # silent on full pass for cron use
    sys.exit(0)


if __name__ == "__main__":
    main()
