"""Cloudflare Turnstile bypass via Patchright stealth.

Verified working May 2026 against:
- nowsecure.nl  (Cloudflare anti-bot test endpoint — only serves content
                 to humans / convincing bots)
- xcancel.com   (Twitter mirror, CF-protected)

Usage:
  python3 examples/cloudflare_bypass.py <url>

Example:
  python3 examples/cloudflare_bypass.py https://nowsecure.nl
"""
import sys

from scrapling.fetchers import StealthyFetcher


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    print(f"→ Bypassing Cloudflare on {url}\n")

    page = StealthyFetcher.fetch(
        url=url,
        network_idle=True,
        solve_cloudflare=True,  # auto-handle Turnstile JS challenge
        wait=8000,              # CF challenges take a few seconds to clear
        extraction_type="markdown",
    )

    print(f"Status: {page.status}")
    print()

    # Common challenge indicators — should NOT appear in successful response
    challenge_indicators = [
        "Just a moment",
        "Checking your browser",
        "verifying your request",
        "challenge-platform",
    ]
    if any(ind in page.markdown for ind in challenge_indicators):
        print("⚠️  Looks like the challenge wasn't solved — extracted DOM still shows challenge text.")
        print("Try: increase wait to 10000-15000, or check that solve_cloudflare=True is honored.")
    else:
        print("✅ No challenge indicators in DOM — bypass succeeded.")

    print()
    print("─" * 60)
    print(page.markdown[:3000])
    print("─" * 60)


if __name__ == "__main__":
    main()
