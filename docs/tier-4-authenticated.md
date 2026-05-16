# Tier 4: Authenticated APIs

When Tier 1-3 hit a real login wall (DMs, private accounts, full thread metadata, posting/like operations), real auth is the only option.

## When You Actually Need This

You need Tier 4 when content is:
- Behind a true login wall — redirects to `/i/flow/signup` or `/login`
- Account-protected (private accounts you follow)
- Direct messages
- Real-time bookmarks, list management
- POST operations (tweet, like, follow, DM-send)

You do NOT need this for:
- Public tweet bodies (Tier 1 stealth handles these)
- Public replies/threads (Tier 3 xcancel handles these)
- Public profile metadata (Tier 1 + parsing)

> **Rule of thumb:** if you can read it without being logged in via a real browser, Tier 1-3 can read it.

## X/Twitter Setup (Free Tier)

The free tier is plenty for "occasional read of locked content":

| Tier | Cost | Limits |
|---|---|---|
| **Free** | $0 | Read-only, 1500 tweets/month, 1 project, 1 app |
| **Basic** | $200/mo | 50k reads/mo, write access (post tweets, send DMs) |
| **Pro** | $5000/mo | Business volumes |

### One-Time Bearer Token Setup (~10-15 min)

#### Step 1: Create developer account

Go to [developer.x.com/en/portal/dashboard](https://developer.x.com/en/portal/dashboard) and sign in with your existing X account. Free tier signup is instant since 2024.

#### Step 2: Create project + app

1. Click "Create Project" — give it any name (e.g. `unblock-web`)
2. Inside the project, "Create App" — same naming
3. App settings → "Keys and tokens" tab
4. Copy the **Bearer Token** (one-time display — save it now)

You also see API Key, API Secret, Access Token, Access Secret. For read-only via `xurl`, only Bearer Token is needed.

#### Step 3: Save securely

```bash
# Add to your local .env (gitignored)
echo 'X_API_BEARER_TOKEN=YOUR_BEARER_HERE' >> .env
chmod 600 .env
```

#### Step 4: Configure xurl

[xurl](https://github.com/xdevplatform/xurl) is the official X CLI. Install:

```bash
# Mac
brew install xurl

# Linux (or any Go env)
go install github.com/xdevplatform/xurl@latest
```

Configure:

```bash
source .env
xurl auth app --bearer-token "$X_API_BEARER_TOKEN"
xurl auth status   # verify
```

#### Step 5: Test

```bash
# Lookup a tweet
xurl "/2/tweets/2055155782367187375?tweet.fields=created_at,public_metrics,text,entities&expansions=author_id&user.fields=username,name,verified"

# Lookup a user by handle
xurl "/2/users/by/username/seelffff?user.fields=description,public_metrics,verified"
```

Successful response = JSON body. 401 = bearer not loaded. 429 = rate limit hit.

## Common Endpoints (read-only)

```bash
# Tweet by ID
xurl "/2/tweets/{tweet_id}?tweet.fields=text,created_at,public_metrics,entities&expansions=author_id,attachments.media_keys&user.fields=username,verified&media.fields=type,url,preview_image_url"

# Tweet thread / conversation (requires conversation_id from first tweet)
xurl "/2/tweets/search/recent?query=conversation_id:{conv_id}&tweet.fields=author_id,created_at,in_reply_to_user_id&max_results=100"

# User timeline
xurl "/2/users/{user_id}/tweets?max_results=20&tweet.fields=public_metrics,created_at"

# User lookup
xurl "/2/users/by/username/{handle}?user.fields=description,public_metrics,verified,profile_image_url"

# Search recent (last 7 days, free tier)
xurl "/2/tweets/search/recent?query=from:seelffff&tweet.fields=public_metrics&max_results=50"
```

## Rate Limits (free tier, May 2026)

- Tweet lookup: 300/15min window + 1500/month total reads
- User lookup: 300/15min
- Search: 60/15min, 1500/month

Hit a 429 → back off ~15 min before retry. Don't burn quota on bulk backfills; use Tier 1-3 for public content first.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "No apps registered" | Run `xurl auth apps add hermes` (multi-app users) before `xurl auth app`. Single-app: skip. |
| 401 Unauthorized everywhere | Bearer not loaded. Check `xurl auth status`. Re-run `xurl auth app --bearer-token "$X_API_BEARER_TOKEN"`. |
| 429 on first call | Quota already exhausted. Wait 15 min. |
| 403 Forbidden | Endpoint requires elevated tier. Free tier can't access full archive search, DM endpoints, posting. |
| Token rotated/expired | Tokens don't expire by default but can be regenerated from the dev portal. After regen, redo Step 3-4. |

## Alternative: Cookie Injection via Scrapling

If you don't want to set up X API credentials:

```python
from scrapling.fetchers import StealthyFetcher

# Export cookies from your logged-in browser (use browser_cookie3 or
# manual export), then inject:
page = StealthyFetcher.fetch(
    url="https://x.com/i/dms/...",
    cookies=[
        {"name": "auth_token", "value": "...",
         "domain": ".x.com", "path": "/",
         "secure": True, "httpOnly": True},
        {"name": "ct0", "value": "...",
         "domain": ".x.com", "path": "/", "secure": True},
    ],
    network_idle=True,
    wait=5000,
)
```

| | xurl bearer | Cookie injection |
|---|---|---|
| Setup time | 10-15 min | 2 min |
| Durability | Doesn't expire | Cookies expire (re-export periodically) |
| Rate limits | 1500/mo on free | Same as your account's web rate limit |
| Auth gestures | Read-only | Full account access |
| Risk | Low (revokable) | High if cookies leak (full account) |

For automation: bearer is more durable. For one-off DM peek: cookies are faster.

## Security Note

Bearer tokens grant read access to everything your account can read (following list, blocked list, etc.). Treat as a password.

- Store in `.env` (gitignored), never commit
- Don't paste in chat / Slack / Discord
- Rotate immediately if suspected leaked

## See Also

- [`tier-1-scrapling.md`](tier-1-scrapling.md) — handles public content, no auth
- [`tier-3-mirrors.md`](tier-3-mirrors.md) — for X replies without auth
- xurl docs: [github.com/xdevplatform/xurl](https://github.com/xdevplatform/xurl)
- X API v2 reference: [developer.x.com/en/docs/twitter-api](https://developer.x.com/en/docs/twitter-api)
