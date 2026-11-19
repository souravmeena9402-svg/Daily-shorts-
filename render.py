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

total_frames = sum(parts)

with wave.open(str(out / 'voice.wav'), 'wb') as w:
    w.setparams((1, 2, rate, 0, 'NONE', ''))
    w.writeframes(audio)

# 2. Invoke Blender 3D Headless Renderer
print(f"Rendering 3D Scene in Blender ({total_frames} frames)...")
frames_dir = out / 'frames'
frames_dir.mkdir(exist_ok=True)
frame_prefix = str(frames_dir / 'f_')

blender_cmd = [
    'blender', '-b',
    '-P', 'render_3d.py',
    '--',
    str(k),
    str(v),
    str(total_frames),
    frame_prefix
]
sp.run(blender_cmd, check=True)

# 3. Generate Floating Cinematic UI Overlay Frames
print("Generating UI Overlay...")
overlay_dir = out / 'overlay'
overlay_dir.mkdir(exist_ok=True)

def get_font(sz, bold=False):
    candidates = [
        f'/usr/share/fonts/truetype/dejavu/DejaVuSans{"-Bold" if bold else ""}.ttf',
        f'/usr/share/fonts/truetype/liberation/LiberationSans-{"Bold" if bold else "Regular"}.ttf'
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

badge_f = get_font(20, True)
head_f = get_font(42, True)
body_f = get_font(32, True)
tag_f = get_font(22, True)

def wrap(d, text, f, w):
    lines = ['']
    for word in text.split():
        s = (lines[-1] + ' ' + word).strip()
        if d.textlength(s, font=f) > w and lines[-1]:
            lines.append(word)
        else:
            lines[-1] = s
    return lines

step_names = ['OBSERVATION', 'ANALYSIS', 'THE MECHANISM', 'KEY TAKEAWAY']

for j, ((text, label), frames) in enumerate(zip(beats, parts)):
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)

    # Top Brand Badge
    d.rounded_rectangle((48, 50, 215, 88), radius=18, fill=(15, 25, 45, 220), outline=(0, 240, 255), width=1)
    d.text((64, 57), "THOUGHT LAB", font=badge_f, fill=(0, 240, 255))
    d.text((235, 57), f"•  EPISODE #{n+1:03}", font=tag_f, fill=(180, 200, 230))

    # Title
    for i, line in enumerate(wrap(d, title, head_f, 620)):
        d.text((48, 118 + i * 50), line, font=head_f, fill=(245, 248, 255))

    # Bottom Subtitle Card
    d.rounded_rectangle((38, 870, 682, 1160), radius=26, fill=(10, 16, 30, 230), outline=(45, 75, 125, 180), width=2)
    d.text((62, 890), f"PHASE {j+1}: {step_names[j]}", font=tag_f, fill=(255, 200, 80))

    body_lines = wrap(d, text, body_f, 600)
    for i, l in enumerate(body_lines):
        d.text((62, 935 + i * 44), l, font=body_f, fill=(245, 248, 255))

    # Top Instagram-style progress bar
    bar_w = (W - 96 - 30) / 4
    for idx in range(4):
        bx = 48 + idx * (bar_w + 10)
        d.rounded_rectangle((bx, 28, bx + bar_w, 34), radius=3, fill=(40, 60, 95, 200))
        if idx <= j:
            d.rounded_rectangle((bx, 28, bx + bar_w, 34), radius=3, fill=(0, 240, 255))

    for f in range(frames):
        frame_idx = sum(parts[:j]) + f
        card.save(overlay_dir / f'overlay_{frame_idx:05d}.png')

# 4. Final Composite: Blender 3D Video + Overlay PNG Sequence + Voice
print("Compositing 3D Video + UI + Audio with FFmpeg...")
final_output = out / 'short.mp4'

ffmpeg_composite = [
    'ffmpeg', '-loglevel', 'error', '-y',
    '-framerate', str(FPS),
    '-i', str(frames_dir / 'f_%04d.png'),
    '-framerate', str(FPS),
    '-i', str(overlay_dir / 'overlay_%05d.png'),
    '-i', str(out / 'voice.wav'),
    '-filter_complex', '[0:v][1:v]overlay=0:0[v]',
    '-map', '[v]',
    '-map', '2:a',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-c:a', 'aac',
    '-movflags', '+faststart',
    str(final_output)
]
sp.run(ffmpeg_composite, check=True)

meta = {
    'title': f'{title} | Lab {n+1:03}',
    'description': ' '.join(x[0] for x in beats) + '\n\nOriginal cinematic 3D explainer rendered with Blender Eevee engine. #Shorts #Blender3D #Science',
    'episode': n
}
(out / 'meta.json').write_text(json.dumps(meta, indent=2))
print("Finished rendering Short:", meta['title'], f"{total_frames/FPS:.1f}s")
