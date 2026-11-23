"""Branded promo Reel for Kannur Computers: 1080x1920, 30 fps, ~18 s, no footage."""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 18.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "promo.mp4"

NAVY = (10, 22, 48)
NAVY2 = (18, 42, 88)
WHITE = (255, 255, 255)
ACCENT = (255, 176, 32)    # warm amber
CYAN = (90, 200, 255)
MUTED = (175, 195, 225)

LAT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LAT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ML_B = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"
ML = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf"
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]

def _runs(txt):
    out = []
    for ch in txt:
        ml = '\u0d00' <= ch <= '\u0d7f' or ch in '\u200c\u200d'
        if ch == ' ' and out: ml = out[-1][0]
        if out and out[-1][0] == ml: out[-1][1] += ch
        else: out.append([ml, ch])
    return out

def text_img(txt, path, size, color, max_w=960):
    bold = path in (LAT_B, ML_B)
    def build(sz):
        segs = []
        for ml, t in _runs(txt):
            f = font((ML_B if bold else ML) if ml else (LAT_B if bold else LAT), sz)
            segs.append((t, f, f.getlength(t)))
        return segs
    segs = build(size)
    while sum(w for _, _, w in segs) > max_w and size > 20:
        size -= 2; segs = build(size)
    asc = max(f.getmetrics()[0] for _, f, _ in segs); desc = max(f.getmetrics()[1] for _, f, _ in segs)
    width = int(sum(w for _, _, w in segs)) + 12
    im = Image.new("RGBA", (width, asc + desc + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 6
    for t, f, w in segs:
        d.text((x, 6 + asc), t, font=f, fill=color, anchor="ls"); x += w
    return im

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

# ---------- background (precomputed gradient + animated glow + grid) ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
grad = (yy / H)[..., None]
base = (np.array(NAVY) * (1 - grad) + np.array(NAVY2) * grad).astype(np.float32)
grid = ((xx % 90 < 2) | (yy % 90 < 2)).astype(np.float32)[..., None] * 10.0

def background(t):
    cx = W * (0.5 + 0.35 * math.sin(t * 0.5)); cy = H * (0.35 + 0.15 * math.cos(t * 0.4))
    d2 = ((xx - cx) ** 2 + (yy - cy) ** 2) / (520.0 ** 2)
    glow = np.exp(-d2)[..., None] * np.array([30, 70, 120], np.float32)
    cx2 = W * (0.5 - 0.3 * math.sin(t * 0.35)); cy2 = H * 0.8
    d3 = ((xx - cx2) ** 2 + (yy - cy2) ** 2) / (420.0 ** 2)
    glow2 = np.exp(-d3)[..., None] * np.array([60, 35, 0], np.float32)
    arr = np.clip(base + glow + glow2 + grid, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")

def place(canvas, im, cx, y, alpha=1.0, dy=0):
    if alpha <= 0: return
    if alpha < 1:
        im = im.copy(); a = im.getchannel("A").point(lambda v: int(v * alpha)); im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(y + dy)))

def appear(t, start, dur=0.5, rise=60):
    p = ease((t - start) / dur); return p, (1 - p) * rise

def overlay(canvas, fn):
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); fn(ImageDraw.Draw(ov)); canvas.alpha_composite(ov)

def bar(canvas, cx, y, w, h, color, alpha):
    if w <= 1: return
    overlay(canvas, lambda d: d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + h), radius=h // 2, fill=color + (int(255 * alpha),)))

# ---------- scene assets ----------
S1 = [text_img("ലാപ്ടോപ്പ് സ്ലോ ആണോ?", ML_B, 84, WHITE),
      text_img("Laptop running slow?", LAT_B, 64, CYAN),
      text_img("ഓൺ ആകുന്നില്ലേ?", ML_B, 84, WHITE),
      text_img("Not turning on?", LAT_B, 64, CYAN)]
S2 = [text_img("KANNUR", LAT_B, 150, WHITE),
      text_img("COMPUTERS", LAT_B, 118, ACCENT),
      text_img("കമ്പ്യൂട്ടർ സർവീസ് & റിപ്പയർ", ML_B, 60, WHITE),
      text_img("Computer Service & Repair", LAT, 48, MUTED)]
SERV = [("ലാപ്ടോപ്പ് റിപ്പയർ", "Laptop Repair"),
        ("ഡെസ്ക്ടോപ്പ് സർവീസ്", "Desktop / PC Service"),
        ("ഡാറ്റ റിക്കവറി", "Data Recovery"),
        ("SSD / RAM അപ്ഗ്രേഡ്", "SSD / RAM Upgrade"),
        ("സ്ക്രീൻ മാറ്റിവയ്ക്കൽ", "Screen Replacement")]
S3_title = text_img("OUR SERVICES", LAT_B, 76, ACCENT)
S3 = [(text_img(m, ML_B, 54, WHITE, 760), text_img(e, LAT, 40, MUTED, 760)) for m, e in SERV]
S4 = [text_img("ഇപ്പോൾ തന്നെ വിളിക്കൂ!", ML_B, 70, WHITE),
      text_img("Call / WhatsApp", LAT_B, 52, CYAN),
      text_img("+91 94475 40218", LAT_B, 96, ACCENT),
      text_img("www.kannurcomputers.com", LAT_B, 54, WHITE),
      text_img("Chakkarakal Bus Stand", LAT_B, 50, WHITE),
      text_img("Near Sana Fancy, P.O. Mouwanchery, Kannur", LAT, 36, MUTED),
      text_img("KANNUR COMPUTERS", LAT_B, 60, WHITE)]

