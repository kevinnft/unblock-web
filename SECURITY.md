# Security Policy

## Reporting a Vulnerability

Found a bug that exposes credentials, leaks data, or could be used to bypass authentication on a site you don't own?

Email: kevinnft@users.noreply.github.com (use GitHub's no-reply, no real email needed)

Or open a GitHub Security Advisory: https://github.com/kevinnft/unblock-web/security/advisories/new

I aim to respond within 7 days.

## Out of Scope

The following are NOT considered security issues in this repo:

- Reports that "this code can be used to scrape sites" — yes, that's the point. See [Ethics & Legal in README](README.md#%EF%B8%8F-ethics--legal).
- Reports that scraping sites X violates X's Terms of Service — that's a contractual issue, not a security vulnerability.
- Cloudflare bypass capability — Cloudflare is an anti-bot vendor; bypassing it is what this repo documents.

## In Scope

These ARE in scope:

- Hardcoded API keys / tokens / passwords in any committed file
- Logic that exfiltrates user data to a third party
- Code that executes arbitrary commands from untrusted input
- Path traversal / SSRF in any helper script
- Insecure defaults that could harm the user (e.g. logging full bearer tokens, world-readable secret files)
- Supply chain issues with `requirements.txt` pins

## Coordinated Disclosure

If you find an in-scope issue, please:

1. Don't open a public issue
2. Email or use the GitHub security advisory link above
3. Give me 30 days to fix before public disclosure
4. I'll credit you in the fix commit unless you prefer anonymity
