"""3-tier health canary — verifies the stack is operational.

Public:
    verify_stack(verbose=False) -> bool   # True if healthy

CLI:
    unblock-web verify [--verbose]
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Tuple


def _get_playwright_cache_dir() -> Path:
    """Return the Playwright browser cache dir for current OS."""
    import os as _os
    import platform as _plat
    env_path = _os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if env_path:
        return Path(env_path)
    system = _plat.system().lower()
    home = Path.home()
    if system == "darwin":
        return home / "Library" / "Caches" / "ms-playwright"
    if system == "windows":
        return home / "AppData" / "Local" / "ms-playwright"
    return home / ".cache" / "ms-playwright"


def _check_scrapling() -> Tuple[bool, str]:
    """Tier 1: Patchright + Scrapling importable + Chromium present."""
    cache = _get_playwright_cache_dir()
    chromium = list(cache.glob("chromium-*")) + list(cache.glob("chromium_headless_shell-*"))
    if not chromium:
        return False, f"Chromium not installed under {cache} — run `unblock-web heal`"
    try:
        import patchright  # noqa: F401
        import scrapling   # noqa: F401
    except ImportError as e:
        return False, f"missing dep: {e} — run: pip install unblock-web[stealth]"
    return True, f"patchright + scrapling importable, chromium at {cache}"


def _check_tinyfish() -> Tuple[bool, str]:
    """Tier 2: TinyFish API alive + key valid."""
    from unblock_web.fetcher import _get_tinyfish_key

    api_key = _get_tinyfish_key()
    if not api_key:
        return False, "TINYFISH_API_KEY not set (env var or .env). Free key: https://tinyfish.ai"
    req = urllib.request.Request(
        "https://api.search.tinyfish.ai/?query=hello",
        headers={"X-API-Key": api_key},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        if "results" in data:
            return True, f"search API live ({len(data['results'])} results for 'hello')"
        return False, f"unexpected response shape: {list(data.keys())[:5]}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode()[:120]}"
    except Exception as e:
        return False, f"exception: {e}"


def _check_aggregator() -> Tuple[bool, str]:
    """Tier 3: xcancel.com reachable (CF challenge response is OK — host is up)."""
    try:
        req = urllib.request.Request("https://xcancel.com/", method="HEAD")
        urllib.request.urlopen(req, timeout=10)
        return True, "xcancel.com reachable"
    except urllib.error.HTTPError as e:
        if e.code in (403, 503) or 500 <= e.code < 600:
            return True, f"xcancel.com up (HTTP {e.code} — CF anti-bot expected, Tier 1 bypasses it)"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, f"unreachable: {e}"


def verify_stack(verbose: bool = False, skip_tier2: bool = False) -> bool:
    """Run the 3-tier canary.

    Returns True if all required tiers pass. Tier 2 may be skipped via
    skip_tier2=True or env var UNBLOCK_WEB_SKIP_TIER2=1.
    """
    if not skip_tier2:
        skip_tier2 = os.environ.get("UNBLOCK_WEB_SKIP_TIER2") == "1"

    checks = [
        ("Tier 1: Scrapling+Patchright", _check_scrapling),
        ("Tier 2: TinyFish API", _check_tinyfish),
        ("Tier 3: xcancel mirror", _check_aggregator),
    ]
    results = []
    for name, fn in checks:
        ok, msg = fn()
        results.append((name, ok, msg))
        if verbose:
            mark = "OK " if ok else ("SKIP" if (name.startswith("Tier 2") and skip_tier2) else "FAIL")
            print(f"[{mark}] {name}: {msg}")

    failed = [
        (name, ok, msg) for name, ok, msg in results
        if not ok and not (name.startswith("Tier 2") and skip_tier2)
    ]
    if failed:
        print("WEB SCRAPING STACK REGRESSION:", file=sys.stderr)
        for name, _, msg in failed:
            print(f"  - {name}: {msg}", file=sys.stderr)
        print("Fix: run `unblock-web heal` or see https://github.com/kevinnft/unblock-web", file=sys.stderr)
        return False
    if verbose:
        print("\nAll tiers healthy.")
    return True
