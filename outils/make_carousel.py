"""Generate a typographic Instagram carousel (1080x1350) with Pillow.
Usage: python3 make_carousel.py <spec.json> <out_dir>
"""
import json, sys, os, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
F = "/usr/share/fonts/opentype/inter/"
SERIF_B = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"

def hex2rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def background(c1, c2, glow, seed):
    random.seed(seed)
    base = Image.new("RGB", (W, H))
    a, b = hex2rgb(c1), hex2rgb(c2)
    px = base.load()
    for y in range(H):
        t = y / H
        col = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = col
    # soft light glow
    g = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(g)
    gx, gy = int(W * glow[0]), int(H * glow[1])
    for r in range(700, 0, -20):
        d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=int(110 * (1 - r / 700)))
    g = g.filter(ImageFilter.GaussianBlur(80))
    light = Image.new("RGB", (W, H), hex2rgb(glow[2]))
    base = Image.composite(light, base, g)
    # film grain
    noise = Image.effect_noise((W, H), 28).convert("L")
    base = Image.blend(base, Image.merge("RGB", (noise,) * 3), 0.06)
    # vignette
    v = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(v)
    dv.ellipse([-300, -250, W + 300, H + 250], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(base, dark, v)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def photo_background(path, focus, pos, dim):
    """Cover-crop a photo to 1080x1350, darken it, and add a gradient behind the text."""
    from PIL import ImageEnhance, ImageOps
    im = ImageOps.exif_transpose(Image.open(os.path.join(REPO, path))).convert("RGB")
    sc = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * sc + 0.5), int(im.height * sc + 0.5)), Image.LANCZOS)
    fx, fy = focus
    left = int((im.width - W) * fx); top = int((im.height - H) * fy)
    im = im.crop((left, top, left + W, top + H))
    im = ImageEnhance.Brightness(im).enhance(dim)
    # vertical gradient: opaque black on the text side, fading away
    g = Image.new("L", (1, H))
    for y in range(H):
        t = y / H if pos == "bas" else 1 - y / H
        g.putpixel((0, y), int(235 * max(0.0, (t - 0.25) / 0.75) ** 1.3))
    g = g.resize((W, H))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, g)
    # light top band for the handle
    band = Image.new("L", (1, H))
    for y in range(H):
        band.putpixel((0, y), int(150 * max(0.0, 1 - y / 260)))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, band.resize((W, H)))
    return im

def wrap(draw, text, font, maxw):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textlength(test, font=font) <= maxw:
                cur = test
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines

def slide(s, i, n, handle, accent, out, reel=False):
    pos = s.get("pos", "haut")
    if s.get("photo"):
        img = photo_background(s["photo"], s.get("focus", [0.5, 0.5]), pos, s.get("dim", 0.72))
    else:
        img = background(s["c1"], s["c2"], s["glow"], i)
    d = ImageDraw.Draw(img)
    acc = hex2rgb(accent)
    margin = 100
    # top bar: handle + counter
    small = ImageFont.truetype(F + "Inter-Medium.otf", 30)
    d.text((margin, 80), handle, font=small, fill=(255, 255, 255, 200))
    cnt = f"{i}/{n}"
    d.text((W - margin - d.textlength(cnt, font=small), 80), cnt, font=small, fill=(220, 220, 220))
    # text block height (to place it at the bottom when pos == "bas")
    size = s.get("size", 76)
    font = ImageFont.truetype(SERIF_B, size)
    sf = ImageFont.truetype(SERIF_I, 44)
    lines = wrap(d, s["text"], font, W - 2 * margin)
    sub_lines = wrap(d, s["sub"], sf, W - 2 * margin) if s.get("sub") else []
    block = (100 if s.get("kicker") else 0) + len(lines) * int(size * 1.22) + (30 + 58 * len(sub_lines) if sub_lines else 0)
    if pos == "bas":
        y = (H - 260 if i < n else H - 300) - block
    else:
        y = 330
    # kicker
    if s.get("kicker"):
        k = ImageFont.truetype(F + "Inter-SemiBold.otf", 34)
        d.text((margin, y), s["kicker"].upper(), font=k, fill=acc)
        y += 80
        d.line([margin, y - 20, margin + 90, y - 20], fill=acc, width=5)
        y += 20
    # main text
    for line in lines:
        d.text((margin + 3, y + 3), line, font=font, fill=(0, 0, 0))
        d.text((margin, y), line, font=font, fill=(255, 255, 255))
        y += int(size * 1.22)
    # sub text
    if s.get("sub"):
        y += 30
        for line in sub_lines:
            d.text((margin, y), line, font=sf, fill=(235, 228, 215))
            y += 58
    # bottom: swipe or CTA
    bf = ImageFont.truetype(F + "Inter-SemiBold.otf", 32)
    if i < n and reel:
        pass
    elif i < n:
        t = "Glisse  →"
        d.text((W - margin - d.textlength(t, font=bf), H - 120), t, font=bf, fill=acc)
    else:
        t = s.get("cta", "Abonne-toi pour d'autres leçons de vie")
        d.rounded_rectangle([margin, H - 170, W - margin, H - 80], radius=45, fill=acc)
        d.text((W / 2 - d.textlength(t, font=bf) / 2, H - 143), t, font=bf, fill=(20, 20, 20))
    # progress dots
    dy = H - 112 if i < n else H - 215
    for k in range(n):
        x = margin + k * 26
        d.ellipse([x, dy, x + 12, dy + 12], fill=acc if k + 1 == i else (120, 120, 120))
    img.save(os.path.join(out, f"slide_{i:02d}.png"), optimize=True)

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    n = len(spec["slides"])
    for i, s in enumerate(spec["slides"], 1):
        slide(s, i, n, spec["handle"], spec["accent"], out, spec.get("reel", False))
    print("ok", n)
