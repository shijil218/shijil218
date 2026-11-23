"""Reel: 'Don't leave your laptop in a hot car' for Kannur Computers. Uses timings.json + voiceover.wav."""
import json, math, subprocess, sys
from PIL import Image, ImageDraw
import make_promo as mp
from make_promo import (W, H, WHITE, ACCENT, CYAN, MUTED, NAVY, LAT_B, LAT, ML_B, text_img, ease,
                        place, appear, bar, overlay, CHECK, scene_alpha)

FPS = 30
TM = json.load(open("timings.json"))
TOTAL = TM["total"]
SC = {s["name"]: s for s in TM["scenes"]}
RED = (255, 84, 72)
HOT = (255, 120, 40)

def T(txt, size, color=WHITE, bold=True, mw=960):
    return text_img(txt, LAT_B if bold else LAT, size, color, mw)

A = {
 "hook": [T("ലാപ്ടോപ്പ് ബാഗ്", 80), T("കാറിൽ വെച്ചുപോകാറുണ്ടോ?", 76),
          T("Leaving your laptop in the car?", 50, CYAN), T("സൂക്ഷിക്കുക!", 110, ACCENT)],
 "heat": [T("വെറും 30 മിനിറ്റിൽ", 70), T("Inside a parked car in just 30 minutes", 40, MUTED),
          T("കാറിനുള്ളിൽ 60°C വരെ!", 66, HOT)],
 "battery": [T("ബാറ്ററി വീർത്തുപൊട്ടൽ", 74), T("Swollen battery", 52, CYAN), T("തീപിടിക്കാനും സാധ്യത", 52, RED),
             T("Can even catch fire", 38, MUTED)],
 "screen": [T("ഡിസ്പ്ലേ തകരാർ", 80), T("Screen damage", 52, CYAN), T("മഞ്ഞപ്പാടുകൾ, ഡെഡ് പിക്സലുകൾ", 50, WHITE),
            T("Yellow patches & dead pixels", 38, MUTED)],
 "paste": [T("തെർമൽ പേസ്റ്റ് ഉണങ്ങും", 74), T("Thermal paste dries out", 52, CYAN),
           T("കപ്പാസിറ്ററുകൾ കേടാകാം", 52, WHITE), T("Motherboard capacitors can fail", 38, MUTED)],
 "theft": [T("മോഷണ സാധ്യത", 84), T("Theft risk", 52, CYAN), T("കാണുന്ന ബാഗ് = കള്ളന്മാർക്ക് ക്ഷണം", 48, WHITE),
           T("A visible bag invites a break-in", 38, MUTED)],
 "fix": [T("പരിഹാരം", 96, ACCENT), T("What to do", 48, CYAN),
         [(T("എപ്പോഴും കൂടെ കരുതുക", 52, WHITE, mw=740), T("Carry it with you", 36, MUTED, False, 740)),
          (T("തണലിൽ പാർക്ക് ചെയ്യുക", 52, WHITE, mw=740), T("Park in the shade", 36, MUTED, False, 740)),
          (T("ഡിക്കിയിൽ വെക്കുക", 52, WHITE, mw=740), T("Keep it in the boot, briefly", 36, MUTED, False, 740))]],
 "cta": [T("ബാറ്ററി വീർത്തോ? അമിത ചൂടോ?", 62), T("Swollen battery? Overheating?", 44, CYAN),
         T("ഒറിജിനൽ ബാറ്ററി · ഫാസ്റ്റ് ഡിസ്പ്ലേ റീപ്ലേസ്മെന്റ്", 44, WHITE),
         T("Original batteries · Fast display replacement", 34, MUTED),
         T("KANNUR COMPUTERS", 78, WHITE), T("Call / WhatsApp", 48, CYAN), T("+91 94475 40218", 92, ACCENT),
         T("www.kannurcomputers.com", 50, WHITE), T("Chakkarakal Bus Stand, Near Sana Fancy, Kannur", 36, MUTED)],
}
NUM = {k: T(str(i), 96, NAVY) for i, k in enumerate(["battery", "screen", "paste", "theft"], 1)}
_deg = {}
def deg(v):
    if v not in _deg: _deg[v] = T(f"{v}°C", 150, HOT)
    return _deg[v]

# ---------------- icons ----------------
def warn_icon(d, cx, cy, s, a, col=ACCENT):
    d.polygon([(cx, cy - s), (cx + s * 1.1, cy + s * .8), (cx - s * 1.1, cy + s * .8)], fill=col + (a,))
    d.rounded_rectangle((cx - s * .09, cy - s * .45, cx + s * .09, cy + s * .25), radius=6, fill=NAVY + (a,))
    d.ellipse((cx - s * .1, cy + s * .4, cx + s * .1, cy + s * .6), fill=NAVY + (a,))

