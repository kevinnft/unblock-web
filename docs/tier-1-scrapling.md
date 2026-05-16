# Tier 1: Scrapling Stealth (Patchright) — Deep Dive

The workhorse of the stack. Local Chromium with anti-fingerprint patches via Patchright. Handles ~99% of "hard" pages.

## When to Use

- ✅ JavaScript-rendered SPAs (React, Next.js, Vue, Svelte, Angular)
- ✅ Cloudflare Turnstile / "Checking your browser..."
- ✅ x.com tweet bodies (no auth needed)
- ✅ Any page where curl returns a near-empty shell
- ❌ Login-walled content (use Tier 4)
- ❌ ISP DNS-blocked sites (use Tier 2 first — local DNS is poisoned)

## Minimal Working Example

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    url="https://target.com/article",
    network_idle=True,        # wait for XHR settle
    solve_cloudflare=True,    # auto-handle Turnstile JS challenge
    wait=5000,                # ms — let SPA hydrate before extraction
)
print(page.markdown)          # clean markdown extract
print(page.status)            # 200
```

Or via the Hermes/MCP wrapper:

```python
mcp_scrapling_stealthy_fetch(
    url="https://target.com",
    extraction_type="markdown",
    network_idle=True,
    solve_cloudflare=True,
    wait=5000,
)
```

## Full Parameter Reference

```python
StealthyFetcher.fetch(
    url="https://target.com",

    # ── Extraction ─────────────────────────────────────
    extraction_type="markdown",     # markdown | html | text
    main_content_only=True,         # strip nav/footer/ads (Readability mode)
    css_selector=".article-body",   # narrow extraction to a specific node

    # ── Browser fingerprint ───────────────────────────
    useragent="Mozilla/5.0 ...",    # override UA
    locale="en-US",                 # navigator.language
    timezone_id="America/New_York", # geo timezone
    headless=True,
    real_chrome=False,              # use real Chrome instead of Chromium
    hide_canvas=True,               # canvas fingerprint defense
    block_webrtc=True,              # prevent WebRTC IP leak
    allow_webgl=True,

    # ── Auth / state ──────────────────────────────────
    cookies=[                       # inject cookies (login state, consent)
        {"name": "auth_token", "value": "...",
         "domain": ".target.com", "path": "/",
         "secure": True, "httpOnly": True}
    ],
    extra_headers={                 # custom headers
        "Authorization": "Bearer ..."
    },

    # ── Network ────────────────────────────────────────
    proxy="http://user:pass@host:port",  # outbound HTTP/SOCKS proxy
    disable_resources=True,         # block images/fonts/css for speed
    google_search=False,            # set True if Referer should be google.com

    # ── Timing ─────────────────────────────────────────
    wait=5000,                      # ms after load before extracting
    timeout=30,                     # seconds for whole operation
    network_idle=True,              # wait until <2 in-flight requests for 500ms
    wait_selector=".content",       # block until selector appears (better than wait)
    wait_selector_state="visible",  # attached | detached | visible | hidden

    # ── Anti-bot ───────────────────────────────────────
    solve_cloudflare=True,          # auto-handle Turnstile JS challenge
    session_id="my-session-id",     # reuse opened session for multi-step
    cdp_url="ws://...",             # connect to remote Chrome DevTools Protocol
)
```

## Persistent Session Pattern (Login Flows)

Multi-step navigation where state must persist:

```python
from scrapling.fetchers import StealthyFetcher

# 1. Open persistent session
session = StealthyFetcher.open_session(
    headless=True,
    solve_cloudflare=True,
    cookies=[...],          # pre-seed login cookies if available
    timeout=60,
)
sid = session["session_id"]

# 2. Reuse session_id for each step — cookies persist between fetches
StealthyFetcher.fetch("https://site.com/login",
                     session_id=sid, wait=3000)
StealthyFetcher.fetch("https://site.com/dashboard",
                     session_id=sid, wait=2000)
result = StealthyFetcher.fetch("https://site.com/private/page",
                               session_id=sid)

# 3. Cleanup
StealthyFetcher.close_session(session_id=sid)
```

Without a persistent session, every fetch starts a fresh browser → loses cookies, hits Cloudflare from scratch each time.

## Bulk Fetch (Batch Scraping)

```python
result = StealthyFetcher.fetch_all(
    urls=["https://target.com/page/1",
          "https://target.com/page/2",
          "https://target.com/page/3"],
    network_idle=True,
    solve_cloudflare=True,
    wait=5000,
)
# Returns list of {url, status, content} per URL
```

Use case: scraping a paginated index where you have all URLs upfront. Up to ~10-20 in parallel depending on RAM.

## Screenshot for Visual Debugging

When extracted text is empty/garbled but you suspect the page actually rendered:

```python
StealthyFetcher.screenshot(
    url="https://site.com",
    session_id=sid,
    full_page=True,
    image_type="png",
    wait=3000,
    wait_selector=".main",
)
```

Reveals: layout, modals, CAPTCHA prompts, hidden login forms.

## CSS Selector Narrowing

For long pages where you only need one section — reduces token cost dramatically:

```python
StealthyFetcher.fetch(
    url="https://news-site.com/article/123",
    css_selector="article.main-content",  # extract just this node
    extraction_type="markdown",
    main_content_only=True,                # plus boilerplate stripping
)
```

## Pitfalls

| ⚠️ | Issue |
|---|---|
| `real_chrome=True` | Requires Chrome installed at the system level — Chromium-only setups (default) ignore this flag. |
| `solve_cloudflare=True` | Adds 5-15s latency. Only enable when CF challenge is suspected. |
| `session_id` | Doesn't auto-expire. Always pair `open_session` with `close_session` or run `list_sessions` periodically. |
| `bulk_*` tools | Share one Patchright instance. If one URL hangs, the whole batch can stall. Set per-URL timeout aggressively. |
| `disable_resources=True` | Breaks JS-heavy sites. They often need fonts/CSS to compute layout before XHRs fire. Default to False. |
| `wait_selector` > `wait` | Wait for a known element instead of guessing milliseconds. More reliable. |

## Verified Targets

| Target | Config | Result |
|---|---|---|
| `x.com/<user>/status/<id>` (no auth) | `wait=5000, network_idle=True` | ✅ Full tweet body + meta + view count |
| `nowsecure.nl` (CF anti-bot test) | `solve_cloudflare=True` | ✅ "NOWSECURE / by nodriver" content |
| `xcancel.com/<user>/status/<id>` | `solve_cloudflare=True, wait=5000` | ✅ Tweet + 11 multilingual replies |

See [`examples/`](../examples/) for runnable scripts.
