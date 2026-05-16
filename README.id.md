<div align="center">

# 🌐 unblock-web

### **Stack web scraping anti-blok untuk AI agent**
*Cloudflare Turnstile · Internet Positif (DNS poison) · X.com login wall — beres semua.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/unblock-web?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/unblock-web/)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://github.com/kevinnft/unblock-web/pkgs/container/unblock-web)
[![CI](https://img.shields.io/github/actions/workflow/status/kevinnft/unblock-web/canary.yml?branch=main&style=for-the-badge&label=canary&logo=github-actions&logoColor=white)](https://github.com/kevinnft/unblock-web/actions/workflows/canary.yml)

**🌐 [English](README.md) · 🇮🇩 Bahasa Indonesia**

</div>

---

## 🎯 Solusi untuk Apa

Lo fetch URL, hasilnya sampah:

```
❌ "Please enable JavaScript"   ← x.com tweet, SPA
❌ "Checking your browser..."   ← Cloudflare Turnstile
❌ HTTP 403 / 503               ← bot detection
❌ "internet-positif.info"      ← ISP DNS block (🇮🇩)
❌ "Sign in to view"            ← login wall
```

`unblock-web` adalah **decision tree + script verified** yang milih tool yang tepat per kelas blok. Drop ke AI agent manapun (Claude, Hermes, Cursor, Aider, atau bikinan sendiri) dan stop nebak-nebak pakai curl/wget/playwright doang.

> **Status (May 2026):** Semua 4 tier verified jalan di Ubuntu 26.04 + WSL2 + macOS + GitHub Actions.

---

## 🚀 Mulai Cepat

### Pakai pip

```bash
pip install 'unblock-web[stealth]'
unblock-web heal             # install Chromium (sekali aja)
unblock-web verify           # cek sehat ngga
unblock-web fetch https://x.com/elonmusk/status/123456789
```

### Pakai Docker (zero-install)

```bash
docker run --rm ghcr.io/kevinnft/unblock-web fetch https://example.com
```

### Sebagai library Python

```python
from unblock_web import fetch

# Auto-pilih tier terbaik
page = fetch("https://x.com/seelffff/status/2055155782367187375")
print(page.text)
print(f"Pakai tier: {page.tier}")

# Bypass blok ISP (Indonesia → routing US)
page = fetch("https://web3.okx.com", proxy_country="US")
```

---

## 🛡️ 4-Tier Stack

```
URL masuk → kelas blok apa?

🛡️ Tier 1: Scrapling + Patchright (Chromium lokal)
   → Cloudflare Turnstile · x.com tweet · SPA React/Next/Vue
   → 99% target sulit
   → GRATIS (CPU lokal)

🌍 Tier 2: TinyFish (browser remote, geo-proxy)
   → Bypass DNS Internet Positif via --proxy US
   → Konten geo-locked
   → GRATIS unlimited (no kartu kredit)

🪞 Tier 3: Mirror aggregator (xcancel.com, Nitter)
   → Reply tree X/Twitter yang ga muncul tanpa login
   → GRATIS

🔑 Tier 4: API authenticated (xurl + bearer)
   → DM, akun private, paywall
   → Setup signup gratis di developer.x.com
```

---

## 🧪 Target Verified

Stack ini diuji di sini (May 2026):

| 🎯 Target | 🛠️ Tier | 📦 Hasil |
|---|---|---|
| 🐦 `x.com/<user>/status/<id>` (no login) | T1 + `wait=5000` | ✅ Tweet body + view count + quoted tweet |
| 🛡️ `nowsecure.nl` (anti-bot test Cloudflare) | T1 + `solve_cloudflare=True` | ✅ Lolos challenge |
| 🪞 `xcancel.com/<user>/status/<id>` (CF-protected) | T1 + `solve_cloudflare=True` | ✅ Tweet + 11 reply (multi-bahasa) |
| 🇮🇩 `web3.okx.com` (DNS block ISP Indonesia) | T2 + `--proxy US` | ✅ Render JS + data prize pool |
| 📚 GitHub README | T0 | ✅ Markdown extract |

---

## 🩺 Self-Healing

Tiga lapisan, **tanpa cron** (built buat laptop yang sering tidur):

### 🚦 Canary saat session start

Drop ke hook agent. Diem kalo sehat, alarm kalo regression:

```yaml
# Contoh Hermes Agent (~/.hermes/config.yaml)
hooks:
  on_session_start:
    - command: "unblock-web verify"
      timeout: 30
```

### 🔧 Self-heal saat Chromium hilang

Pas `unblock-web fetch` error `Executable doesn't exist` (biasa abis venv recreate), tinggal:

```bash
unblock-web heal
```

Idempotent. Aman dijalankan kapanpun.

### 👀 Audit on-demand

```bash
unblock-web verify --verbose
```

---

## 🎨 Kenapa "Anti-Blok"?

Tutorial scraping di internet biasanya stop di:

> "Tinggal install Playwright! Tinggal pakai Selenium! Tinggal bayar ScrapingBee!"

Terus ketemu dunia *real*:
- 🇮🇩 ISP poisoning DNS lo (Internet Positif)
- 🇨🇳 GFW drop packet lo
- ☁️ Cloudflare upgrade Turnstile tiap kuartal
- 🐦 X.com nambah login wall semalaman
- 🐧 Ubuntu 26.04 mecahin install Playwright

`unblock-web` adalah decision tree hasil tempur dari pertempuran itu. **Tools gratis aja.** **Ga numpukin API key.** **Reproducible terhadap target yang dilist.**

---

## 📖 Dokumentasi Lengkap

Setiap tier punya deep-dive:

- 📚 [Tier 1 — Scrapling Stealth](docs/tier-1-scrapling.md)
- 📚 [Tier 2 — TinyFish Geo-Proxy](docs/tier-2-tinyfish.md)
- 📚 [Tier 3 — Aggregator Mirror](docs/tier-3-mirrors.md)
- 📚 [Tier 4 — API Authenticated](docs/tier-4-authenticated.md)
- 🐧 [Fix Ubuntu 26.04 Chromium](docs/ubuntu-26-04-fix.md)
- 🎯 [Database target yang udah dicoba](docs/known-targets.md)

---

## 🤝 Kontribusi

Nemu target yang stack ini ga bisa? Buka issue:

1. ❓ URL atau pattern-nya
2. 📋 Apa yang dikembaliin tiap tier (paste failure-nya)
3. 🤔 Hipotesis (login? CF v3? anti-bot baru?)

Atau kirim PR ke [`docs/known-targets.md`](docs/known-targets.md) kalo udah nemu workaround.

---

## ⚖️ Etik & Legal

Stack ini buat **baca konten yang publik**:

✅ Tweet publik, blog, dokumentasi, GitHub
✅ Konten yang lo bisa baca di browser
✅ API yang lo punya kunci-nya

❌ **Jangan** dipake buat:
- Scrape di belakang autentikasi yang bukan milik lo
- Langgar Terms of Service situs
- Mass-extract konten copyright
- Bikin tool credential-harvesting / phishing

Hormatin `robots.txt`. Hormatin rate limit. Jadi warga yang baik di internet.

---

## 🙏 Credits

Stack disusun dari:

- 🛡️ [**Scrapling**](https://github.com/D4Vinci/Scrapling)
- 🥷 [**Patchright**](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)
- 🐟 [**TinyFish**](https://tinyfish.ai)
- 🪞 [**xcancel.com**](https://xcancel.com)
- 🐤 [**xurl**](https://github.com/xdevplatform/xurl)

---

<div align="center">

**Dibuat dengan 🥷 oleh [@kevinnft](https://github.com/kevinnft)**
*Field-tested di kondisi internet Indonesia.*

[⬆ Kembali ke atas](#-unblock-web)

</div>
