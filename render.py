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

total_frames = sum(parts)

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
counter_f = get_font(36, True)
unit_f = get_font(20, True)
label_f = get_font(22, True)
sub_f = get_font(34, True)
tag_f = get_font(24, True)

# Color Scheme (Deep Cinematic)
C_CYAN = (0, 240, 255)
C_GOLD = (255, 205, 75)
C_MINT = (80, 250, 180)
C_RED = (255, 65, 85)
C_WHITE = (255, 255, 255)
C_MUTED = (145, 175, 215)

def wrap(d, text, f, w):
    lines = ['']
    for word in text.split():
        s = (lines[-1] + ' ' + word).strip()
        if d.textlength(s, font=f) > w and lines[-1]:
            lines.append(word)
        else:
            lines[-1] = s
    return lines

# Target numerical distance/metric for dynamic running counter
if k == 'echo':
    target_metric = 170 + 5 * v
    metric_unit = "METERS (DISTANCE)"
elif k == 'orbit':
    target_metric = (2 + v) * 150
    metric_unit = "M KM (ORBIT RADIUS)"
elif k == 'fall':
    target_metric = int(0.5 * 9.81 * (2 + v)**2)
    metric_unit = "METERS (FREE FALL)"
else:
    target_metric = 340
    metric_unit = "M/S (ACOUSTIC VELOCITY)"

# 2. Master Frame-by-Frame Generation with Cinematic Shaders & Dynamic Telemetry
print(f"Generating Cinematic Telemetry & 3D Visual Frames ({total_frames} frames)...")
p = sp.Popen([
    'ffmpeg', '-loglevel', 'error', '-y',
    '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
    '-i', '-', '-i', str(out / 'voice.wav'),
    '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '19',
    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart',
    str(out / 'short.mp4')
], stdin=sp.PIPE)

phases = ['INITIAL DISCOVERY', 'TELEMETRY TRACKING', 'CORE MECHANISM', 'FINAL PROOF']

