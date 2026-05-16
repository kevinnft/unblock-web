# Ubuntu 26.04 Chromium Install Fix

If you're on Ubuntu 26.04 (or any distro Playwright/Patchright don't ship for yet), Chromium install fails with:

```
$ patchright install chromium
Failed to install browsers
Error: ERROR: Patchright does not support chromium on ubuntu26.04-x64
```

Or:

```
$ playwright install chromium
Failed to install browsers
Error: ERROR: Playwright does not support chromium on ubuntu26.04-x64
```

## Root Cause

- Playwright and Patchright don't ship Ubuntu 26.04 builds yet (released April 2026)
- Their installer detects host platform and refuses if not on the allowlist
- The actual Chromium binary from the Ubuntu 24.04 build runs fine on 26.04 — only the installer's allowlist is the blocker

## The Fix

Override platform detection at install time:

```bash
# Install Chromium for Playwright
PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 \
  python3 -m playwright install chromium

# Install Chromium for Patchright (Scrapling actually uses this fork)
PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 \
  python3 -m patchright install chromium
```

Or use the bundled script (handles both + verifies):

```bash
bash scripts/heal-chromium.sh
```

The script accepts env overrides:

```bash
# Use a specific venv
PYTHON=/path/to/venv/bin/python bash scripts/heal-chromium.sh

# Different parent platform (e.g. fedora, arch — try ubuntu22.04-x64 too)
PLATFORM_OVERRIDE=ubuntu22.04-x64 bash scripts/heal-chromium.sh
```

## Verify Install

After install, `~/.cache/ms-playwright/` should contain:

```
~/.cache/ms-playwright/
├── chromium-1217/                ← full Chromium
├── chromium_headless_shell-1217/ ← headless shell variant
└── ffmpeg-1011/                  ← media support
```

Run the canary:

```bash
python3 scripts/verify-stack.py --verbose
# [OK ] Tier 1: Scrapling+Patchright: ...
```

## What This Unlocks

After the override succeeds:

- ✅ Scrapling `StealthyFetcher` (real browser, JS rendering)
- ✅ Tweet content from x.com without authentication (page renders the tweet body before showing the login modal, headless browser captures it)
- ✅ Cloudflare bypass via `solve_cloudflare=True`
- ✅ Full SPA rendering (React/Vue/Next.js)
- ✅ All `mcp_scrapling_*` tools functional
- ✅ Anything depending on Patchright/Playwright

## Other Distros

The same approach should work for any distro Playwright doesn't list. Try these parent platforms in order:

| Your distro | Try `PLATFORM_OVERRIDE=` |
|---|---|
| Ubuntu 26.04 | `ubuntu24.04-x64` |
| Ubuntu 25.10 | `ubuntu24.04-x64` |
| Ubuntu 24.10 | `ubuntu24.04-x64` |
| Debian 13 | `ubuntu24.04-x64` |
| Pop!_OS 24.04 | `ubuntu24.04-x64` |
| Fedora 41+ | `ubuntu24.04-x64` (try, may need libs) |
| WSL2 (any Ubuntu) | matches your WSL distro |
| Older systems | `ubuntu22.04-x64` |

If the binary actually fails to launch (not the installer), you'll need missing system libs — `apt install libnspr4 libnss3 libatk-bridge2.0-0 libxkbcommon0 libatspi2.0-0 libxrandr2 libxcomposite1 libxdamage1 libgbm1 libpango-1.0-0 libcairo2 libasound2`.

## Related Issue

The override env var is mentioned in Playwright source but not in the public docs. Reference: search `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE` in [microsoft/playwright](https://github.com/microsoft/playwright) issues.

## Why Not Just Wait For Official Support?

You can — Playwright eventually adds new Ubuntu LTS builds. But:
- Ubuntu 26.04 is non-LTS (may never get explicit support)
- Wait time is months
- The override is a one-line fix
- Same Chromium binary works fine

If you'd rather wait, run scraping inside a Docker container based on `ubuntu:24.04` instead.
