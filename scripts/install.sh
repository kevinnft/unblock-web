#!/usr/bin/env bash
# unblock-web one-liner installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/kevinnft/unblock-web/main/scripts/install.sh | bash
#
# What it does:
#   1. Picks a working Python (prefers 3.11 → 3.12 → 3.13 → 3.10 → 3.14)
#   2. Creates an isolated venv at ~/.unblock-web (or uses uv if installed)
#   3. pip-installs unblock-web[stealth] from git
#   4. Runs `unblock-web heal` to install Chromium with the OS-detect override
#   5. Symlinks `unblock-web` into ~/.local/bin (or asks you to add it to PATH)
#
# Reversible:  rm -rf ~/.unblock-web ~/.local/bin/unblock-web

set -euo pipefail

INSTALL_DIR="${UNBLOCK_WEB_HOME:-$HOME/.unblock-web}"
BIN_DIR="${UNBLOCK_WEB_BIN_DIR:-$HOME/.local/bin}"
GIT_URL="https://github.com/kevinnft/unblock-web.git"
VERSION="${UNBLOCK_WEB_VERSION:-main}"

# ─── helpers ─────────────────────────────────────────────────────────
note()  { printf '\033[36m▶\033[0m %s\n' "$*"; }
ok()    { printf '\033[32m✓\033[0m %s\n' "$*"; }
warn()  { printf '\033[33m!\033[0m %s\n' "$*"; }
fail()  { printf '\033[31m✗\033[0m %s\n' "$*" >&2; exit 1; }

# ─── pick the right Python ───────────────────────────────────────────
# Some distros (Ubuntu 26.04) ship Python 3.14 as default but don't include
# python3-venv. Prefer a Python where venv works out of the box.
PYTHON=""
for cand in python3.11 python3.12 python3.13 python3.10 python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c 'import venv, ensurepip' 2>/dev/null; then
      PYTHON=$(command -v "$cand")
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  # Fall back to uv if available — it has its own Python toolchain.
  if command -v uv >/dev/null 2>&1; then
    note "No working python venv — falling back to uv"
    note "Creating venv at $INSTALL_DIR (uv will install Python if needed)"
    uv venv --python 3.11 "$INSTALL_DIR" --quiet
    "$INSTALL_DIR/bin/python" -m ensurepip --quiet 2>/dev/null || true
    uv pip install --python "$INSTALL_DIR/bin/python" --quiet "unblock-web[stealth] @ git+${GIT_URL}@${VERSION}"
  else
    fail "No working Python venv found. Install one of: python3.11, python3.12, or uv (https://github.com/astral-sh/uv)"
  fi
else
  PYVER=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  note "Python $PYVER ($PYTHON) selected"

  note "Creating venv at $INSTALL_DIR"
  "$PYTHON" -m venv "$INSTALL_DIR"

  note "Installing unblock-web from $GIT_URL@$VERSION"
  "$INSTALL_DIR/bin/pip" install --quiet --upgrade pip
  "$INSTALL_DIR/bin/pip" install --quiet "unblock-web[stealth] @ git+${GIT_URL}@${VERSION}"
fi

# ─── heal (install Chromium with OS-detect override) ─────────────────
note "Running unblock-web heal (installs Chromium)"
"$INSTALL_DIR/bin/unblock-web" heal

# ─── symlink ─────────────────────────────────────────────────────────
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/bin/unblock-web" "$BIN_DIR/unblock-web"
ok "Symlinked $BIN_DIR/unblock-web → $INSTALL_DIR/bin/unblock-web"

# ─── verify ──────────────────────────────────────────────────────────
note "Verifying installation"
if "$INSTALL_DIR/bin/unblock-web" verify --skip-tier2 >/dev/null 2>&1; then
  ok "unblock-web verify: PASS"
else
  warn "unblock-web verify failed — run \`$INSTALL_DIR/bin/unblock-web verify --verbose\` to debug"
fi

# ─── PATH guidance ───────────────────────────────────────────────────
if echo ":$PATH:" | grep -qF ":$BIN_DIR:"; then
  ok "$BIN_DIR is in PATH"
  echo ""
  echo "Try:  unblock-web fetch https://example.com"
else
  warn "$BIN_DIR is not in PATH. Add this to your shell profile:"
  echo ""
  echo "    export PATH=\"$BIN_DIR:\$PATH\""
  echo ""
  echo "Or just call:  $INSTALL_DIR/bin/unblock-web fetch https://example.com"
fi

ok "Done."
