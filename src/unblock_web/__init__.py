"""unblock-web: Anti-blok web scraping stack.

A 4-tier decision tree for AI agents and scrapers:
- Tier 1: Scrapling + Patchright (Cloudflare bypass, x.com tweets)
- Tier 2: TinyFish (geo-proxy, ISP DNS bypass)
- Tier 3: xcancel/Nitter mirrors (X reply trees)
- Tier 4: Authenticated APIs (xurl + bearer)

CLI:
    unblock-web verify           # 3-tier health canary
    unblock-web heal             # reinstall Chromium with platform override
    unblock-web fetch <url>      # smart fetch using best tier for the URL

Library:
    from unblock_web import fetch, verify_stack
    page = fetch("https://x.com/<user>/status/<id>")
    print(page.text)
"""

__version__ = "0.2.0"

from unblock_web.fetcher import fetch, FetchResult
from unblock_web.verify import verify_stack

__all__ = ["fetch", "FetchResult", "verify_stack", "__version__"]
