#!/usr/bin/env python3
"""TinyFish Fetch wrapper - fallback when Scrapling is blocked by Cloudflare/anti-bot.
Usage: tinyfish_fetch.py <url> [url2] [url3] ... [--format markdown|html|json] [--proxy US|JP|...]
"""
import sys
import os
import json
import urllib.request

API_KEY = os.environ.get("TINYFISH_API_KEY", "")
ENDPOINT = "https://api.fetch.tinyfish.ai"

def fetch(urls, fmt="markdown", proxy_country=None):
    payload = {"urls": urls, "format": fmt}
    if proxy_country:
        payload["proxy_config"] = {"country_code": proxy_country}
    
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        return result
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:500]}"}
    except Exception as e:
        return {"error": str(e)}

def search(query, location=None, language=None, page=None, include_thumbnail=False):
    """Search via TinyFish Search API (GET method, free unlimited)."""
    import urllib.parse
    params = {"query": query}
    if location:
        params["location"] = location
    if language:
        params["language"] = language
    if page is not None:
        params["page"] = str(page)
    if include_thumbnail:
        params["include_thumbnail"] = "true"
    qs = urllib.parse.urlencode(params)
    endpoint = f"https://api.search.tinyfish.ai/?{qs}"
    req = urllib.request.Request(
        endpoint,
        headers={"X-API-Key": API_KEY}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:500]}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if not API_KEY:
        print("Error: TINYFISH_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    args = sys.argv[1:]
    if not args:
        print("Usage: tinyfish_fetch.py <url> [url2...] [--format markdown] [--proxy US]")
        print("       tinyfish_fetch.py --search 'query here'")
        sys.exit(1)
    
    fmt = "markdown"
    proxy = None
    urls = []
    search_query = None
    
    i = 0
    while i < len(args):
        if args[i] == "--format" and i + 1 < len(args):
            fmt = args[i + 1]
            i += 2
        elif args[i] == "--proxy" and i + 1 < len(args):
            proxy = args[i + 1]
            i += 2
        elif args[i] == "--search" and i + 1 < len(args):
            search_query = args[i + 1]
            i += 2
        else:
            urls.append(args[i])
            i += 1
    
    if search_query:
        result = search(search_query)
        if "results" in result and result["results"]:
            for r in result["results"]:
                print(f"{r.get('position', '?')}. {r.get('title', '(no title)')}")
                print(f"   {r.get('url', '')}")
                snippet = r.get("snippet", "").strip()
                if snippet:
                    print(f"   {snippet}")
                print()
        elif "error" in result:
            print(f"ERROR: {result['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            print(json.dumps(result, indent=2))
    elif urls:
        result = fetch(urls, fmt=fmt, proxy_country=proxy)
        if "results" in result:
            for r in result["results"]:
                print(f"=== {r.get('title', 'No title')} ===")
                print(f"URL: {r.get('url')}")
                print(f"Final URL: {r.get('final_url')}")
                print()
                print(r.get("text", ""))
                print()
        if "errors" in result and result["errors"]:
            for e in result["errors"]:
                print(f"ERROR: {e}", file=sys.stderr)
        if "error" in result:
            print(f"ERROR: {result['error']}", file=sys.stderr)
            sys.exit(1)
