import json, math as m, os, subprocess as sp, wave, sys, asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from stories import story, TOPICS
from character import draw_character

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

# 1. Voice Synthesis (BrianNeural - Engaging Storyteller)
async def synthesize_all():
    voice = 'en-US-BrianNeural'
    for j, (text, label) in enumerate(beats):
        mp3_path = str(out / f'line_{j}.mp3')
        wav_path = str(out / f'line_{j}.wav')
        tts = edge_tts.Communicate(text, voice, pitch="+0Hz", rate="+3%")
        await tts.save(mp3_path)
        sp.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp3_path, '-ar', '24000', '-ac', '1', wav_path], check=True)

print("Synthesizing voice (BrianNeural)...")
asyncio.run(synthesize_all())

parts = []
audio = bytearray()
rate = None

for j, (text, label) in enumerate(beats):
    wav_path = str(out / f'line_{j}.wav')
    with wave.open(wav_path) as w:
        rate = w.getframerate()
        raw = w.readframes(w.getnframes())
    frames = m.ceil((len(raw) / 2 / rate + 0.3) * FPS)
    target = round((sum(parts) + frames) * rate / FPS)
    audio.extend(raw)
    audio.extend(bytes(2 * target - len(audio)))
    parts.append(frames)

with wave.open(str(out / 'voice.wav'), 'wb') as w:
    w.setparams((1, 2, rate, 0, 'NONE', ''))
    w.writeframes(audio)

# Fonts
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

brand_f = get_font(22, True)
head_f = get_font(42, True)
sub_f = get_font(33, True)
badge_f = get_font(20, True)
tag_f = get_font(24, True)

# Color Scheme
C_BG = (10, 15, 26)
C_STAGE_BG = (16, 25, 44)
C_BORDER = (45, 75, 125)
C_CYAN = (0, 240, 255)
C_GOLD = (255, 205, 75)
C_MINT = (80, 250, 180)
C_MAGENTA = (255, 65, 140)
C_WHITE = (250, 252, 255)
C_MUTED = (145, 170, 205)

def wrap(d, text, f, w):
    lines = ['']
    for word in text.split():
        s = (lines[-1] + ' ' + word).strip()
        if d.textlength(s, font=f) > w and lines[-1]:
            lines.append(word)
        else:
            lines[-1] = s
    return lines

# Background
base_bg = Image.new('RGB', (W, H), C_BG)
bd = ImageDraw.Draw(base_bg)
for x in range(30, W, 40):
    bd.line((x, 0, x, H), fill=(16, 25, 42), width=1)
for y in range(30, H, 40):
    bd.line((0, y, W, y), fill=(16, 25, 42), width=1)

# Top Brand Pill
bd.rounded_rectangle((48, 48, 225, 88), radius=20, fill=(20, 36, 68), outline=C_CYAN, width=1)
bd.text((64, 55), "THOUGHT LAB", font=brand_f, fill=C_CYAN)
bd.text((245, 55), f"•  EP #{n+1:03}", font=brand_f, fill=C_MUTED)

# Title Hook
for i, line in enumerate(wrap(bd, title, head_f, 620)):
    bd.text((48, 115 + i * 50), line, font=head_f, fill=C_WHITE)

# Main Stage Frame (Interactive 3D Arena)
STAGE_BOX = (40, 335, 680, 785)
bd.rounded_rectangle(STAGE_BOX, radius=26, fill=C_STAGE_BG, outline=C_BORDER, width=2)
# Internal Perspective Grid Floor
for i in range(-5, 6):
    bd.line((360 + i * 26, 765, 360 + i * 62, 450), fill=(26, 40, 70), width=1)
for yg in [755, 715, 665, 605, 535, 465]:
    bd.line((60, yg, 660, yg), fill=(26, 40, 70), width=1)

# 3D Math Projection Engine
def project_3d(x, y, z, cx=360, cy=555, fov=440):
    dist = z + 480
    if dist <= 10: dist = 10
    scale = fov / dist
    return int(cx + x * scale), int(cy + y * scale), scale

def draw_glow(d, pt, r, col):
    x, y = pt
    d.ellipse((x-r-6, y-r-6, x+r+6, y+r+6), fill=(*col[:3], 40))
    d.ellipse((x-r-2, y-r-2, x+r+2, y+r+2), fill=(*col[:3], 90))
    d.ellipse((x-r, y-r, x+r, y+r), fill=col)