def car_icon(d, cx, cy, s, a, t):
    body = WHITE + (a,)
    d.rounded_rectangle((cx - s, cy - s * .15, cx + s, cy + s * .35), radius=int(s * .15), fill=body)
    d.polygon([(cx - s * .6, cy - s * .15), (cx - s * .35, cy - s * .55), (cx + s * .4, cy - s * .55), (cx + s * .65, cy - s * .15)], fill=body)
    d.polygon([(cx - s * .5, cy - s * .18), (cx - s * .3, cy - s * .47), (cx - s * .02, cy - s * .47), (cx - s * .02, cy - s * .18)], fill=(40, 70, 120, a))
    d.polygon([(cx + s * .05, cy - s * .18), (cx + s * .05, cy - s * .47), (cx + s * .36, cy - s * .47), (cx + s * .55, cy - s * .18)], fill=(40, 70, 120, a))
    # laptop bag on the back seat
    d.rounded_rectangle((cx + s * .12, cy - s * .36, cx + s * .34, cy - s * .2), radius=4, fill=ACCENT + (a,))
    for wx in (-s * .55, s * .55):
        d.ellipse((cx + wx - s * .2, cy + s * .2, cx + wx + s * .2, cy + s * .6), fill=(20, 20, 30, a))
        d.ellipse((cx + wx - s * .09, cy + s * .31, cx + wx + s * .09, cy + s * .49), fill=(150, 160, 180, a))

def sun_icon(d, cx, cy, r, a, t):
    for i in range(12):
        ang = i * math.pi / 6 + t * 0.6
        d.line([(cx + math.cos(ang) * r * 1.3, cy + math.sin(ang) * r * 1.3),
                (cx + math.cos(ang) * r * 1.75, cy + math.sin(ang) * r * 1.75)], fill=(255, 200, 60, a), width=10)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 190, 40, a))

def thermo(d, cx, cy, h, level, a):
    d.rounded_rectangle((cx - 34, cy - h, cx + 34, cy), radius=34, fill=(255, 255, 255, int(a * .9)))
    d.ellipse((cx - 62, cy - 30, cx + 62, cy + 94), fill=(255, 255, 255, int(a * .9)))
    fh = (h - 40) * level
    col = tuple(int(c1 + (c2 - c1) * level) for c1, c2 in zip((255, 180, 40), RED))
    d.rounded_rectangle((cx - 18, cy - 20 - fh, cx + 18, cy + 10), radius=18, fill=col + (a,))
    d.ellipse((cx - 46, cy - 14, cx + 46, cy + 78), fill=col + (a,))
    for i in range(1, 6):
        y = cy - 20 - (h - 40) * i / 6
        d.line([(cx + 40, y), (cx + 62, y)], fill=(255, 255, 255, a), width=5)

def battery_icon(d, cx, cy, a, swell):
    w, h = 300, 170
    d.rounded_rectangle((cx + w / 2, cy - 30, cx + w / 2 + 26, cy + 30), radius=8, fill=WHITE + (a,))
    bulge = 60 * swell
    if bulge > 2:
        d.ellipse((cx - w / 2 + 10, cy - h / 2 - bulge, cx + w / 2 - 10, cy + h / 2 + bulge), fill=(30, 50, 90, a),
                  outline=(RED if swell > .5 else WHITE) + (a,), width=12)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=22, outline=WHITE + (a,), width=12,
                        fill=(30, 50, 90, a))
    d.rounded_rectangle((cx - w / 2 + 24, cy - h / 2 + 24, cx - w / 2 + 24 + (w - 48) * (1 - swell * .7), cy + h / 2 - 24), radius=10,
                        fill=((80, 220, 120) if swell < .5 else RED) + (a,))
    if swell > .3:
        k = (swell - .3) / .7
        for i, (dx, dy) in enumerate([(-170, -150), (0, -190), (170, -150)]):
            d.line([(cx + dx * .6, cy + dy * .6), (cx + dx * (.6 + .25 * k), cy + dy * (.6 + .25 * k))], fill=HOT + (int(a * k),), width=10)