def check_icon(size=56):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, size - 1, size - 1), fill=ACCENT + (255,))
    d.line([(size * .27, size * .52), (size * .44, size * .69), (size * .74, size * .33)], fill=NAVY + (255,), width=7)
    return im
CHECK = check_icon()

def scene_alpha(t, a, b, fade=0.35):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / fade, (b - t) / fade)

def frame(t):
    c = background(t)
    # Scene 1: hook 0-3.2
    sa = scene_alpha(t, 0.0, 3.2, 0.3)
    if sa:
        ys = [620, 740, 900, 1020]
        for i, im in enumerate(S1):
            p, dy = appear(t, 0.1 + i * 0.35 + (0.25 if i >= 2 else 0))
            place(c, im, W / 2, ys[i], p * sa, dy)
    # Scene 2: brand 3.2-6.0
    sa = scene_alpha(t, 3.2, 6.0)
    if sa:
        p, _ = appear(t, 3.3, 0.6)
        s = 0.85 + 0.15 * p
        k = S2[0].resize((int(S2[0].width * s), int(S2[0].height * s)), Image.LANCZOS)
        place(c, k, W / 2, 700 - k.height / 2, p * sa)
        p2, dy2 = appear(t, 3.6)
        place(c, S2[1], W / 2, 800, p2 * sa, dy2)
        bar(c, W / 2, 960, 420 * ease((t - 3.9) / 0.5), 10, ACCENT, sa)
        p3, dy3 = appear(t, 4.1); place(c, S2[2], W / 2, 1020, p3 * sa, dy3)
        p4, dy4 = appear(t, 4.4); place(c, S2[3], W / 2, 1110, p4 * sa, dy4)
    # Scene 3: services 6.0-12.6
    sa = scene_alpha(t, 6.0, 12.6)
    if sa:
        p, dy = appear(t, 6.05); place(c, S3_title, W / 2, 330, p * sa, dy)
        bar(c, W / 2, 440, 300 * ease((t - 6.3) / 0.5), 8, ACCENT, sa)
        for i, (ml, en) in enumerate(S3):
            st = 6.6 + i * 0.7
            p = ease((t - st) / 0.5); dx = (1 - p) * -120
            if p <= 0: continue
            y = 540 + i * 220
            overlay(c, lambda d: d.rounded_rectangle((90 + dx, y - 20, 990 + dx, y + 170), radius=28,
                                fill=(255, 255, 255, int(22 * p * sa)), outline=(90, 200, 255, int(110 * p * sa)), width=2))
            place(c, CHECK, 160 + dx, y + 47, p * sa)
            place(c, ml, 230 + dx + ml.width / 2, y + 8, p * sa)
            place(c, en, 230 + dx + en.width / 2, y + 100, p * sa)
    # Scene 4: outro 12.6-18
    sa = scene_alpha(t, 12.6, DUR + 1)
    if sa:
        ys = [420, 560, 650, 840, 1080, 1160, 1460]
        starts = [12.7, 13.0, 13.25, 13.7, 14.1, 14.3, 14.8]
        for i, im in enumerate(S4):
            p, dy = appear(t, starts[i])
            if i == 2:  # pulse the phone number
                pulse = 1 + 0.04 * math.sin((t - 13.25) * 5) * (p >= 1)
                im = im.resize((int(im.width * pulse), int(im.height * pulse)), Image.LANCZOS)
                dy -= (im.height - S4[2].height) / 2
            place(c, im, W / 2, ys[i], p * sa, dy)
        ov = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        pb = ease((t - 13.5) / 0.4)
        d.rounded_rectangle((W / 2 - 380, 790, W / 2 + 380, 790 + 5), radius=2, fill=CYAN + (int(160 * pb),))
        pp = ease((t - 13.9) / 0.4)
        # map pin
        px, py = W / 2, 1000
        d.ellipse((px - 26, py - 26, px + 26, py + 26), fill=ACCENT + (int(255 * pp),))
        d.polygon([(px - 22, py + 12), (px + 22, py + 12), (px, py + 52)], fill=ACCENT + (int(255 * pp),))
        d.ellipse((px - 10, py - 10, px + 10, py + 10), fill=NAVY + (int(255 * pp),))
        c.alpha_composite(ov)
        bar(c, W / 2, 1420, 560 * ease((t - 14.8) / 0.5), 6, ACCENT, 1)
    # global fade in/out
    g = min(1.0, t / 0.3, (DUR - t) / 0.5)
    img = c.convert("RGB")
    if g < 1:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.0, g))
    return img

def main():
    n = int(DUR * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-t", str(DUR),
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", OUT],
                          stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    if len(sys.argv) > 2:  # preview stills: make_promo.py out.png t
        frame(float(sys.argv[2])).save(sys.argv[1])
    else:
        main()
