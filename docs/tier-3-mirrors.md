# Tier 3: Aggregator Mirrors

For X/Twitter content that won't render fully unauthenticated — replies, threads, full conversation context. Mirrors quote the original but expose more DOM than x.com's logged-out view.

## When to Use

- ✅ Need full thread / replies / conversation tree on X
- ✅ Tweet author has a public account but their reply tree is gated
- ✅ Want quote-tweet expansions
- ❌ Single tweet body — Tier 1 stealth on x.com directly is faster
- ❌ Account-protected (truly private) tweets — use Tier 4

## Primary: xcancel.com

xcancel preserves multilingual replies and full thread context. It's Cloudflare-protected, so always go through Tier 1 stealth:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    url="https://xcancel.com/<user>/status/<tweet_id>",
    network_idle=True,
    solve_cloudflare=True,   # xcancel is CF-protected
    wait=5000,
)
# Returns: tweet body + all replies with author handles + reply counts
```

## Fallback Mirrors

When xcancel is rate-limiting or down:

| Mirror | Status (May 2026) | Notes |
|---|---|---|
| `xcancel.com` | ✅ Working | Best preservation, CF-protected |
| `nitter.net` | ⚠️ Often empty / instance dead | Original Nitter — sporadic |
| `nitter.privacydev.net` | ⚠️ DNS may not resolve from some networks | Try via TinyFish `--proxy US` |
| `nitter.poast.org` | 🔄 Rotates availability | Check before depending on it |
| `x-thread.org` | ⚠️ Search-indexed only | Returns "Thread Not Found" via direct fetch; only useful via search snippets |

**Live instance list:** [github.com/zedeus/nitter/wiki/Instances](https://github.com/zedeus/nitter/wiki/Instances)

## URL Patterns

The mirror URL follows x.com's path structure:

```
x.com/<handle>/status/<id>
   ↓
xcancel.com/<handle>/status/<id>
nitter.net/<handle>/status/<id>
```

For user profiles:

```
x.com/<handle>
   ↓
xcancel.com/<handle>
```

## Pitfalls

| ⚠️ | Issue |
|---|---|
| Mirror DOM can lag x.com | Replies posted in last few minutes may not show — mirrors poll, not stream. |
| Rate limits per mirror | Hit one too hard, rotate to another. Don't hammer a single instance. |
| Cloudflare on xcancel | Always pair with `solve_cloudflare=True` or expect 503. |
| Media (images/video) | URLs work but may proxy through mirror's CDN — different from twimg.com. |
| Quoted tweets | Some mirrors expand them inline, others link out. Check DOM structure. |

## Last Resort: Search-Snippet Reconstruction

If all mirrors fail AND no auth is available, pivot to TinyFish search:

```bash
# Search for the exact tweet ID or distinctive phrase
python3 scripts/tinyfish_fetch.py --search "<exact post id or distinctive phrase>"
```

Aggregator domains that often quote locked content into search-indexable HTML:
- `x-thread.org` (paginated thread reader)
- `xrticles.com` (X article archive)
- `twstalker.com` (account history mirror)
- `lightbrd.com` (brand mention archive)
- LinkedIn/Instagram posts that quote the tweet

Each search result returns a 1-2 line snippet — stitch 3-6 across queries to reconstruct most short-form posts.

> **Always disclose** when using snippet reconstruction: "this is reconstructed from search snippets, not the canonical source."

## Verified Example

```python
# Real run (May 2026) — full tweet + 11 replies in 5 languages
page = StealthyFetcher.fetch(
    url="https://xcancel.com/seelffff/status/2055155782367187375",
    network_idle=True,
    solve_cloudflare=True,
    wait=5000,
)
# Got: tweet body, view count, plus replies in EN, JP, CN, VI, IT
```

## See Also

- [`tier-1-scrapling.md`](tier-1-scrapling.md) — direct x.com fetch (faster for single tweets)
- [`tier-4-authenticated.md`](tier-4-authenticated.md) — when auth is the only option
