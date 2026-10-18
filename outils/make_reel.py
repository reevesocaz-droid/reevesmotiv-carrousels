"""Turn carousel slides into a 9:16 Instagram reel (MP4, no audio track:
the music is added by Metricool via instagramData.audioConfiguration).

Usage: python3 make_reel.py <dossier> [secondes_par_slide]
Reads <dossier>/slide_*.png, writes <dossier>/reel.mp4 and <dossier>/cover.jpg.
"""
import glob, os, subprocess, sys, tempfile
from PIL import Image, ImageFilter, ImageEnhance

W, H = 1080, 1920

def frame(slide_path, out_path):
    s = Image.open(slide_path).convert("RGB")
    # blurred, darkened background filling 9:16
    bg = s.resize((int(s.width * H / s.height), H)).crop((0, 0, W, H))
    bg = bg.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fg = s.resize((W, int(s.height * W / s.width)))
    bg.paste(fg, (0, (H - fg.height) // 2))
    bg.save(out_path, quality=95)

def main():
    folder = sys.argv[1]
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 3.2
    slides = sorted(glob.glob(os.path.join(folder, "slide_*.png")))
    if not slides:
        sys.exit("aucune slide trouvée")
    fade = 0.5
    with tempfile.TemporaryDirectory() as tmp:
        frames = []
        for i, sp in enumerate(slides):
            fp = os.path.join(tmp, f"f{i:02d}.jpg")
            frame(sp, fp)
            frames.append(fp)
        Image.open(frames[0]).save(os.path.join(folder, "cover.jpg"), quality=92)
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for fp in frames:
            cmd += ["-loop", "1", "-t", str(dur), "-i", fp]
        # crossfade chain between still frames
        parts, n = [], len(frames)
        for i in range(n):
            parts.append(f"[{i}:v]fps=30,scale={W}:{H},setsar=1,format=yuv420p[v{i}]")
        last = "v0"
        for i in range(1, n):
            off = round(i * (dur - fade), 2)
            parts.append(f"[{last}][v{i}]xfade=transition=fade:duration={fade}:offset={off}[x{i}]")
            last = f"x{i}"
        cmd += ["-filter_complex", ";".join(parts), "-map", f"[{last}]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                "-r", "30", "-movflags", "+faststart", os.path.join(folder, "reel.mp4")]
        subprocess.run(cmd, check=True)
    print("ok", os.path.join(folder, "reel.mp4"))

if __name__ == "__main__":
    main()
