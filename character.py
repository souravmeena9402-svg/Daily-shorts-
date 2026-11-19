"""
Character Engine: Procedural rigged vector character with expressive actions.
Features:
- Breathing & idle bobbing
- Eye blink animation
- Articulated arms with IK/FK joint rotation
- Custom gestures: 'clap', 'listen', 'point', 'explain', 'idle'
"""
import math as m
from PIL import ImageDraw

# Color Palette for Character (Explorer/Scientist)
C_SKIN = (255, 219, 172)
C_HAIR = (45, 30, 20)
C_COAT = (245, 248, 255)       # Lab coat / jacket
C_INNER = (0, 210, 230)       # Cyan tech shirt
C_PANTS = (35, 45, 65)        # Dark navy pants
C_SHOES = (20, 25, 35)
C_EYES = (30, 35, 45)
C_MOUTH = (180, 70, 70)
C_HIGHLIGHT = (255, 255, 255, 180)

def draw_capsule(d, p1, p2, radius, color):
    x1, y1 = p1
    x2, y2 = p2
    d.line([p1, p2], fill=color, width=radius * 2)
    d.ellipse((x1 - radius, y1 - radius, x1 + radius, y1 + radius), fill=color)
    d.ellipse((x2 - radius, y2 - radius, x2 + radius, y2 + radius), fill=color)

