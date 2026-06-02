#!/usr/bin/env python3
import sys, json, base64, urllib.request, urllib.parse, re, os, glob

OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
MICROLINK = "https://api.microlink.io"
MODEL = "moonshotai/kimi-k2.6"

def get_openrouter_key():
    patterns = [
        os.path.expanduser("~/.openclaw/agents/*/agent/auth-profiles.json"),
        os.path.expanduser("~/.openclaw/auth-profiles.json"),
    ]
    for pattern in patterns:
        for path in glob.glob(pattern):
            try:
                with open(path) as f:
                    data = json.load(f)
                for profile in data.get("profiles", {}).values():
                    if profile.get("provider") == "openrouter" and profile.get("key"):
                        return profile["key"]
            except:
                continue
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    raise RuntimeError("No OpenRouter API key found.")

def get_screenshot_url(url):
    params = urllib.parse.urlencode({"url": url, "screenshot": "true", "fullPage": "true"})
    with urllib.request.urlopen(f"{MICROLINK}?{params}", timeout=30) as r:
        data = json.loads(r.read())
        return data["data"]["screenshot"]["url"]

def fetch_bytes(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()

def get_page_text(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", "ignore")
        text = re.sub(r'<[^>]+>', ' ', html)
        return re.sub(r'\s+', ' ', text).strip()[:3000]
    except:
        return ""

def analyze(url, img_bytes, page_text):
    key = get_openrouter_key()
    b64 = base64.standard_b64encode(img_bytes).decode()
    payload = {
        "model": MODEL,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": "You are an expert web designer and CRO specialist. Be specific and blunt. No fluff."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": (
                    f"URL: {url}\nPage text: {page_text}\n\n"
                    "Audit this page for:\n"
                    "1. Visual design (colors, fonts, layout, images, spacing)\n"
                    "2. Copy (headlines, CTAs, value prop, typos)\n"
                    "3. Missing trust signals\n"
                    "4. Broken or confusing elements\n\n"
                    "Format:\n"
                    "### 🔴 Critical Fixes\n"
                    "### 🟡 Important Improvements\n"
                    "### 🟢 Nice to Have\n"
                    "### ✅ What's Working\n"
                    "### 💬 Suggested Headline\n"
                    "### 🎯 Suggested CTA\n\n"
                    "Give exact replacement text where relevant."
                )}
            ]}
        ]
    }
    req = urllib.request.Request(
        OPENROUTER_API,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://openclaw.ai",
            "X-Title": "OpenClaw"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
        msg = resp["choices"][0]["message"]
        return msg.get("content") or msg.get("reasoning") or "No response"

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else input("Enter URL: ")
    print(f"\n🔍 Auditing: {url}\n")
    print("📸 Taking screenshot...")
    img_url = get_screenshot_url(url)
    print("⬇️  Downloading...")
    img_bytes = fetch_bytes(img_url)
    page_text = get_page_text(url)
    print("🤖 Analyzing...\n")
    report = analyze(url, img_bytes, page_text)
    print("="*60)
    print(report)
    print("="*60)