for j, ((text, label), frames) in enumerate(zip(beats, parts)):
    for f in range(frames):
        global_f = sum(parts[:j]) + f
        t = global_f / FPS
        progress = global_f / total_frames

        # A. Procedural Cinematic Deep Abyss Background
        # Dark moody blue gradient deepening with progress
        im = Image.new('RGB', (W, H))
        idraw = ImageDraw.Draw(im)
        
        # Depth color shift: Deep Navy -> Total Abyss Black
        dark_factor = max(0.0, 1.0 - progress * 0.7)
        top_c = (int(8 * dark_factor), int(22 * dark_factor), int(45 * dark_factor))
        bot_c = (int(3 * dark_factor), int(7 * dark_factor), int(16 * dark_factor))
        
        # Render fast depth gradient in bands
        for band in range(0, H, 16):
            b_ratio = band / H
            br = int(top_c[0] * (1 - b_ratio) + bot_c[0] * b_ratio)
            bg = int(top_c[1] * (1 - b_ratio) + bot_c[1] * b_ratio)
            bb = int(top_c[2] * (1 - b_ratio) + bot_c[2] * b_ratio)
            idraw.rectangle([(0, band), (W, band + 16)], fill=(br, bg, bb))

        # Floating Volumetric Particles / Stars
        for p_idx in range(45):
            p_seed = p_idx * 137.5
            px = int((m.sin(p_seed) * 360 + 360 + m.cos(t * 0.4 + p_idx) * 20) % W)
            py = int((p_seed * 11 + t * 45) % H)
            pr = 1 if p_idx % 3 != 0 else 2
            p_alpha = int(90 + 70 * m.sin(t * 2 + p_idx))
            idraw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(p_alpha, p_alpha + 40, p_alpha + 60))

        # B. Central 3D Visual Stage with Perspective Grid
        # Stage Box (Dark Glassmorphism)
        idraw.rounded_rectangle((40, 320, 680, 775), radius=24, fill=(12, 20, 38), outline=(35, 60, 100), width=2)

        # 3D Depth Grid Lines converging into the distance
        grid_vanish_y = 440
        for gx in range(70, 660, 52):
            idraw.line([(gx, 760), (360 + (gx - 360) * 0.35, grid_vanish_y)], fill=(22, 38, 68), width=1)
        for gy in [750, 705, 650, 585, 515, 455]:
            idraw.line([(60, gy), (660, gy)], fill=(22, 38, 68), width=1)

        # C. 3D Elements based on topic
        if k == 'echo':
            # 3D Sound Beacon
            idraw.ellipse((140 - 15, 550 - 15, 140 + 15, 550 + 15), fill=C_CYAN)
            idraw.ellipse((140 - 25, 550 - 25, 140 + 25, 550 + 25), outline=(0, 240, 255, 120), width=2)
            
            # Massive 3D Cliff Silhouette in depth
            idraw.rectangle([(560, 370), (640, 740)], fill=(25, 38, 65), outline=C_GOLD, width=3)
            for cy in range(390, 730, 25):
                idraw.line([(560, cy), (640, cy)], fill=(45, 65, 105), width=2)

            # Volumetric Sound Wave rings travelling across 3D grid
            wave_p = (t * 0.8) % 1.0
            wx = 140 + 420 * (1 - abs(2 * wave_p - 1))
            wr = 25 + 50 * m.sin(wave_p * m.pi)
            w_col = C_CYAN if (2 * wave_p) < 1 else C_GOLD
            idraw.ellipse((wx - wr * 0.35, 550 - wr, wx + wr * 0.35, 550 + wr), outline=w_col, width=3)
            # Distance measurement ray
            idraw.line([(140, 725), (560, 725)], fill=(60, 95, 150), width=2)
            idraw.line([(140, 715), (140, 735)], fill=(60, 95, 150), width=2)
            idraw.line([(560, 715), (560, 735)], fill=(60, 95, 150), width=2)

        elif k == 'orbit':
            # Central Star with Pulsing Corona
            star_pulse = int(4 * m.sin(t * 5))
            idraw.ellipse((360 - 26 - star_pulse, 545 - 26 - star_pulse, 360 + 26 + star_pulse, 545 + 26 + star_pulse), fill=(255, 180, 40))
            # 3D Elliptical Orbits
            idraw.ellipse((360 - 140, 545 - 45, 360 + 140, 545 + 45), outline=(0, 240, 255, 110), width=2)
            idraw.ellipse((360 - 240, 545 - 80, 360 + 240, 545 + 80), outline=(255, 65, 140, 90), width=2)
            # Orbiting Planets
            p1_x = int(360 + 140 * m.cos(t * 2.2))
            p1_y = int(545 + 45 * m.sin(t * 2.2))
            idraw.ellipse((p1_x - 10, p1_y - 10, p1_x + 10, p1_y + 10), fill=C_CYAN)
            p2_x = int(360 + 240 * m.cos(t * 0.9))
            p2_y = int(545 + 80 * m.sin(t * 0.9))
            idraw.ellipse((p2_x - 14, p2_y - 14, p2_x + 14, p2_y + 14), fill=(255, 65, 140))

        else:
            # 3D Rotating Ring Gyroscope
            for ri, (rad_s, col_r, spd) in enumerate([(130, C_CYAN, 1.4), (180, C_GOLD, 0.9)]):
                pts = []
                for deg in range(0, 360, 15):
                    rad = m.radians(deg)
                    rx = int(360 + rad_s * m.cos(rad))
                    ry = int(545 + rad_s * m.sin(rad) * m.cos(t * spd + ri))
                    pts.append((rx, ry))
                idraw.line(pts + [pts[0]], fill=col_r, width=3)

        # D. Real-time Depth / Telemetry Meter (HUD Style - As seen in 3D Eye reference)
        cur_val = int(target_metric * min(1.0, progress * 1.05))
        # HUD Panel at top-right of 3D stage
        idraw.rounded_rectangle((410, 335, 665, 410), radius=12, fill=(8, 14, 28), outline=C_CYAN, width=1)
        idraw.text((425, 345), "CURRENT DEPTH / METRIC", font=unit_f, fill=C_MUTED)
        idraw.text((425, 365), f"{cur_val:,}", font=counter_f, fill=C_CYAN)
        idraw.text((545, 375), metric_unit.split()[0], font=unit_f, fill=C_GOLD)

        # E. Top Brand Bar & Progress Bar
        bar_w = (W - 96 - 30) / 4
        for idx in range(4):
            bx = 48 + idx * (bar_w + 10)
            idraw.rounded_rectangle((bx, 28, bx + bar_w, 34), radius=3, fill=(35, 52, 85))
            if idx <= j:
                idraw.rounded_rectangle((bx, 28, bx + bar_w, 34), radius=3, fill=C_CYAN)

        idraw.rounded_rectangle((48, 48, 220, 88), radius=20, fill=(18, 32, 60), outline=C_CYAN, width=1)
        idraw.text((64, 55), "THOUGHT LAB", font=brand_f, fill=C_CYAN)
        idraw.text((240, 55), f"•  EPISODE #{n+1:03}", font=brand_f, fill=C_MUTED)

        # Title Hook
        for line_i, line in enumerate(wrap(idraw, title, head_f, 620)):
            idraw.text((48, 115 + line_i * 50), line, font=head_f, fill=C_WHITE)

        # F. High-Retention Kinetic Subtitles Card (Bottom)
        idraw.rounded_rectangle((38, 855, 682, 1160), radius=26, fill=(8, 14, 28), outline=(40, 68, 115), width=2)
        idraw.text((62, 878), f"TELEMETRY LOG  //  {phases[j]}", font=tag_f, fill=C_GOLD)

        body_lines = wrap(idraw, text, sub_f, 595)
        for line_i, l in enumerate(body_lines):
            idraw.text((62, 928 + line_i * 46), l, font=sub_f, fill=C_WHITE)

        p.stdin.write(im.tobytes())

p.stdin.close()
assert p.wait() == 0

meta = {
    'title': f'{title} | Lab {n+1:03}',
    'description': ' '.join(x[0] for x in beats) + '\n\nCinematic 3D science exploration. #Shorts #Science #3DAnimation #Education',
    'episode': n
}
(out / 'meta.json').write_text(json.dumps(meta, indent=2))
print("Finished rendering Cinematic 3D Telemetry Short:", meta['title'])
