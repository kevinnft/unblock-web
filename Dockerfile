FROM python:3.12-slim

# unblock-web Docker image — works out of the box with Tier 1 + Tier 2.
#
# Run an ad-hoc fetch:
#   docker run --rm ghcr.io/kevinnft/unblock-web fetch https://example.com
#
# With TinyFish (Tier 2):
#   docker run --rm -e TINYFISH_API_KEY=$TINYFISH_API_KEY \
#     ghcr.io/kevinnft/unblock-web fetch https://blocked.com --proxy US
#
# Persistent shell:
#   docker run --rm -it --entrypoint bash ghcr.io/kevinnft/unblock-web

LABEL org.opencontainers.image.source="https://github.com/kevinnft/unblock-web"
LABEL org.opencontainers.image.description="Anti-blok web scraping stack: 4-tier decision tree (Cloudflare, x.com, ISP DNS bypass)"
LABEL org.opencontainers.image.licenses="MIT"

# Playwright/Patchright system deps (Chromium runtime libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnspr4 libnss3 libatk-bridge2.0-0 libxkbcommon0 libatspi2.0-0 \
    libxrandr2 libxcomposite1 libxdamage1 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2 libxshmfence1 \
    fonts-liberation \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install unblock-web with all extras (Tier 1 stealth included)
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir '.[all]'

# Install Chromium with the platform override (the trick this repo documents)
RUN PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 \
      python -m playwright install chromium && \
    PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 \
      python -m patchright install chromium

# Health check via the canary
HEALTHCHECK --interval=5m --timeout=30s --retries=2 \
    CMD unblock-web verify --skip-tier2 || exit 1

ENTRYPOINT ["unblock-web"]
CMD ["--help"]
