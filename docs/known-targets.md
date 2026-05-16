# Known Targets

A community-maintained list of sites tested with this stack — what works, what doesn't, what config to use.

> **Found a new one?** Open a PR with the entry. Format: target, tier used, exact flags, verification date, notes.

## ✅ Verified Working

### Cloudflare-protected sites

| Target | Tier | Flags | Last verified | Notes |
|---|---|---|---|---|
| `nowsecure.nl` | T1 | `solve_cloudflare=True, wait=8000` | 2026-05-16 | Anti-bot test page; only serves "NOWSECURE / by nodriver" to convincing bots |
| `xcancel.com/<user>/status/<id>` | T1 | `solve_cloudflare=True, network_idle=True, wait=5000` | 2026-05-16 | Twitter mirror with Cloudflare; full reply tree exposed |

### Twitter / X.com

| Target | Tier | Flags | Last verified | Notes |
|---|---|---|---|---|
| `x.com/<user>/status/<id>` (no auth, body only) | T1 | `network_idle=True, wait=5000` | 2026-05-16 | DOM captured before login modal; gets root tweet only |
| `x.com/<user>/status/<id>` (replies/thread) | T1 + T3 | go through `xcancel.com/...` | 2026-05-16 | Direct x.com unauth doesn't render replies |

### ISP-blocked (Indonesian Internet Positif)

| Target | Tier | Flags | Last verified | Notes |
|---|---|---|---|---|
| `web3.okx.com` | T2 | TinyFish `--proxy US` | 2026-05-16 | DNS-blocked locally; remote browser bypasses |
| `binance.com` | T2 | TinyFish `--proxy US` | (untested via this stack — community PR welcome) | Same DNS block class |

### SPAs / dynamic content

| Target | Tier | Flags | Last verified | Notes |
|---|---|---|---|---|
| GitHub README rendered | T0 | `scrapling.Fetcher().get()` | 2026-05-16 | Static HTML, no browser needed |

## ⚠️ Known Hard / Unsolved

These targets resist the current stack. PRs welcome with workarounds.

| Target | Failure mode | What was tried | Best workaround |
|---|---|---|---|
| `linkedin.com/in/<user>` | Login wall | T1, T2 | T4: cookie injection or LinkedIn API |
| `instagram.com/<user>/p/<post>` | Login wall (most posts) | T1, T2 | T4: official Graph API |
| `facebook.com/<post>` | Login wall | T1, T2 | T4: Graph API + page access token |
| Cloudflare Turnstile v3 (new) | `solve_cloudflare=True` returns mid-challenge HTML | T1 with `wait=15000` | None known yet — bump scrapling/patchright versions |
| DataDome-protected sites | Anti-bot detects Patchright | T1 | Browserbase or commercial stealth-as-a-service |

## 🔬 How to add a new entry

```bash
# 1. Verify it works
python3 examples/<closest_existing>.py "your_url"

# 2. If it works with a tweak, document the tweak

# 3. Open a PR adding a row to the relevant table above
```

Format:

| `domain.com/<pattern>` | T<n> | `key=value, key=value` | YYYY-MM-DD | Short note |

Keep notes terse — quirks, gotchas, why this config and not another.

## 🤝 Maintenance

This file is community-maintained. Entries older than ~6 months should be re-verified or marked `(unverified since YYYY-MM)`. Anti-bot services iterate — what worked last year may not work today.
