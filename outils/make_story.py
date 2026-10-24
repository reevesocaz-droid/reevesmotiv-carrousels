"""Make a 9:16 Instagram story (1080x1920 JPG) announcing a new post.

Usage: python3 make_story.py <dossier> [reel]
Takes <dossier>/slide_01.png as the visual and writes <dossier>/story.jpg.
Pass "reel" as 2nd argument when the publication is a reel (changes the label).
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1080, 1920
F = "/usr/share/fonts/opentype/inter/"
ACC = (232, 176, 74)

def main():
    folder = sys.argv[1]
    is_reel = len(sys.argv) > 2 and sys.argv[2] == "reel"
    s = Image.open(os.path.join(folder, "slide_01.png")).convert("RGB")
    bg = s.resize((int(s.width * H / s.height), H)).crop((0, 0, W, H)).resize((W, H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(45))).enhance(0.35)
    # card: the cover slide, slightly smaller, rounded corners, drop shadow
    cw = 860; ch = int(s.height * cw / s.width)
    card = s.resize((cw, ch), Image.LANCZOS)
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, ch], radius=36, fill=255)
    x, y = (W - cw) // 2, (H - ch) // 2 + 30
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([x + 10, y + 24, x + cw + 10, y + ch + 24], radius=40, fill=170)
    bg = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), bg, sh.filter(ImageFilter.GaussianBlur(30)))
    bg.paste(card, (x, y), mask)
    d = ImageDraw.Draw(bg)
    # top label
    lab = "NOUVEAU REEL" if is_reel else "NOUVEAU POST"
    f1 = ImageFont.truetype(F + "Inter-Bold.otf", 44)
    tw = d.textlength(lab, font=f1)
    d.rounded_rectangle([(W - tw) / 2 - 36, y - 140, (W + tw) / 2 + 36, y - 60], radius=40, fill=ACC)
    d.text(((W - tw) / 2, y - 128), lab, font=f1, fill=(20, 20, 20))
    # bottom call to action
    f2 = ImageFont.truetype(F + "Inter-SemiBold.otf", 40)
    t = "Va le voir sur mon profil  ↓" if not is_reel else "Regarde-le sur mon profil  ↓"
    d.text(((W - d.textlength(t, font=f2)) / 2, y + ch + 70), t, font=f2, fill=(255, 255, 255))
    f3 = ImageFont.truetype(F + "Inter-Medium.otf", 34)
    h = "@reevesmotiv"
    d.text(((W - d.textlength(h, font=f3)) / 2, y + ch + 135), h, font=f3, fill=ACC)
    bg.save(os.path.join(folder, "story.jpg"), quality=92)
    print("ok", os.path.join(folder, "story.jpg"))

if __name__ == "__main__":
    main()
