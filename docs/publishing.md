# Publishing Setup (one-time)

This file documents the one-time setup for automated publishing. Most users won't need to read this — it's for repo maintainers.

## TL;DR

PyPI publishing is **opt-in via the `PYPI_PUBLISH` repo variable**, so a tag push doesn't fail before Trusted Publishing is configured. After running the steps below once, set the variable and PyPI publishes automatically on every tag.

```bash
# After setup is complete, flip the switch:
gh variable set PYPI_PUBLISH --body true --repo kevinnft/unblock-web
```

## Docker (GHCR) — already working ✅

GHCR uses `GITHUB_TOKEN` automatically. No setup needed. The publish.yml workflow:
- Builds the Dockerfile on every tag push
- Tags as `vX.Y.Z`, `X.Y`, and `latest`
- Pushes to `ghcr.io/kevinnft/unblock-web`

Result: `docker pull ghcr.io/kevinnft/unblock-web:v0.2.0` works for anyone.

## PyPI — Trusted Publishing setup

PyPI's Trusted Publishing flow lets you publish from GitHub Actions WITHOUT storing an API token. You configure it once on the PyPI website.

### Step 1: Create the package on PyPI (first time only)

1. Go to https://pypi.org/manage/account/publishing/
2. Sign in / create account if needed
3. Click "Add a new pending publisher"
4. Fill in:
   - **PyPI Project Name**: `unblock-web`
   - **Owner**: `kevinnft`
   - **Repository name**: `unblock-web`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
5. Submit

### Step 2: Configure the GitHub environment

1. Go to https://github.com/kevinnft/unblock-web/settings/environments
2. Click "New environment"
3. Name it: `pypi`
4. Save (no secrets needed — Trusted Publishing uses OIDC)

### Step 3: Trigger a publish

```bash
# Re-run the failed publish
gh workflow run publish.yml --repo kevinnft/unblock-web

# Or push a new patch tag
git tag v0.2.1 -m "Test PyPI publish"
git push origin v0.2.1
```

After PyPI registers the project once, subsequent tag pushes auto-publish.

### Verify

- Package page: https://pypi.org/project/unblock-web/
- Install: `pip install unblock-web` (works for everyone in the world)

## Manual PyPI (fallback if Trusted Publishing not set up)

If you need to publish without configuring Trusted Publishing:

1. Generate an API token at https://pypi.org/manage/account/token/
2. Add it as a GitHub secret named `PYPI_TOKEN`
3. Edit `.github/workflows/publish.yml`, replace the Trusted Publishing step with:

```yaml
- name: Publish to PyPI (token mode)
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_TOKEN }}
```

Trusted Publishing is preferred (no token rotation, no secret leak risk).

## Tagging convention

```bash
# Patch (bug fix)
git tag -a v0.2.1 -m "Fix X"
git push origin v0.2.1

# Minor (new feature, backward compatible)
git tag -a v0.3.0 -m "Add feature Y"
git push origin v0.3.0

# Major (breaking)
git tag -a v1.0.0 -m "First stable release"
git push origin v1.0.0
```

The publish.yml workflow triggers on any `v*.*.*` tag.

## What gets published

Every tag push triggers BOTH:

1. **PyPI** — sdist + wheel from `python -m build`
   - Source layout: `src/unblock_web/`
   - Includes: README, LICENSE, examples/, docs/, scripts/
2. **GHCR** — Docker image from `Dockerfile`
   - Tags: vX.Y.Z, X.Y, latest
   - Multi-arch: amd64 (arm64 not enabled, can be added)

## Bumping version

Two places need the version number:

- `pyproject.toml` → `version = "X.Y.Z"`
- `src/unblock_web/__init__.py` → `__version__ = "X.Y.Z"`

Could be unified later via `hatch-vcs` or similar.
