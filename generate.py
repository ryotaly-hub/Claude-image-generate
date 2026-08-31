"""Gemini 3 Pro Image (gemini-3-pro-image) generator / editor.

Usage:
    python generate.py <config_module>
e.g. python generate.py jobs.sniper

Each job module must define:
    PROMPT      : str   - the text instruction
    REF_IMAGES  : list  - (optional) paths to reference images
    OUT_NAME    : str   - output basename (without extension)
    ASPECT      : str   - (optional) e.g. "5:4"  (default "5:4")
    SIZE        : tuple - (optional) exact output pixels (default (2000, 1600))
"""
import base64, importlib, json, os, sys, urllib.request, urllib.error

D = os.path.dirname(os.path.abspath(__file__))
MODEL = "gemini-3-pro-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def api_key():
    with open(os.path.join(D, ".env"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise SystemExit("GEMINI_API_KEY not found in .env")


def run(job):
    parts = []
    for p in getattr(job, "REF_IMAGES", []):
        path = p if os.path.isabs(p) else os.path.join(D, p)
        mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
        with open(path, "rb") as f:
            parts.append({"inline_data": {"mime_type": mime,
                                          "data": base64.b64encode(f.read()).decode()}})
    parts.append({"text": job.PROMPT})

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": getattr(job, "ASPECT", "5:4"),
                            "imageSize": "2K"},
        },
    }
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key()},
    )
    try:
        data = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        print("HTTP", e.code); print(e.read().decode()); raise SystemExit(1)

    out = None
    for part in data["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            out = base64.b64decode(part["inlineData"]["data"])
        elif "text" in part:
            print("model text:", part["text"])
    if not out:
        print(json.dumps(data)[:2000]); raise SystemExit(1)

    raw = os.path.join(D, f"{job.OUT_NAME}_raw.png")
    with open(raw, "wb") as f:
        f.write(out)
    print("saved raw:", len(out), "bytes")

    from PIL import Image
    im = Image.open(raw).convert("RGB")
    print("raw size:", im.size)
    tw, th = getattr(job, "SIZE", (2000, 1600))
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - tw) // 2, (nh - th) // 2
    im = im.crop((l, t, l + tw, t + th))
    final = os.path.join(D, f"{job.OUT_NAME}_{tw}x{th}.png")
    im.save(final)
    print("saved final:", final, im.size)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    run(importlib.import_module(sys.argv[1]))
