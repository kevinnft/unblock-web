---
name: Bug report
about: Something in the stack is broken — install, canary, or example
title: "[Bug] "
labels: ["bug"]
---

## What's broken

<!-- Brief description -->

## Steps to reproduce

```bash
# Paste the exact commands you ran
```

## Expected vs actual

**Expected:**

**Actual:**

```
<paste error output / failed canary output>
```

## Environment

- OS: <!-- Ubuntu 26.04 / macOS 15 / WSL2 / etc -->
- Python: <!-- 3.11.x -->
- scrapling: <!--`pip show scrapling | grep Version` -->
- patchright: <!-- `pip show patchright | grep Version` -->
- Browser cache exists? <!-- `ls ~/.cache/ms-playwright/` -->

## Canary output

```
<paste `python3 scripts/verify-stack.py --verbose` output>
```

## Have you tried

- [ ] `bash scripts/heal-chromium.sh`
- [ ] `pip install --upgrade scrapling patchright playwright`
- [ ] Increasing `wait=` to 10000-15000ms
