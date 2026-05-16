# Examples

Reproducible scripts for each tier and verified target. All examples include the exact configuration that worked in May 2026.

## Setup

```bash
pip install scrapling patchright
bash ../scripts/heal-chromium.sh   # one-time, fixes Ubuntu 26.04+
```

For Tier 2 (TinyFish):

```bash
export TINYFISH_API_KEY="your_free_key"   # get at https://tinyfish.ai
```

## Run

| Example | Tier | What it does |
|---|---|---|
| [`x_com_tweet.py`](x_com_tweet.py) | T1 | Fetch X tweet body without login |
| [`cloudflare_bypass.py`](cloudflare_bypass.py) | T1 | Pass Cloudflare Turnstile (e.g. `nowsecure.nl`) |
| [`xcancel_replies.py`](xcancel_replies.py) | T1 + T3 | Get full X reply tree via mirror |
| [`indonesian_isp_bypass.py`](indonesian_isp_bypass.py) | T2 | Bypass Indonesian ISP DNS block |

```bash
python3 examples/x_com_tweet.py https://x.com/seelffff/status/2055155782367187375
python3 examples/cloudflare_bypass.py https://nowsecure.nl
python3 examples/xcancel_replies.py seelffff 2055155782367187375
python3 examples/indonesian_isp_bypass.py https://web3.okx.com US
```

## Adding Your Own

PRs welcome. Pattern:

1. Pick a target that exercises a specific block class
2. Document the exact config that worked + version date
3. Use only `scrapling`, `patchright`, and Python stdlib (or `urllib` for TinyFish HTTP)
4. Print enough output to verify the bypass succeeded

The cleaner the example, the more useful for the next person.