def scene_world(d, b, t):
    p = (t % 4) / 4
    if k == 'orbit':
        sx, sy, _ = project_3d(60, 0, 0)
        draw_glow(d, (sx, sy), 20, C_GOLD)
        # Inner Orbit
        o1 = [project_3d(60 + 130 * m.cos(m.radians(deg)), 40 * m.sin(m.radians(deg)), 130 * m.sin(m.radians(deg)))[:2] for deg in range(0, 360, 10)]
        d.line(o1 + [o1[0]], fill=(0, 240, 255, 100), width=2)
        p1 = project_3d(60 + 130 * m.cos(t * 2.2), 40 * m.sin(t * 2.2), 130 * m.sin(t * 2.2))[:2]
        draw_glow(d, p1, 9, C_CYAN)
        # Outer Orbit
        o2 = [project_3d(60 + 220 * m.cos(m.radians(deg)), 75 * m.sin(m.radians(deg)), 220 * m.sin(m.radians(deg)))[:2] for deg in range(0, 360, 10)]
        d.line(o2 + [o2[0]], fill=(255, 65, 140, 90), width=2)
        p2 = project_3d(60 + 220 * m.cos(t * 0.9), 75 * m.sin(t * 0.9), 220 * m.sin(t * 0.9))[:2]
        draw_glow(d, p2, 12, C_MAGENTA)
    elif k == 'echo':
        # 3D Cliff Rock
        for cz in range(-90, 95, 20):
            c1 = project_3d(190, -75, cz)[:2]
            c2 = project_3d(190, 75, cz)[:2]
            d.line((c1[0], c1[1], c2[0], c2[1]), fill=C_GOLD, width=4)
        # Distance marker line
        d.line((190, 730, 600, 730), fill=(80, 120, 180), width=2)
        d.text((360, 705), "170 m", font=badge_f, fill=C_GOLD)
        # 3D Expanding Sonic Echo Waves traveling between character and cliff
        for offset in [0.0, 0.33, 0.66]:
            cp = (p + offset) % 1.0
            wx = -120 + 310 * (1 - abs(2 * cp - 1))
            rw = 20 + 40 * m.sin(cp * m.pi)
            w_pts = [project_3d(wx, rw * m.sin(m.radians(deg)), rw * m.cos(m.radians(deg)))[:2] for deg in range(0, 360, 20)]
            col = C_CYAN if (2*cp) < 1 else C_GOLD
            d.line(w_pts + [w_pts[0]], fill=(*col[:3], 180), width=2)
    else:
        # 3D Dynamic Science Ring
        for ri, (rad_s, col_r, spd) in enumerate([(120, C_CYAN, 1.4), (160, C_GOLD, 0.9)]):
            r_pts = [project_3d(60 + rad_s * m.cos(m.radians(deg)), rad_s * m.sin(m.radians(deg)) * m.cos(t * spd + ri), rad_s * m.sin(m.radians(deg)) * m.sin(t * spd + ri))[:2] for deg in range(0, 360, 12)]
            d.line(r_pts + [r_pts[0]], fill=col_r, width=3)

# Master Video Encoding Pipeline
print("Encoding video with character actions & 3D world...")
p = sp.Popen([
    'ffmpeg', '-loglevel', 'error', '-y',
    '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
    '-i', '-', '-i', str(out / 'voice.wav'),
    '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart',
    str(out / 'short.mp4')
], stdin=sp.PIPE)

phases = ['THE QUESTION', 'WATCH CLOSELY', 'THE MECHANISM', 'KEY TAKEAWAY']
# Character action sequence matched to story beats
beat_actions = ['clap', 'listen', 'point', 'explain']

for j, ((text, label), frames) in enumerate(zip(beats, parts)):
    card_bg = base_bg.copy()
    c_draw = ImageDraw.Draw(card_bg)

    # Top Instagram Story Progress Bar
    bar_w = (W - 96 - 30) / 4
    for idx in range(4):
        bx = 48 + idx * (bar_w + 10)
        c_draw.rounded_rectangle((bx, 28, bx + bar_w, 34), radius=3, fill=(40, 58, 90))
        if idx <= j:
            c_draw.rounded_rectangle((bx, 28, bx + bar_w, 34), radius=3, fill=C_CYAN)

    # Stage Badge
    c_draw.rounded_rectangle((60, 350, 310, 390), radius=10, fill=(20, 35, 62))
    c_draw.text((74, 358), f"PHASE 0{j+1} • {label.upper()}", font=badge_f, fill=C_CYAN)

    # Subtitle Glassmorphism Card
    c_draw.rounded_rectangle((38, 855, 682, 1150), radius=26, fill=(14, 22, 38), outline=C_BORDER, width=2)
    c_draw.text((62, 878), f"INSIGHT #{j+1}  //  {phases[j]}", font=tag_f, fill=C_GOLD)

    body_lines = wrap(c_draw, text, sub_f, 595)
    for i, l in enumerate(body_lines):
        c_draw.text((62, 928 + i * 46), l, font=sub_f, fill=C_WHITE)

    current_action = beat_actions[j % len(beat_actions)]

    for f in range(frames):
        im = card_bg.copy()
        scene_draw = ImageDraw.Draw(im)
        t_now = (sum(parts[:j]) + f) / FPS
        # 1. Draw 3D world elements
        scene_world(scene_draw, j, t_now)
        # 2. Draw Interactive Rigged Character on the stage floor
        draw_character(scene_draw, x=175, y=715, action=current_action, t=t_now, scale=1.05)
        p.stdin.write(im.tobytes())

p.stdin.close()
assert p.wait() == 0

meta = {
    'title': f'{title} | Lab {n+1:03}',
    'description': ' '.join(x[0] for x in beats) + '\n\nCharacter animated physics explainer. #Shorts #Science #Physics #Education',
    'episode': n
}
(out / 'meta.json').write_text(json.dumps(meta, indent=2))
print("Finished rendering Short with Animated Character:", meta['title'])
