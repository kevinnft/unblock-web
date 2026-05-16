#!/usr/bin/env bash
# heal-chromium.sh — Install/repair Patchright + Playwright Chromium binaries.
#
# Why: On Ubuntu 26.04 (and any future distro Playwright doesn't ship builds
# for yet), `patchright install chromium` and `playwright install chromium`
# refuse with "platform not supported". The actual Chromium binary from the
# Ubuntu 24.04 build runs fine — only the installer's allowlist blocks it.
#
# Fix: set PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 (or whatever
# your target's parent platform is) and re-run.
#
# Idempotent — safe to run multiple times.
#
# Usage:
#   bash scripts/heal-chromium.sh                      # use system python
#   PYTHON=path/to/venv/bin/python bash heal-chromium.sh   # use specific venv
#   PLATFORM_OVERRIDE=ubuntu22.04-x64 bash heal-chromium.sh # different parent

set -e

# Defaults — caller can override via env vars
PYTHON="${PYTHON:-python3}"
PLATFORM_OVERRIDE="${PLATFORM_OVERRIDE:-ubuntu24.04-x64}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "ERROR: python interpreter not found: $PYTHON" >&2
    echo "Set PYTHON=/path/to/python explicitly." >&2
    exit 1
fi

echo "Using Python: $($PYTHON -V 2>&1)"
echo "Platform override: $PLATFORM_OVERRIDE"
echo ""

# Verify deps
for mod in playwright patchright; do
    if ! "$PYTHON" -c "import $mod" 2>/dev/null; then
        echo "Installing $mod..."
        "$PYTHON" -m pip install --quiet "$mod" 2>&1 | tail -3 || {
            echo "ERROR: pip install $mod failed" >&2
            exit 1
        }
    fi
done

echo "Re-installing Chromium with platform override..."

PLAYWRIGHT_HOST_PLATFORM_OVERRIDE="$PLATFORM_OVERRIDE" \
    "$PYTHON" -m playwright install chromium 2>&1 | tail -5

PLAYWRIGHT_HOST_PLATFORM_OVERRIDE="$PLATFORM_OVERRIDE" \
    "$PYTHON" -m patchright install chromium 2>&1 | tail -5

echo ""
echo "Verifying install..."

CACHE_DIR="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"

if compgen -G "$CACHE_DIR/chromium-*" >/dev/null \
   || compgen -G "$CACHE_DIR/chromium_headless_shell-*" >/dev/null; then
    echo "OK: Chromium installed under $CACHE_DIR/"
    ls "$CACHE_DIR/" | grep -E "chromium|ffmpeg" | head -5
    exit 0
else
    echo "FAIL: Chromium directory still missing under $CACHE_DIR" >&2
    echo "Manual debug: PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=$PLATFORM_OVERRIDE $PYTHON -m patchright install chromium" >&2
    exit 1
fi
