# Changelog

All notable changes to **unblock-web** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] — 2026-05-16

### Fixed
- `unblock-web --version` and `unblock_web.__version__` now match the installed wheel version (previously stuck at `0.2.0` after a `pip install` of v0.2.2).
- Single source of truth: version is now read dynamically from `src/unblock_web/__init__.py` via Hatch.
- Removed stale `dist/` wheels from git history (they were already in `.gitignore`).

### Added
- `CHANGELOG.md` (this file).
- Repository **Homepage** field now points to https://pypi.org/project/unblock-web/.

## [0.2.2] — 2026-05-16

### Added
- 🎉 First PyPI release. `pip install unblock-web` works worldwide.
- GitHub Actions Trusted Publishing flow for PyPI (no API tokens in repo).

### Fixed
- `pypi` Environment in `publish.yml` now allows tag pushes via the `v*` deployment branch policy.

## [0.2.1] — 2026-05-16

### Added
- ⚡ One-liner installer: `curl -fsSL .../install.sh | bash`. Auto-picks a working Python (3.11–3.13), falls back to `uv`, creates an isolated venv at `~/.unblock-web`, runs `heal`, and symlinks the binary into `~/.local/bin`.
- `docs/publishing.md` — step-by-step PyPI Trusted Publishing setup.

### Changed
- README install order: one-liner → pip → Docker → source.
- `publish.yml` PyPI job is now gated on `vars.PYPI_PUBLISH == 'true'` so a tag push doesn't fail before Trusted Publishing is configured.
- Switched README install command to git-URL form during the PyPI bootstrap window.

### Removed
- Broken PyPI badge (re-added in 0.2.2 once the package was live).

## [0.2.0] — 2026-05-16

### Added
- `unblock-web heal` command: detects Ubuntu 25/26 and uses `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64` automatically before installing Chromium.
- `unblock-web verify` command: 3-tier health check (Scrapling+Patchright, TinyFish API, mirror reachability).
- `unblock-web fetch URL` CLI command.
- Docker image at `ghcr.io/kevinnft/unblock-web` with auto-tagged versions.
- Examples directory with verified scripts: `cloudflare_bypass.py`, `indonesian_isp_bypass.py`, `x_com_tweet.py`, `xcancel_replies.py`.
- Indonesian translation: `README.id.md`.
- `SECURITY.md`, `CONTRIBUTING.md`.
- Canary CI workflow (`canary.yml`) running 3-tier verify on every push.

### Documentation
- Tier-by-tier docs under `docs/`: `tier-1-scrapling.md`, `tier-2-tinyfish.md`, `tier-3-mirrors.md`, `tier-4-authenticated.md`, `ubuntu-26-04-fix.md`, `known-targets.md`.

## [0.1.0] — 2026-05-16

### Added
- Initial release: 4-tier anti-blok decision tree for web scraping.
  - Tier 1: Scrapling + Patchright (Cloudflare Turnstile, JS-SPA bypass).
  - Tier 2: TinyFish API (geo-proxy for ISP DNS blocks).
  - Tier 3: Public mirrors (xcancel.com for X/Twitter without login).
  - Tier 4: Authenticated APIs (xurl, official Twitter API).
- `from unblock_web import fetch` library entry point with auto-tier selection.
- `FetchResult` dataclass with `text`, `html`, `tier`, and metadata fields.

[Unreleased]: https://github.com/kevinnft/unblock-web/compare/v0.2.3...HEAD
[0.2.3]: https://github.com/kevinnft/unblock-web/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/kevinnft/unblock-web/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/kevinnft/unblock-web/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/kevinnft/unblock-web/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kevinnft/unblock-web/releases/tag/v0.1.0
