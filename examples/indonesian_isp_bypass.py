"""Bypass ISP-level DNS poisoning via TinyFish geo-proxy.

Verified working May 2026 from Indonesian Internet Positif network against:
- web3.okx.com  (crypto exchange — DNS-blocked locally)
- binance.com   (DNS-blocked)

Usage:
  python3 examples/indonesian_isp_bypass.py <url>

Setup:
  export TINYFISH_API_KEY="your_free_key"  # get one at https://tinyfish.ai
"""
import json
import os
import sys
import urllib.request

API_KEY = os.environ.get("TINYFISH_API_KEY")
ENDPOINT = "https://api.fetch.tinyfish.ai"


def fetch(url: str, country_code: str = "US") -> dict:
    if not API_KEY:
        raise RuntimeError(
            "TINYFISH_API_KEY not set. Get a free key at https://tinyfish.ai"
        )
    payload = {
        "urls": [url],
        "format": "markdown",
        "proxy_config": {"country_code": country_code},
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    proxy = sys.argv[2] if len(sys.argv) > 2 else "US"

    print(f"→ Routing {url} via TinyFish proxy: {proxy}\n")

    result = fetch(url, country_code=proxy)
    if not result.get("results"):
        print(f"No results: {result}")
        sys.exit(1)

    page = result["results"][0]
    print(f"Title:      {page.get('title') or '(none)'}")
    print(f"Final URL:  {page.get('final_url')}")
    print(f"Latency:    {page.get('latency_ms', 0):.0f}ms")
    print(f"Language:   {page.get('language') or '(unknown)'}")
    print()
    print("─" * 60)
    print(page.get("text", "")[:3000])
    print("─" * 60)

    if result.get("errors"):
        print(f"\nErrors: {result['errors']}")


if __name__ == "__main__":
    main()
