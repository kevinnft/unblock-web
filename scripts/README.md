# scripts/ (legacy direct-use)

These standalone scripts predate the pip package. They still work and are kept for users who don't want to `pip install`. Prefer the CLI installed by the package:

| Old | New (pip-installed) |
|---|---|
| `python3 scripts/verify-stack.py --verbose` | `unblock-web verify --verbose` |
| `bash scripts/heal-chromium.sh` | `unblock-web heal` |
| `python3 scripts/tinyfish_fetch.py URL --proxy US` | `unblock-web fetch URL --tier T2 --proxy US` |

The CLI versions are derived from the same logic as these scripts (via `src/unblock_web/`).
