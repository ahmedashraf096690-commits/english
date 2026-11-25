import os, re, math, struct, wave, zlib, glob, sys

# 1) chime sound (synthesized, no copyright)
os.makedirs("android/app/src/main/res/raw", exist_ok=True)
sr = 22050
notes = [(784, 0.00), (988, 0.22), (1175, 0.44), (1568, 0.70), (1175, 1.10), (1568, 1.35)]
total = 2.4
data = [0.0] * int(sr * total)
for f, t0 in notes:
    for i in range(int(sr * 0.9)):
        k = int(sr * t0) + i
        if k >= len(data):
            break
        t = i / sr
        env = min(1.0, t / 0.01) * math.exp(-3.2 * t)
        data[k] += 0.45 * env * (math.sin(2 * math.pi * f * t) + 0.3 * math.sin(2 * math.pi * 2 * f * t))
m = max(abs(x) for x in data) or 1
with wave.open("android/app/src/main/res/raw/chime.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x / m)) * 30000)) for x in data))

# 2) icons: green square with a white E
def png(path, size, bg, fg_only=False, round_=False):
    rows = []
    c = size / 2
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            u, v = x / size, y / size
            inside = True
            if round_:
                inside = (x - c) ** 2 + (y - c) ** 2 <= (size * 0.5) ** 2
            a = 255 if inside else 0
            col = bg if not fg_only else (0, 0, 0)
            alpha = a if not fg_only else 0
            # E glyph
            e = (0.34 <= u <= 0.44 and 0.28 <= v <= 0.72) or (0.34 <= u <= 0.68 and (0.28 <= v <= 0.38 or 0.46 <= v <= 0.54 or 0.62 <= v <= 0.72))
            if e and inside:
                col = (255, 255, 255); alpha = 255
            row += bytes([col[0], col[1], col[2], alpha])
        rows.append(bytes(row))
    raw = b"".join(rows)
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

green = (31, 111, 92)
for p in glob.glob("android/app/src/main/res/mipmap-*/ic_launcher*.png"):
    with open(p, "rb") as f:
        hd = f.read(24)
    size = struct.unpack(">I", hd[16:20])[0]
    name = os.path.basename(p)
    if "foreground" in name:
        # adaptive foreground: E on transparent, scaled into safe zone is already handled by margins
        png(p, size, green, fg_only=True)
    else:
        png(p, size, green, round_=("round" in name))
bgx = "android/app/src/main/res/values/ic_launcher_background.xml"
if os.path.exists(bgx):
    open(bgx, "w").write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#1F6F5C</color>\n</resources>\n')
# notification small icon
os.makedirs("android/app/src/main/res/drawable", exist_ok=True)
open("android/app/src/main/res/drawable/ic_stat_icon.xml", "w").write('<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24"><path android:fillColor="#FFFFFF" android:pathData="M12,22c1.1,0 2,-0.9 2,-2h-4c0,1.1 0.9,2 2,2zM18,16v-5c0,-3.07 -1.63,-5.64 -4.5,-6.32V4c0,-0.83 -0.67,-1.5 -1.5,-1.5s-1.5,0.67 -1.5,1.5v0.68C7.64,5.36 6,7.92 6,11v5l-2,2v1h16v-1l-2,-2z"/></vector>\n')

# 3) manifest permissions
mp = "android/app/src/main/AndroidManifest.xml"
s = open(mp, encoding="utf8").read()
perms = ["POST_NOTIFICATIONS", "SCHEDULE_EXACT_ALARM", "USE_EXACT_ALARM", "VIBRATE", "RECEIVE_BOOT_COMPLETED", "WAKE_LOCK", "RECORD_AUDIO", "MODIFY_AUDIO_SETTINGS"]
add = "".join('    <uses-permission android:name="android.permission.%s" />\n' % p for p in perms if p not in s)
s = s.replace("</manifest>", add + "</manifest>")
open(mp, "w", encoding="utf8").write(s)

# 4) release signing from the stable keystore
gp = "android/app/build.gradle"
g = open(gp, encoding="utf8").read()
sc = "signingConfigs {\n        release {\n            storeFile file('../../release.jks')\n            storePassword System.getenv('KS_PASS')\n            keyAlias 'english'\n            keyPassword System.getenv('KS_PASS')\n        }\n    }\n    buildTypes {"
g = g.replace("buildTypes {", sc, 1)
g = g.replace("minifyEnabled false", "minifyEnabled false\n            signingConfig signingConfigs.release", 1)
open(gp, "w", encoding="utf8").write(g)
print("prepared")