def screen_icon(d, cx, cy, a, t, p):
    w, h = 420, 270
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=16, fill=(40, 60, 100, a), outline=WHITE + (a,), width=10)
    d.polygon([(cx - w / 2 - 40, cy + h / 2 + 10), (cx + w / 2 + 40, cy + h / 2 + 10), (cx + w / 2 + 70, cy + h / 2 + 46), (cx - w / 2 - 70, cy + h / 2 + 46)], fill=WHITE + (a,))
    k = ease(p)
    for (x, y, r) in [(-90, -40, 70), (100, 50, 55), (20, -70, 40)]:
        d.ellipse((cx + x - r * k, cy + y - r * k * .7, cx + x + r * k, cy + y + r * k * .7), fill=(230, 200, 60, int(a * .55)))
    for i, (x, y) in enumerate([(-150, 80), (140, -80), (-30, 30), (60, -20), (-120, -90)]):
        if k > i / 6:
            d.rectangle((cx + x - 8, cy + y - 8, cx + x + 8, cy + y + 8), fill=(0, 0, 0, a))

def chip_icon(d, cx, cy, a, t, p):
    s = 140
    for i in range(5):
        o = -s + 25 + i * (2 * s - 50) / 4
        for (x1, y1, x2, y2) in [(cx + o - 8, cy - s - 40, cx + o + 8, cy - s), (cx + o - 8, cy + s, cx + o + 8, cy + s + 40),
                                 (cx - s - 40, cy + o - 8, cx - s, cy + o + 8), (cx + s, cy + o - 8, cx + s + 40, cy + o + 8)]:
            d.rectangle((x1, y1, x2, y2), fill=(200, 210, 225, a))
    d.rounded_rectangle((cx - s, cy - s, cx + s, cy + s), radius=20, fill=(35, 45, 60, a), outline=WHITE + (a,), width=6)
    k = ease(p)
    # paste: from grey-white blob to dry cracked brown
    col = tuple(int(c1 + (c2 - c1) * k) for c1, c2 in zip((225, 225, 230), (150, 105, 60)))
    d.ellipse((cx - 85, cy - 85, cx + 85, cy + 85), fill=col + (a,))
    if k > .4:
        q = int(a * (k - .4) / .6)
        for pts in [[(cx - 60, cy - 20), (cx - 10, cy + 5), (cx + 30, cy - 30), (cx + 70, cy - 10)],
                    [(cx - 40, cy + 50), (cx, cy + 20), (cx + 50, cy + 45)], [(cx - 10, cy + 5), (cx - 5, cy + 60)]]:
            d.line(pts, fill=(70, 40, 20, q), width=6)
    # heat waves
    for i in range(3):
        x = cx - 120 + i * 120; ph = t * 4 + i
        pts = [(x + 14 * math.sin(ph + j * .9), cy - s - 70 - j * 18) for j in range(6)]
        d.line(pts, fill=HOT + (int(a * k),), width=8)

def lock_icon(d, cx, cy, a, t, p):
    car_icon(d, cx, cy + 20, 330, a, t)
    k = ease(p)
    if k > 0:  # glass crack on the rear window
        ox, oy = cx + 70, cy - 110
        for ang in range(0, 360, 50):
            r = 70 * k
            d.line([(ox, oy), (ox + math.cos(math.radians(ang)) * r, oy + math.sin(math.radians(ang)) * r)], fill=RED + (a,), width=6)
    warn_icon(d, cx, cy - 300, 70, int(a * k), RED)

ICONS = {"battery": lambda d, t, s, a: battery_icon(d, W / 2, 760, a, ease((t - s - .6) / 3.0)),
         "screen": lambda d, t, s, a: screen_icon(d, W / 2, 740, a, t, (t - s - .5) / 2.5),
         "paste": lambda d, t, s, a: chip_icon(d, W / 2, 780, a, t, (t - s - .5) / 3.0),
         "theft": lambda d, t, s, a: lock_icon(d, W / 2, 800, a, t, (t - s - .6) / 1.0)}

def bg_tint(c, t, amt, col):
    if amt <= 0: return
    overlay(c, lambda d: d.rectangle((0, 0, W, H), fill=col + (int(amt),)))

