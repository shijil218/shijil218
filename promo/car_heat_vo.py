"""Generate the Malayalam voiceover per scene with edge-tts, write timings.json and voiceover.wav."""
import json, os, subprocess, sys

VOICE = sys.argv[1] if len(sys.argv) > 1 else "ml-IN-MidhunNeural"
GAP = 0.45
SCENES = [
    ("hook", "ഓഫീസിലോ ഷോപ്പിംഗിനോ പോകുമ്പോൾ, ലാപ്ടോപ്പ് ബാഗ് കാറിന്റെ പിൻസീറ്റിൽ വെച്ചുപോകാറുണ്ടോ? എങ്കിൽ സൂക്ഷിക്കുക!"),
    ("heat", "കേരളത്തിലെ കടുത്ത ചൂടിൽ, വെയിലത്ത് പാർക്ക് ചെയ്ത കാറിനുള്ളിൽ, വെറും മുപ്പത് മിനിറ്റ് കൊണ്ട് താപനില അറുപത് ഡിഗ്രി വരെ ഉയരാം."),
    ("battery", "ഒന്ന്. ബാറ്ററി വീർത്തുപൊട്ടാം. ചിലപ്പോൾ തീപിടിക്കാനും സാധ്യതയുണ്ട്."),
    ("screen", "രണ്ട്. സ്ക്രീനിൽ മഞ്ഞപ്പാടുകളും ഡെഡ് പിക്സലുകളും വരാം."),
    ("paste", "മൂന്ന്. തെർമൽ പേസ്റ്റ് ഉണങ്ങി, മദർബോർഡിലെ കപ്പാസിറ്ററുകൾ കേടാകാം."),
    ("theft", "നാല്. സീറ്റിൽ കാണുന്ന ബാഗ്, മോഷ്ടാക്കളെ ആകർഷിക്കും."),
    ("fix", "പരിഹാരം. ലാപ്ടോപ്പ് എപ്പോഴും കൂടെ കരുതുക. കാറിൽ വെക്കേണ്ടി വന്നാൽ, തണലിൽ പാർക്ക് ചെയ്ത്, ഡിക്കിയിൽ വെക്കുക."),
    ("cta", "ബാറ്ററി വീർക്കുകയോ, ലാപ്ടോപ്പ് അമിതമായി ചൂടാവുകയോ ചെയ്യുന്നുണ്ടോ? ഒറിജിനൽ ബാറ്ററികൾക്കും, ഡിസ്പ്ലേ റീപ്ലേസ്മെന്റിനും, കണ്ണൂർ കമ്പ്യൂട്ടേഴ്സിലേക്ക് വരൂ. വിളിക്കൂ: ഒമ്പത് നാല് നാല് ഏഴ്, അഞ്ച് നാല് പൂജ്യം, രണ്ട് ഒന്ന് എട്ട്."),
]
os.makedirs("vo", exist_ok=True)
env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt")
proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
timings, t = [], 0.6  # short lead-in before first line
parts = []
for name, text in SCENES:
    mp3 = f"vo/{name}.mp3"
    if not os.path.exists(mp3) or os.path.getsize(mp3) == 0:
        cmd = ["edge-tts", "--voice", VOICE, "--rate=+4%", "--text", text, "--write-media", mp3]
        if proxy: cmd[1:1] = ["--proxy", proxy]
        subprocess.run(cmd, check=True, env=env)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", mp3]))
    timings.append({"name": name, "start": round(t, 3), "voice": round(d, 3)})
    parts.append((mp3, t))
    t += d + GAP
total = t + 2.0  # hold the outro a little
for s, nxt in zip(timings, timings[1:] + [{"start": total}]):
    s["end"] = round(nxt["start"], 3)
json.dump({"total": round(total, 3), "scenes": timings}, open("timings.json", "w"), indent=1)

inputs, filt = [], []
for i, (mp3, st) in enumerate(parts):
    inputs += ["-i", mp3]
    filt.append(f"[{i}:a]aresample=44100,adelay={int(st*1000)}|{int(st*1000)}[a{i}]")
filt.append("".join(f"[a{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,apad,atrim=0:{total},loudnorm=I=-16:TP=-1.5[out]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ac", "2", "-ar", "44100", "voiceover.wav"], check=True)
print(json.dumps(timings, ensure_ascii=False, indent=1), "total", total)
