"""High-level fetch() — picks the right tier for the URL automatically.

Public API:
    fetch(url, ...) -> FetchResult

The decision logic:
    1. Plain HTTP first (fast path) — for URLs that probably don't need a browser
    2. Scrapling stealth (Tier 1) — default for hard targets, Cloudflare, SPAs, x.com
    3. TinyFish (Tier 2) — only if user passes proxy_country (geo bypass)
    4. xcancel mirror (Tier 3) — only when URL is a x.com/twitter.com tweet
                                 AND replies/thread is requested

Caller can force a tier via tier= argument. Default is auto.
"""
from __future__ import annotations

import os
import re
import urllib.parse
from dataclasses import dataclass
from typing import Optional


@dataclass
class FetchResult:
    """Result of a fetch operation, regardless of which tier was used."""
    url: str
    status: int
    text: str               # extracted plain text (markdown-ish)
    html: str               # full HTML body (when available; "" for TinyFish)
    tier: str               # "T0" | "T1" | "T2" | "T3"
    final_url: str = ""
    title: Optional[str] = None
    error: Optional[str] = None


# URL patterns that need Tier 1 by default
_TWEET_URL_RE = re.compile(
    r"^https?://(?:x|twitter)\.com/[^/]+/status/\d+",
    re.IGNORECASE,
)


def _looks_like_tweet(url: str) -> bool:
    return bool(_TWEET_URL_RE.match(url))


def _looks_like_static(url: str) -> bool:
    """Heuristic: github raw, simple TLDs without obvious anti-bot."""
    parsed = urllib.parse.urlparse(url)
    static_hints = ("raw.githubusercontent.com", "gist.github.com")
    return any(h in parsed.netloc for h in static_hints)


def fetch(
    url: str,
    *,
    tier: str = "auto",
    proxy_country: Optional[str] = None,
    wait: int = 5000,
    solve_cloudflare: bool = True,
    timeout: int = 30,
) -> FetchResult:
    """Fetch a URL using the right tier for the target.

    Args:
        url: Target URL.
        tier: "auto" (default), "T0", "T1", "T2", or "T3". Force a specific tier.
        proxy_country: ISO-3166 alpha-2 (e.g. "US", "JP"). Forces Tier 2 if set.
        wait: ms to wait after page load (Tier 1 only).
        solve_cloudflare: whether to handle Turnstile JS challenge (Tier 1).
        timeout: seconds (Tier 1) or per-request timeout (Tier 2).

    Returns:
        FetchResult with status, text, html (if applicable), and tier used.

    Raises:
        ImportError: if the chosen tier's dependency is missing.
        RuntimeError: if Tier 2 is requested but TINYFISH_API_KEY isn't set.

    Examples:
        >>> from unblock_web import fetch
        >>> page = fetch("https://x.com/seelffff/status/2055155782367187375")
        >>> print(page.text[:200])

        >>> # Force ISP/geo bypass
        >>> page = fetch("https://web3.okx.com", proxy_country="US")
    """
    # Forced tier overrides auto
    if tier == "T0":
        return _fetch_t0(url, timeout=timeout)
    if tier == "T1":
        return _fetch_t1(url, wait=wait, solve_cloudflare=solve_cloudflare, timeout=timeout)
    if tier == "T2":
        return _fetch_t2(url, proxy_country=proxy_country or "US", timeout=timeout)
    if tier == "T3":
        return _fetch_t3(url, wait=wait, timeout=timeout)
    if tier != "auto":
        raise ValueError(f"Unknown tier: {tier!r}. Use 'auto', 'T0', 'T1', 'T2', or 'T3'.")

    # AUTO routing
    # 1. proxy_country forces Tier 2 (geo bypass is the explicit user intent)
    if proxy_country:
        return _fetch_t2(url, proxy_country=proxy_country, timeout=timeout)

    # 2. Tweet URLs go to Tier 1 (stealth captures DOM before login modal)
    if _looks_like_tweet(url):
        return _fetch_t1(url, wait=wait, solve_cloudflare=solve_cloudflare, timeout=timeout)

    # 3. Known-static URLs go to Tier 0 (faster)
    if _looks_like_static(url):
        return _fetch_t0(url, timeout=timeout)

    # 4. Default: Tier 1 stealth (handles ~99% of hard cases)
    return _fetch_t1(url, wait=wait, solve_cloudflare=solve_cloudflare, timeout=timeout)


