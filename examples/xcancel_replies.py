"""Get full X/Twitter reply tree via xcancel.com mirror.

x.com unauthenticated only renders the root tweet body, NOT the reply tree.
The xcancel mirror exposes both. xcancel is Cloudflare-protected, so we
go through Patchright stealth to bypass the challenge.

Verified working May 2026 — pulled tweet + 11 replies in 5 languages
(EN, JP, CN, VI, IT) from a single fetch.

Usage:
  python3 examples/xcancel_replies.py <handle> <tweet_id>
  python3 examples/xcancel_replies.py <full_x_com_url>

Example:
  python3 examples/xcancel_replies.py seelffff 2055155782367187375
"""
import re
import sys

from scrapling.fetchers import StealthyFetcher


def parse_args() -> str:
    """Returns xcancel URL."""
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    if len(args) == 1:
        url = args[0]
        m = re.match(r"https?://(?:x|twitter)\.com/([^/]+)/status/(\d+)", url)
        if not m:
            print(f"Couldn't parse URL: {url}")
            sys.exit(1)
        handle, tweet_id = m.group(1), m.group(2)
    elif len(args) == 2:
        handle, tweet_id = args[0].lstrip("@"), args[1]
    else:
        print(__doc__)
        sys.exit(1)

    return f"https://xcancel.com/{handle}/status/{tweet_id}"


def main():
    url = parse_args()
    print(f"→ Fetching {url}\n")

    page = StealthyFetcher.fetch(
        url=url,
        headless=True,
        network_idle=True,
        solve_cloudflare=True,  # xcancel is CF-protected
        wait=5000,
    )

    print(f"Status: {page.status}\n")

    if page.status != 200:
        print("xcancel returned non-200 — try a different mirror:")
        print("  - nitter.net")
        print("  - nitter.privacydev.net")
        print("  - nitter.poast.org")
        print("Live instances: https://github.com/zedeus/nitter/wiki/Instances")
        sys.exit(1)

    text = page.get_all_text()
    print("─" * 60)
    print(text[:5000])
    print("─" * 60)

    reply_count = text.count("Replying to ")
    print(f"\nDetected {reply_count} reply blocks in DOM.")


if __name__ == "__main__":
    main()
