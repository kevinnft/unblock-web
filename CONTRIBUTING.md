# Contributing to unblock-web

## Quick PR Workflow

1. Fork + clone
2. Make your change
3. Run the canary locally:
   ```bash
   pip install -e '.[stealth]'
   unblock-web heal
   unblock-web verify --verbose
   ```
4. Push to a branch, open PR

## What Makes a Good Contribution

### 🎯 New verified target

Did you find a site that needed a specific config to bypass? Document it in `docs/known-targets.md` (create if missing) with:

- The URL or pattern
- The exact config that worked (Tier + flags)
- Date verified
- What didn't work (so we don't relearn)

### 📝 New example

Add to `examples/`:

- One file per scenario, runnable standalone
- Document the failure mode it bypasses (in the docstring)
- Use only `scrapling`, `patchright`, and Python stdlib
- Print enough output to verify success

### 📚 Doc improvement

Clarify a tier, add a pitfall, fix a typo. Keep tone matter-of-fact (not marketing fluff). Reference the verified-targets table when claiming "this works".

### 🐛 Bug fix

If `verify-stack.py` is producing false positives/negatives, or `heal-chromium.sh` doesn't work on your distro, PR a fix with the failing case as a comment.

## Style

- Python: stdlib-first; if you need a lib, justify it
- Bash: `set -e`, quote vars, no `&&` chains for setup steps
- Markdown: tables for compact reference, prose for explanation, code blocks for runnable samples
- Commit messages: imperative ("Add X" not "Added X")

## What Won't Be Merged

- Tools that require paid APIs as the only path (free alternatives must stay)
- Tools that bypass authentication (this stack is for public content only)
- Anything that scrapes content where you don't have legal/ethical right to read

## Questions?

Open an issue. We're friendly.