def frame(t):
    c = mp.background(t)
    s = SC["hook"]; sa = scene_alpha(t, 0, s["end"], .3)
    if sa:
        p, dy = appear(t, .1); ov = Image.new("RGBA", c.size); d = ImageDraw.Draw(ov)
        car_icon(d, W / 2, 470 + dy, 260, int(255 * p * sa), t)
        pw = ease((t - 2.2) / .5); warn_icon(d, W / 2 + 250, 330, 60, int(255 * pw * sa))
        c.alpha_composite(ov)
        for i, (im, y, st) in enumerate(zip(A["hook"], [760, 870, 990, 1130], [.4, .8, 1.3, 4.6])):
            p, dy = appear(t, st); place(c, im, W / 2, y, p * sa, dy)
    s = SC["heat"]; sa = scene_alpha(t, s["start"], s["end"])
    if sa:
        heat = ease((t - s["start"]) / s["voice"])
        bg_tint(c, t, 70 * heat * sa, (200, 60, 10))
        ov = Image.new("RGBA", c.size); d = ImageDraw.Draw(ov)
        sun_icon(d, 820, 360, 70, int(255 * sa), t)
        thermo(d, 300, 1040, 560, heat, int(255 * sa))
        car_icon(d, 330, 340, 170, int(200 * sa), t)
        c.alpha_composite(ov)
        place(c, deg(int(30 + 30 * heat)), 700, 700, sa)
        for im, y, st in zip(A["heat"], [1220, 1320, 1420], [s["start"] + .3, s["start"] + .7, s["start"] + 3.5]):
            p, dy = appear(t, st); place(c, im, W / 2, y, p * sa, dy)
    for key in ["battery", "screen", "paste", "theft"]:
        s = SC[key]; sa = scene_alpha(t, s["start"], s["end"])
        if not sa: continue
        st = s["start"]
        p, dy = appear(t, st + .05)
        overlay(c, lambda d: d.ellipse((W / 2 - 75, 250 + dy, W / 2 + 75, 400 + dy), fill=ACCENT + (int(255 * p * sa),)))
        place(c, NUM[key], W / 2, 262 + dy, p * sa)
        ov = Image.new("RGBA", c.size); d = ImageDraw.Draw(ov)
        pi, _ = appear(t, st + .2); ICONS[key](d, t, st, int(255 * pi * sa)); c.alpha_composite(ov)
        ims = A[key]
        for im, y, dl in zip(ims, [1100, 1210, 1320, 1400], [.4, .7, 1.6, 1.9]):
            p, dy = appear(t, st + dl); place(c, im, W / 2, y, p * sa, dy)
    s = SC["fix"]; sa = scene_alpha(t, s["start"], s["end"])
    if sa:
        st = s["start"]; ims = A["fix"]
        p, dy = appear(t, st + .05); place(c, ims[0], W / 2, 330, p * sa, dy)
        p, dy = appear(t, st + .3); place(c, ims[1], W / 2, 470, p * sa, dy)
        for i, (ml, en) in enumerate(ims[2]):
            p = ease((t - st - [1.0, 3.6, 5.6][i]) / .5)
            if p <= 0: continue
            dx = (1 - p) * -120; y = 640 + i * 240
            overlay(c, lambda d: d.rounded_rectangle((80 + dx, y - 20, 1000 + dx, y + 180), radius=28,
                    fill=(255, 255, 255, int(22 * p * sa)), outline=(90, 200, 255, int(110 * p * sa)), width=2))
            place(c, CHECK, 150 + dx, y + 52, p * sa)
            place(c, ml, 220 + dx + ml.width / 2, y + 10, p * sa)
            place(c, en, 220 + dx + en.width / 2, y + 104, p * sa)
    s = SC["cta"]; sa = scene_alpha(t, s["start"], TOTAL + 1)
    if sa:
        st = s["start"]; ims = A["cta"]
        ys = [300, 400, 520, 590, 760, 900, 970, 1140, 1240]
        dl = [.1, .4, 3.6, 3.8, 6.4, 7.6, 7.9, 8.6, 9.0]
        for i, im in enumerate(ims):
            p, dy = appear(t, st + dl[i])
            if i == 6 and p >= 1:
                k = 1 + .04 * math.sin((t - st) * 5)
                im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS); dy -= (im.height - ims[6].height) / 2
            place(c, im, W / 2, ys[i], p * sa, dy)
        bar(c, W / 2, 690, 520 * ease((t - st - 6.2) / .5), 8, ACCENT, sa)
        bar(c, W / 2, 1110, 600 * ease((t - st - 8.4) / .5), 5, CYAN, sa)
    g = min(1.0, t / .3, (TOTAL - t) / .5)
    img = c.convert("RGB")
    if g < 1: img = Image.blend(Image.new("RGB", (W, H)), img, max(0.0, g))
    return img

def main(out):
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", "voiceover.wav", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    if len(sys.argv) > 2: frame(float(sys.argv[2])).save(sys.argv[1])
    else: main(sys.argv[1])
