import json, math as m, os, subprocess as sp, wave, sys, asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from stories import story, TOPICS

W, H, FPS = 720, 1280, 24
cfg = json.loads(Path('studio.json').read_text())
topics = cfg['topics']
assert topics and all(k in TOPICS for k in topics)

n = int(sys.argv[1]) if len(sys.argv) > 1 else 0
k = topics[n % len(topics)]
v = n // len(topics)
title, beats = story(k, v)

out = Path('output')
out.mkdir(exist_ok=True)

# 1. Voice Synthesis (Deep Human Male Voice)
async def synthesize_all():
    voice = 'en-US-GuyNeural' # Deep documentary narrator
    for j, (text, label) in enumerate(beats):
        mp3_path = str(out / f'line_{j}.mp3')
        wav_path = str(out / f'line_{j}.wav')
        tts = edge_tts.Communicate(text, voice, pitch="-8Hz", rate="-3%")
        await tts.save(mp3_path)
        sp.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp3_path, '-ar', '24000', '-ac', '1', wav_path], check=True)

print("Synthesizing voice...")
asyncio.run(synthesize_all())

parts = []
audio = bytearray()
rate = None

for j, (text, label) in enumerate(beats):
    wav_path = str(out / f'line_{j}.wav')
    with wave.open(wav_path) as w:
        rate = w.getframerate()
        raw = w.readframes(w.getnframes())
    frames = m.ceil((len(raw) / 2 / rate + 0.35) * FPS)
    target = round((sum(parts) + frames) * rate / FPS)
    audio.extend(raw)
    audio.extend(bytes(2 * target - len(audio)))
    parts.append(frames)

with wave.open(str(out / 'voice.wav'), 'wb') as w:
    w.setparams((1, 2, rate, 0, 'NONE', ''))
    w.writeframes(audio)