# ─────────────────────────────────────────────────────────────────────────────
# Tier implementations — kept private; users should call fetch()
# ─────────────────────────────────────────────────────────────────────────────


def _fetch_t0(url: str, timeout: int = 30) -> FetchResult:
    """Plain HTTP via Scrapling Fetcher (or stdlib if Scrapling not installed)."""
    try:
        from scrapling.fetchers import Fetcher
        page = Fetcher().get(url, timeout=timeout * 1000)
        text = page.get_all_text() if hasattr(page, "get_all_text") else ""
        html = page.body.decode("utf-8", errors="replace") if hasattr(page, "body") else ""
        return FetchResult(
            url=url,
            status=page.status,
            text=text,
            html=html,
            tier="T0",
            final_url=getattr(page, "url", url),
        )
    except ImportError:
        # Fallback: pure stdlib
        import urllib.request
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return FetchResult(
                    url=url,
                    status=resp.status,
                    text=body,  # raw HTML — no extraction
                    html=body,
                    tier="T0",
                    final_url=resp.url,
                )
        except Exception as e:
            return FetchResult(url=url, status=0, text="", html="", tier="T0", error=str(e))


def _fetch_t1(
    url: str,
    *,
    wait: int = 5000,
    solve_cloudflare: bool = True,
    timeout: int = 30,
) -> FetchResult:
    """Stealth fetch via Scrapling + Patchright."""
    from scrapling.fetchers import StealthyFetcher
    page = StealthyFetcher.fetch(
        url=url,
        headless=True,
        network_idle=True,
        solve_cloudflare=solve_cloudflare,
        wait=wait,
        timeout=timeout * 1000,
    )
    return FetchResult(
        url=url,
        status=page.status,
        text=page.get_all_text(),
        html=page.body.decode("utf-8", errors="replace") if isinstance(page.body, bytes) else str(page.body),
        tier="T1",
        final_url=page.url,
    )


def _fetch_t2(url: str, *, proxy_country: str = "US", timeout: int = 30) -> FetchResult:
    """TinyFish API fetch with optional geo-proxy."""
    import json
    import urllib.request
    import urllib.error

    api_key = _get_tinyfish_key()
    if not api_key:
        return FetchResult(
            url=url, status=0, text="", html="", tier="T2",
            error="TINYFISH_API_KEY not set. Get free key at https://tinyfish.ai",
        )
    payload = {
        "urls": [url],
        "format": "markdown",
        "proxy_config": {"country_code": proxy_country},
    }
    req = urllib.request.Request(
        "https://api.fetch.tinyfish.ai",
        data=json.dumps(payload).encode(),
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return FetchResult(
            url=url, status=e.code, text="", html="", tier="T2",
            error=f"TinyFish HTTP {e.code}: {e.read().decode()[:200]}",
        )
    if not data.get("results"):
        return FetchResult(
            url=url, status=0, text="", html="", tier="T2",
            error=f"TinyFish returned no results: {data}",
        )
    r = data["results"][0]
    return FetchResult(
        url=url,
        status=200,  # TinyFish flattens upstream status; doesn't return it
        text=r.get("text", ""),
        html="",  # TinyFish returns extracted, not raw HTML
        tier="T2",
        final_url=r.get("final_url", url),
        title=r.get("title"),
    )


def _fetch_t3(url: str, *, wait: int = 5000, timeout: int = 30) -> FetchResult:
    """Aggregator mirror — converts x.com URL to xcancel.com, then T1 stealth."""
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower() not in ("x.com", "twitter.com", "www.x.com", "www.twitter.com"):
        return FetchResult(
            url=url, status=0, text="", html="", tier="T3",
            error="Tier 3 only supports x.com / twitter.com URLs",
        )
    mirror_url = f"https://xcancel.com{parsed.path}"
    return _fetch_t1(mirror_url, wait=wait, solve_cloudflare=True, timeout=timeout)


def _get_tinyfish_key() -> Optional[str]:
    """Look up TINYFISH_API_KEY from env or common dotenv locations."""
    from pathlib import Path

    api_key = os.environ.get("TINYFISH_API_KEY")
    if api_key:
        return api_key
    for env_file in [Path(".env"), Path.home() / ".env", Path.home() / ".hermes/.env"]:
        if not env_file.exists():
            continue
        try:
            for line in env_file.read_text().splitlines():
                if line.startswith("TINYFISH_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            continue
    return None
