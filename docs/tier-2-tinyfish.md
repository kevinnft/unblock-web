# Tier 2: TinyFish — Geo-Proxy & Second Opinion

A free remote browser farm. Renders JS server-side, includes geo-proxy, no rate limit advertised. Use when local Chromium is busy or the local network is what's blocking you.

## When to Use

- ✅ ISP DNS poisoning (🇮🇩 Internet Positif blocks crypto exchanges, Discord, etc.)
- ✅ Geo-locked content (need US/JP/EU IP)
- ✅ Want a second opinion to verify Tier 1 results
- ✅ Local Chromium has crashed or is busy
- ✅ Bulk fetch up to 10 URLs in one request (batch optimization)
- ❌ x.com tweet pages — its server-side renderer drops out before x.com's React boots; returns "JavaScript is disabled" page. **Use Tier 1 instead.**
- ❌ Login-walled content — no auth/cookie support
- ❌ POST operations — fetch-only

## Setup

1. Get a free API key: [tinyfish.ai](https://tinyfish.ai) — no credit card.
2. Set as env var:

```bash
export TINYFISH_API_KEY="your_key_here"
# or in .env file
echo 'TINYFISH_API_KEY="your_key_here"' >> .env
```

The bundled `scripts/tinyfish_fetch.py` wrapper auto-loads from env or `.env`.

## Basic Usage

```bash
# Single URL
python3 scripts/tinyfish_fetch.py "https://blocked-site.com" --proxy US

# Multiple URLs (max 10 per request — batch optimization)
python3 scripts/tinyfish_fetch.py "https://url1.com" "https://url2.com" --proxy US

# HTML output instead of markdown
python3 scripts/tinyfish_fetch.py "https://site.com" --format html

# Search the web (free unlimited, GET-based)
python3 scripts/tinyfish_fetch.py --search "your query"
```

## Proxy Country Codes

Pass via `--proxy XX` (ISO-3166-1 alpha-2):

| Code | Use case |
|---|---|
| `US` | Default for ISP bypass / most blocked content |
| `JP` | Japanese region-locked |
| `DE` | EU-locked, GDPR-aware |
| `SG` | Asia-Pacific neutral |
| `BR` | Latam-only |

Without `--proxy`, requests come from TinyFish's default region (typically US).

## Direct API (no Python wrapper)

```bash
curl -sX POST https://api.fetch.tinyfish.ai \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://target.com"],
    "format": "markdown",
    "proxy_config": {"country_code": "US"}
  }' | jq -r '.results[0].text'
```

Search API (different endpoint, GET-based):

```bash
curl -s "https://api.search.tinyfish.ai/?query=your+query" \
  -H "X-API-Key: $TINYFISH_API_KEY" | jq '.results[]'
```

## Response Shape

```json
{
  "results": [
    {
      "url": "https://requested.com",
      "final_url": "https://final-after-redirects.com",
      "title": "Page Title",
      "description": "Meta description",
      "language": "en",
      "text": "extracted markdown content...",
      "latency_ms": 1617.4,
      "format": "markdown"
    }
  ],
  "errors": []
}
```

## Pitfalls

| ⚠️ | Issue |
|---|---|
| `--js`, `--render`, `--wait` flags | Don't exist. Fetch always renders JS server-side; no opt-out. |
| Proxy country | Some content geo-checks require specific subnets — try `JP`, `DE`, etc. if `US` fails. |
| Login walls | TinyFish has no cookie/auth support. Returns the public-view DOM. |
| Search vs Fetch | Two different endpoints (search is GET, fetch is POST). Old wrappers may have wrong method. |
| 10-URL batch limit | Documented limit. Larger batches return 400. |

## Decision: TinyFish vs Scrapling

```
Is the page JS-rendered AND not login-walled?
├── Yes
│   ├── Local network reaches it OK?
│   │   ├── Yes → Tier 1 (Scrapling stealth) — local control, faster
│   │   └── No (DNS block / firewall) → Tier 2 (TinyFish --proxy US)
│   └── Site has Cloudflare Turnstile?
│       ├── Yes → Tier 1 (solve_cloudflare=True)
│       └── No → Either tier works; Tier 1 is faster locally
└── No (login wall) → Tier 4 (authenticated)
```

## Cost Reality

- Fetch API: **free unlimited** (as of May 2026)
- Search API: **free unlimited** (as of May 2026)
- Proxy routing: included free
- Rate limit: not advertised, but be reasonable (don't hit it 1000x/min)

> **No upgrade tier exists publicly.** TinyFish positions as "free for AI agents". If they ever add paywalled tiers, this doc + the wrapper script need updates.

## See Also

- [`tier-1-scrapling.md`](tier-1-scrapling.md) — primary tier when local works
- [`tier-3-mirrors.md`](tier-3-mirrors.md) — for X/Twitter replies/threads (Tier 1 over xcancel)
