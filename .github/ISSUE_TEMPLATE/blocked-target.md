---
name: Blocked target
about: Report a site/URL the stack cannot crack and request a workaround
title: "[Target] "
labels: ["target-research"]
---

## URL or pattern

<!-- Paste the URL or describe the pattern (e.g. "any *.example.com page") -->

## What each tier returned

### Tier 0 (scrapling.get)

```
<paste output / error / empty content>
```

### Tier 1 (StealthyFetcher.fetch with solve_cloudflare=True)

```
<paste output, status code, first 500 chars>
```

### Tier 2 (TinyFish --proxy US)

```
<paste output>
```

### Tier 3 (xcancel/Nitter mirror) — if X/Twitter content

```
<paste output>
```

## Hypothesis

What kind of block do you think this is?

- [ ] Login wall (redirects to /login or shows "Sign in")
- [ ] Cloudflare Turnstile v3+ (newer than current bypass)
- [ ] Custom JS challenge (not Cloudflare)
- [ ] Geo-block (specific country)
- [ ] Rate limit / IP block
- [ ] Other anti-bot service (DataDome, Akamai, PerimeterX, etc.)
- [ ] No idea — looking for help

## Environment

- OS: <!-- e.g. Ubuntu 26.04, macOS 15, Windows 11 WSL2 -->
- Python: <!-- 3.11.x -->
- scrapling: <!-- pip show scrapling | grep Version -->
- patchright: <!-- pip show patchright | grep Version -->

## Verified targets that DO work for me

<!-- Confirms your install is healthy. Run:
     python3 scripts/verify-stack.py --verbose
     and paste the output -->

```
<paste verify-stack output>
```

## Anything else

<!-- Screenshots, related links, prior attempts, ToS notes if relevant -->