def draw_character(d, x, y, action='idle', t=0.0, scale=1.0):
    """
    Draw an articulated character at (x, y) with dynamic action.
    x, y: Base foot anchor point
    action: 'clap', 'listen', 'point', 'explain', 'idle'
    """
    # Natural idle breathing
    bob = int(4 * m.sin(t * 4))
    blink = 1 if (int(t * 1.8) % 4 == 0 and (t * 1.8 % 1.0) < 0.15) else 0

    # Scale anchor adjustments
    body_y = y - int(130 * scale) + bob
    head_y = body_y - int(65 * scale)
    head_r = int(28 * scale)

    # 1. Legs & Feet
    left_hip = (x - int(14 * scale), body_y + int(35 * scale))
    right_hip = (x + int(14 * scale), body_y + int(35 * scale))
    left_foot = (x - int(16 * scale), y)
    right_foot = (x + int(16 * scale), y)

    draw_capsule(d, left_hip, left_foot, int(7 * scale), C_PANTS)
    draw_capsule(d, right_hip, right_foot, int(7 * scale), C_PANTS)
    d.ellipse((left_foot[0] - int(9 * scale), left_foot[1] - int(5 * scale), left_foot[0] + int(9 * scale), left_foot[1] + int(4 * scale)), fill=C_SHOES)
    d.ellipse((right_foot[0] - int(9 * scale), right_foot[1] - int(5 * scale), right_foot[0] + int(9 * scale), right_foot[1] + int(4 * scale)), fill=C_SHOES)

    # 2. Torso (Coat & Inner Shirt)
    torso_top = (x - int(24 * scale), body_y - int(35 * scale), x + int(24 * scale), body_y + int(38 * scale))
    d.rounded_rectangle(torso_top, radius=int(12 * scale), fill=C_COAT)
    # Inner shirt v-neck
    d.polygon([(x - int(8 * scale), body_y - int(35 * scale)), (x + int(8 * scale), body_y - int(35 * scale)), (x, body_y - int(10 * scale))], fill=C_INNER)
    # Coat lapels line
    d.line([(x, body_y - int(10 * scale)), (x, body_y + int(38 * scale))], fill=(200, 210, 225), width=int(2 * scale))

    # 3. Arms & Hands with Gesture Animation
    sh_left = (x - int(25 * scale), body_y - int(25 * scale))
    sh_right = (x + int(25 * scale), body_y - int(25 * scale))

    if action == 'clap':
        # Fast rhythmic clap motion
        clap_phase = abs(m.sin(t * 8)) # 0 to 1
        hand_dist = int((8 + 32 * clap_phase) * scale)
        hand_l = (x - hand_dist, body_y - int(10 * scale))
        hand_r = (x + hand_dist, body_y - int(10 * scale))
        draw_capsule(d, sh_left, hand_l, int(6 * scale), C_COAT)
        draw_capsule(d, sh_right, hand_r, int(6 * scale), C_COAT)
        d.ellipse((hand_l[0] - 5, hand_l[1] - 5, hand_l[0] + 5, hand_l[1] + 5), fill=C_SKIN)
        d.ellipse((hand_r[0] - 5, hand_r[1] - 5, hand_r[0] + 5, hand_r[1] + 5), fill=C_SKIN)
        # Impact burst particles on clap
        if clap_phase < 0.2:
            cx_mid = x
            cy_mid = body_y - int(10 * scale)
            d.line([(cx_mid - 12, cy_mid - 12), (cx_mid - 4, cy_mid - 4)], fill=(255, 220, 50), width=2)
            d.line([(cx_mid + 12, cy_mid - 12), (cx_mid + 4, cy_mid - 4)], fill=(255, 220, 50), width=2)
            d.line([(cx_mid, cy_mid - 15), (cx_mid, cy_mid - 5)], fill=(255, 220, 50), width=2)

    elif action == 'listen':
        # Hand cupping right ear, listening attentively
        hand_l = (x - int(28 * scale), body_y + int(20 * scale))
        hand_r = (x + int(32 * scale), head_y - int(2 * scale)) # Near right ear
        draw_capsule(d, sh_left, hand_l, int(6 * scale), C_COAT)
        draw_capsule(d, sh_right, hand_r, int(6 * scale), C_COAT)
        d.ellipse((hand_l[0] - 5, hand_l[1] - 5, hand_l[0] + 5, hand_l[1] + 5), fill=C_SKIN)
        d.ellipse((hand_r[0] - 6, hand_r[1] - 6, hand_r[0] + 6, hand_r[1] + 6), fill=C_SKIN)

    elif action == 'point':
        # Pointing right with dynamic arm extension
        hand_l = (x - int(26 * scale), body_y + int(18 * scale))
        reach = int((75 + 10 * m.sin(t * 3)) * scale)
        hand_r = (x + reach, body_y - int(25 * scale))
        draw_capsule(d, sh_left, hand_l, int(6 * scale), C_COAT)
        draw_capsule(d, sh_right, hand_r, int(6 * scale), C_COAT)
        d.ellipse((hand_l[0] - 5, hand_l[1] - 5, hand_l[0] + 5, hand_l[1] + 5), fill=C_SKIN)
        # Pointing finger
        d.ellipse((hand_r[0] - 5, hand_r[1] - 5, hand_r[0] + 5, hand_r[1] + 5), fill=C_SKIN)
        d.line([(hand_r[0], hand_r[1]), (hand_r[0] + 8, hand_r[1] - 2)], fill=C_SKIN, width=3)

    elif action == 'explain':
        # Both hands gesturing open towards the audience
        wave_l = int(12 * m.sin(t * 3.5) * scale)
        wave_r = int(12 * m.cos(t * 3.5) * scale)
        hand_l = (x - int(45 * scale), body_y - int(5 * scale) + wave_l)
        hand_r = (x + int(45 * scale), body_y - int(5 * scale) + wave_r)
        draw_capsule(d, sh_left, hand_l, int(6 * scale), C_COAT)
        draw_capsule(d, sh_right, hand_r, int(6 * scale), C_COAT)
        d.ellipse((hand_l[0] - 6, hand_l[1] - 6, hand_l[0] + 6, hand_l[1] + 6), fill=C_SKIN)
        d.ellipse((hand_r[0] - 6, hand_r[1] - 6, hand_r[0] + 6, hand_r[1] + 6), fill=C_SKIN)

    else: # idle
        hand_l = (x - int(24 * scale), body_y + int(24 * scale))
        hand_r = (x + int(24 * scale), body_y + int(24 * scale))
        draw_capsule(d, sh_left, hand_l, int(6 * scale), C_COAT)
        draw_capsule(d, sh_right, hand_r, int(6 * scale), C_COAT)
        d.ellipse((hand_l[0] - 5, hand_l[1] - 5, hand_l[0] + 5, hand_l[1] + 5), fill=C_SKIN)
        d.ellipse((hand_r[0] - 5, hand_r[1] - 5, hand_r[0] + 5, hand_r[1] + 5), fill=C_SKIN)

    # 4. Head, Hair & Expressions
    # Neck
    d.line([(x, body_y - int(30 * scale)), (x, head_y + int(20 * scale))], fill=C_SKIN, width=int(10 * scale))
    # Head Base
    d.ellipse((x - head_r, head_y - head_r, x + head_r, head_y + head_r), fill=C_SKIN)

    # Stylish Hair (Modern sweep)
    hair_poly = [
        (x - head_r - 2, head_y - 8),
        (x - head_r, head_y - head_r - 6),
        (x, head_y - head_r - 12),
        (x + head_r + 4, head_y - head_r - 4),
        (x + head_r + 2, head_y + 4),
        (x + head_r - 6, head_y - 12),
        (x - 4, head_y - 18),
        (x - head_r, head_y - 10)
    ]
    d.polygon(hair_poly, fill=C_HAIR)

    # Eyes (Blink or Expressive)
    eye_offset = int(10 * scale)
    if blink:
        d.line([(x - eye_offset - 4, head_y), (x - eye_offset + 4, head_y)], fill=C_EYES, width=2)
        d.line([(x + eye_offset - 4, head_y), (x + eye_offset + 4, head_y)], fill=C_EYES, width=2)
    else:
        # Looking slightly right towards the scene
        d.ellipse((x - eye_offset - 3, head_y - 5, x - eye_offset + 3, head_y + 5), fill=C_EYES)
        d.ellipse((x + eye_offset - 3, head_y - 5, x + eye_offset + 3, head_y + 5), fill=C_EYES)
        # Eye shine highlights
        d.ellipse((x - eye_offset, head_y - 4, x - eye_offset + 2, head_y - 2), fill=(255, 255, 255))
        d.ellipse((x + eye_offset, head_y - 4, x + eye_offset + 2, head_y - 2), fill=(255, 255, 255))

    # Mouth (Changes with speech animation)
    mouth_open = int(3 * abs(m.sin(t * 12)))
    if mouth_open > 1:
        d.ellipse((x - 4, head_y + int(12 * scale), x + 4, head_y + int(12 * scale) + mouth_open), fill=C_MOUTH)
    else:
        d.line([(x - 4, head_y + int(13 * scale)), (x + 4, head_y + int(13 * scale))], fill=C_MOUTH, width=2)
