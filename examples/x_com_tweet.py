"""x.com tweet body extraction without authentication.

Verified working May 2026 against the unauthenticated x.com tweet endpoint.
The headless browser captures the tweet DOM before the React login modal mounts.

Limitations:
- Gets root tweet only (body, view count, reply count, video thumbnail, quoted tweet meta)
- Does NOT get reply tree (use examples/xcancel_replies.py for that)
- Does NOT get DMs / private accounts (Tier 4 needed)

Usage:
  python3 examples/x_com_tweet.py <tweet_url_or_id>

Example:
  python3 examples/x_com_tweet.py https://x.com/seelffff/status/2055155782367187375
  python3 examples/x_com_tweet.py 2055155782367187375
"""
import re
import sys

from scrapling.fetchers import StealthyFetcher


def normalize(arg: str) -> str:
    """Accept either full URL or just the tweet ID."""
    if arg.startswith("http"):
        return arg
    if re.fullmatch(r"\d{15,25}", arg):
        # Bare ID — assume @user is in URL or use generic /i/web/status path
        return f"https://x.com/i/web/status/{arg}"
    raise ValueError(f"Unrecognized input: {arg}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = normalize(sys.argv[1])
    print(f"→ Fetching {url}\n")

    page = StealthyFetcher.fetch(
        url=url,
        network_idle=True,    # wait for XHRs to settle
        solve_cloudflare=True, # x.com uses CF in some regions
        wait=5000,             # 5s — let React hydrate the tweet
        extraction_type="markdown",
    )

    print(f"Status: {page.status}")
    print(f"Final URL: {page.url}")
    print()
    print("─" * 60)
    print(page.markdown[:4000])
    print("─" * 60)
    if len(page.markdown) > 4000:
        print(f"\n[truncated — full body is {len(page.markdown)} chars]")


if __name__ == "__main__":
    main()
