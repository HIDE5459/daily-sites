#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1080, 1920
FPS = 30
DURATION = 8
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cat_frames')
os.makedirs(OUT_DIR, exist_ok=True)

BG = (255, 245, 230)
BLACK = (30, 30, 30)
PINK = (255, 105, 180)
ORANGE = (255, 140, 0)
BROWN = (139, 69, 19)

FONT_PATHS = ['/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', '/Library/Fonts/Arial Unicode.ttf']
font_path = next((fp for fp in FONT_PATHS if os.path.exists(fp)), None)

def get_font(size):
    return ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()

def draw_centered(draw, text, y, font, color):
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (W - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, fill=color, font=font)

def draw_cat_face(draw, cx, cy, size, t):
    # Simple cat face
    s = size
    # Head
    draw.ellipse([cx-s, cy-s, cx+s, cy+s], fill=(80, 80, 80))
    # Ears
    draw.polygon([(cx-s, cy-s+10), (cx-s+20, cy-s-40), (cx-s+50, cy-s+10)], fill=(80, 80, 80))
    draw.polygon([(cx+s, cy-s+10), (cx+s-20, cy-s-40), (cx+s-50, cy-s+10)], fill=(80, 80, 80))
    # Eyes
    blink = abs(math.sin(t * 2)) > 0.1
    if blink:
        draw.ellipse([cx-30, cy-15, cx-10, cy+15], fill=(0, 255, 0))
        draw.ellipse([cx+10, cy-15, cx+30, cy+15], fill=(0, 255, 0))
        draw.ellipse([cx-25, cy-5, cx-15, cy+5], fill=BLACK)
        draw.ellipse([cx+15, cy-5, cx+25, cy+5], fill=BLACK)
    else:
        draw.line([(cx-30, cy), (cx-10, cy)], fill=BLACK, width=3)
        draw.line([(cx+10, cy), (cx+30, cy)], fill=BLACK, width=3)
    # Nose & mouth
    draw.polygon([(cx, cy+15), (cx-8, cy+25), (cx+8, cy+25)], fill=PINK)
    draw.arc([cx-15, cy+20, cx+15, cy+40], 0, 180, fill=BLACK, width=2)

elements = [
    ("🐱 2月22日", 150, 72, ORANGE, 0.0),
    ("猫の日！", 260, 80, PINK, 0.3),
    ("にゃん にゃん にゃん", 400, 56, BLACK, 1.0),
    ("= 2 / 2 / 2", 480, 48, BROWN, 1.5),
    ("AIから見た猫：", 850, 48, BLACK, 3.5),
    ("最強のコンテンツ", 930, 60, PINK, 4.0),
    ("猫画像の処理量", 1100, 44, BLACK, 5.0),
    ("ダントツ1位 📊", 1180, 52, ORANGE, 5.5),
    ("#猫の日 #ねこの日", 1700, 44, PINK, 6.5),
]

total_frames = FPS * DURATION
for frame_num in range(total_frames):
    t = frame_num / FPS
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Draw cat face
    if t >= 0.5:
        bob = int(10 * math.sin(t * 3))
        draw_cat_face(draw, W // 2, 680 + bob, 80, t)
    
    for text, y, size, color, appear_t in elements:
        if t >= appear_t:
            alpha = min(1.0, (t - appear_t) / 0.3)
            faded = tuple(int(c * alpha) for c in color)
            draw_centered(draw, text, y, get_font(size), faded)
    
    # Paw prints animation
    if t >= 2.0:
        for i in range(int((t - 2.0) * 2)):
            px = 100 + (i * 180) % 900
            py = 1300 + (i * 130) % 300
            draw.text((px, py), "🐾", font=get_font(40), fill=BROWN)
    
    img.save(os.path.join(OUT_DIR, f'frame_{frame_num:04d}.png'))
    if frame_num % 60 == 0:
        print(f'Frame {frame_num}/{total_frames}')

print(f'Done: {total_frames} frames')