# Typography & Colors
def get_font(sz, bold=False):
    candidates = [
        f'/usr/share/fonts/truetype/dejavu/DejaVuSans{"-Bold" if bold else ""}.ttf',
        f'/usr/share/fonts/truetype/liberation/LiberationSans-{"Bold" if bold else "Regular"}.ttf',
        f'/usr/share/fonts/dejavu/DejaVuSans{"-Bold" if bold else ""}.ttf'
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

badge_f = get_font(20, True)
head_f = get_font(42, True)
body_f = get_font(32, True)
tag_f = get_font(22, True)
math_f = get_font(26, True)

C_BG = (12, 18, 32)
C_CARD_BG = (20, 30, 52)
C_CARD_BORDER = (45, 75, 125)
C_CYAN = (0, 240, 255)
C_MINT = (80, 250, 180)
C_GOLD = (255, 200, 80)
C_MAGENTA = (255, 60, 140)
C_TEXT_WHITE = (245, 248, 255)
C_TEXT_MUTED = (145, 170, 205)

def wrap(d, text, f, w):
    lines = ['']
    for word in text.split():
        s = (lines[-1] + ' ' + word).strip()
        if d.textlength(s, font=f) > w and lines[-1]:
            lines.append(word)
        else:
            lines[-1] = s
    return lines

# Background Pre-render
base_bg = Image.new('RGB', (W, H), C_BG)
bd = ImageDraw.Draw(base_bg)
for x in range(40, W, 48):
    bd.line((x, 0, x, H), fill=(18, 28, 48), width=1)
for y in range(40, H, 48):
    bd.line((0, y, W, y), fill=(18, 28, 48), width=1)

# Header
bd.rounded_rectangle((48, 50, 215, 88), radius=18, fill=(25, 45, 80), outline=C_CYAN, width=1)
bd.text((64, 57), "THOUGHT LAB", font=badge_f, fill=C_CYAN)
bd.text((235, 57), f"•  EPISODE #{n+1:03}", font=tag_f, fill=C_TEXT_MUTED)

for i, line in enumerate(wrap(bd, title, head_f, 620)):
    bd.text((48, 118 + i * 50), line, font=head_f, fill=C_TEXT_WHITE)

# 3D Center Stage (Card)
STAGE_RECT = (40, 345, 680, 790)
bd.rounded_rectangle(STAGE_RECT, radius=28, fill=C_CARD_BG, outline=C_CARD_BORDER, width=2)
# Internal 3D Perspective Grid
for i in range(-5, 6):
    bd.line((360 + i * 28, 770, 360 + i * 65, 460), fill=(28, 44, 75), width=1)
for y_g in [760, 720, 670, 610, 540, 470]:
    bd.line((60, y_g, 660, y_g), fill=(28, 44, 75), width=1)

# Real 3D Perspective Projection Engine (True 3D Math without heavy Blender)
def project_3d(x, y, z, cx=360, cy=560, fov=450):
    # Camera distance offset
    dist = z + 500
    if dist <= 10: dist = 10
    scale = fov / dist
    sx = int(cx + x * scale)
    sy = int(cy + y * scale)
    return sx, sy, scale

def scene_3d(d, b, t):
    p = (t % 4) / 4
    
    if k == 'orbit':
        # 3D Star & Multi-Planet Orbit System
        sx, sy, ss = project_3d(0, 0, 0)
        # 3D Sun Glow
        d.ellipse((sx-28, sy-28, sx+28, sy+28), fill=(255, 180, 30, 80))
        d.ellipse((sx-18, sy-18, sx+18, sy+18), fill=C_GOLD)
        
        # 3D Orbit 1 (Cyan Planet)
        orbit1_pts = []
        for deg in range(0, 360, 10):
            rad = m.radians(deg)
            # Tilt orbit in 3D space
            ox = 140 * m.cos(rad)
            oy = 50 * m.sin(rad)
            oz = 140 * m.sin(rad)
            px, py, _ = project_3d(ox, oy, oz)
            orbit1_pts.append((px, py))
        d.line(orbit1_pts + [orbit1_pts[0]], fill=(0, 240, 255, 90), width=2)
        
        # Planet 1 position
        a1 = t * 2.2
        p1x, p1y, s1 = project_3d(140 * m.cos(a1), 50 * m.sin(a1), 140 * m.sin(a1))
        r1 = max(4, int(12 * s1))
        d.ellipse((p1x-r1-4, p1y-r1-4, p1x+r1+4, p1y+r1+4), fill=(0, 240, 255, 100))
        d.ellipse((p1x-r1, p1y-r1, p1x+r1, p1y+r1), fill=C_CYAN)
        
        # 3D Orbit 2 (Magenta Outer Planet)
        orbit2_pts = []
        for deg in range(0, 360, 10):
            rad = m.radians(deg)
            ox = 250 * m.cos(rad)
            oy = 90 * m.sin(rad)
            oz = 250 * m.sin(rad)
            px, py, _ = project_3d(ox, oy, oz)
            orbit2_pts.append((px, py))
        d.line(orbit2_pts + [orbit2_pts[0]], fill=(255, 60, 140, 90), width=2)
        
        a2 = t * 0.9
        p2x, p2y, s2 = project_3d(250 * m.cos(a2), 90 * m.sin(a2), 250 * m.sin(a2))
        r2 = max(4, int(15 * s2))
        d.ellipse((p2x-r2-4, p2y-r2-4, p2x+r2+4, p2y+r2+4), fill=(255, 60, 140, 100))
        d.ellipse((p2x-r2, p2y-r2, p2x+r2, p2y+r2), fill=C_MAGENTA)
        
    elif k == 'echo':
        # 3D Sound Radar & Acoustic Cliff
        # 3D Cliff
        for cz in range(-120, 120, 20):
            cx1, cy1, _ = project_3d(180, -90, cz)
            cx2, cy2, _ = project_3d(180, 90, cz)
            d.line((cx1, cy1, cx2, cy2), fill=C_GOLD, width=4)
        
        # 3D Source
        ex, ey, _ = project_3d(-180, 0, 0)
        d.ellipse((ex-15, ey-15, ex+15, ey+15), fill=C_CYAN)
        
        # 3D Volumetric Echo Waves
        for offset in [0.0, 0.33, 0.66]:
            cp = (p + offset) % 1.0
            wx = -180 + 360 * (1 - abs(2 * cp - 1))
            w_pts = []
            for deg in range(0, 360, 20):
                rad = m.radians(deg)
                r_3d = 30 + 50 * m.sin(cp * m.pi)
                ry = r_3d * m.sin(rad)
                rz = r_3d * m.cos(rad)
                px, py, _ = project_3d(wx, ry, rz)
                w_pts.append((px, py))
            col = C_CYAN if (2*cp) < 1 else C_GOLD
            d.line(w_pts + [w_pts[0]], fill=(*col[:3], 160), width=2)
            
    else:
        # 3D Rotating Gyroscopic Physics Ring
        for ring_idx, (r_sz, c_col, speed) in enumerate([(140, C_CYAN, 1.4), (190, C_GOLD, 0.9), (80, C_MINT, 2.0)]):
            ring_pts = []
            for deg in range(0, 360, 12):
                rad = m.radians(deg)
                # 3D rotation matrix
                rx = r_sz * m.cos(rad)
                ry = r_sz * m.sin(rad) * m.cos(t * speed + ring_idx)
                rz = r_sz * m.sin(rad) * m.sin(t * speed + ring_idx)
                px, py, _ = project_3d(rx, ry, rz)
                ring_pts.append((px, py))
            d.line(ring_pts + [ring_pts[0]], fill=c_col, width=3)
            # 3D Nodes
            nodex, nodey, _ = ring_pts[int((t * 10) % len(ring_pts))]
            d.ellipse((nodex-6, nodey-6, nodex+6, nodey+6), fill=C_TEXT_WHITE)

# 4. Master Composite Animation Pipeline
print("Encoding video...")
p = sp.Popen([
    'ffmpeg', '-loglevel', 'error', '-y',
    '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
    '-i', '-', '-i', str(out / 'voice.wav'),
    '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart',
    str(out / 'short.mp4')
], stdin=sp.PIPE)

step_names = ['OBSERVATION', 'ANALYSIS', 'THE MECHANISM', 'KEY TAKEAWAY']

for j, ((text, label), frames) in enumerate(zip(beats, parts)):
    card_bg = base_bg.copy()
    c_draw = ImageDraw.Draw(card_bg)

    # Stage Badge
    c_draw.rounded_rectangle((60, 360, 310, 400), radius=10, fill=(20, 35, 65))
    c_draw.text((74, 368), f"STAGE 0{j+1} • {label.upper()}", font=tag_f, fill=C_CYAN)

    # Bottom Subtitle Card
    c_draw.rounded_rectangle((38, 860, 682, 1150), radius=26, fill=(14, 22, 40), outline=C_CARD_BORDER, width=2)
    c_draw.text((62, 880), f"PHASE {j+1}: {step_names[j]}", font=tag_f, fill=C_GOLD)

    body_lines = wrap(c_draw, text, body_f, 600)
    for i, l in enumerate(body_lines):
        c_draw.text((62, 925 + i * 44), l, font=body_f, fill=C_TEXT_WHITE)

    # Instagram Progress Bar
    bar_w = (W - 96 - 30) / 4
    for idx in range(4):
        bx = 48 + idx * (bar_w + 10)
        c_draw.rounded_rectangle((bx, 28, bx + bar_w, 34), radius=3, fill=(40, 60, 95))
        if idx <= j:
            c_draw.rounded_rectangle((bx, 28, bx + bar_w, 34), radius=3, fill=C_CYAN)

    for f in range(frames):
        im = card_bg.copy()
        scene_draw = ImageDraw.Draw(im)
        scene_3d(scene_draw, j, (sum(parts[:j]) + f) / FPS)
        p.stdin.write(im.tobytes())

p.stdin.close()
assert p.wait() == 0

meta = {
    'title': f'{title} | Lab {n+1:03}',
    'description': ' '.join(x[0] for x in beats) + '\n\nOriginal 3D perspective explainer. #Shorts #Science #Physics',
    'episode': n
}
(out / 'meta.json').write_text(json.dumps(meta, indent=2))
print("Finished rendering Short:", meta['title'])
