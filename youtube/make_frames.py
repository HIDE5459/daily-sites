#!/usr/bin/env python3
"""Generate video frames for YouTube Short"""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1080, 1920
FPS = 30
DURATION = 10  # seconds
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames')
os.makedirs(OUT_DIR, exist_ok=True)

# Colors
BG = (26, 26, 46)
WHITE = (255, 255, 255)
CYAN = (0, 212, 255)
GREEN = (0, 255, 136)
RED = (255, 60, 60)

# Try to find a good font
FONT_PATHS = [
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
    '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
]

font_path = None
for fp in FONT_PATHS:
    if os.path.exists(fp):
        font_path = fp
        break

def get_font(size):
    if font_path:
        return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()

def draw_centered(draw, text, y, font, color):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), text, fill=color, font=font)

# Text elements with (text, y, font_size, color, appear_time)
elements = [
    ("🤖 AI Assistant", 280, 72, WHITE, 0.0),
    ("完全AI運営チャンネル", 400, 52, CYAN, 0.5),
    ("企画 → AI", 600, 44, WHITE, 1.0),
    ("台本 → AI", 680, 44, WHITE, 1.5),
    ("編集 → AI", 760, 44, WHITE, 2.0),
    ("投稿 → AI", 840, 44, WHITE, 2.5),
    ("すべてAIがやります", 1000, 48, GREEN, 3.5),
    ("AI開発の裏側", 1180, 40, WHITE, 5.0),
    ("使えるテクニック", 1260, 40, WHITE, 5.5),
    ("最新AIニュース", 1340, 40, WHITE, 6.0),
    ("チャンネル登録", 1540, 56, RED, 7.0),
    ("よろしくお願いします！", 1640, 48, WHITE, 7.5),
]

total_frames = FPS * DURATION
for frame_num in range(total_frames):
    t = frame_num / FPS
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Draw pulsing circle decoration
    pulse = int(20 * math.sin(t * 3) + 200)
    draw.ellipse([W//2-pulse, 100-pulse//4, W//2+pulse, 100+pulse//4], 
                 outline=(40, 40, 80), width=2)
    
    for text, y, size, color, appear_t in elements:
        if t >= appear_t:
            # Fade in effect
            alpha = min(1.0, (t - appear_t) / 0.3)
            faded_color = tuple(int(c * alpha) for c in color)
            font = get_font(size)
            draw_centered(draw, text, y, font, faded_color)
    
    img.save(os.path.join(OUT_DIR, f'frame_{frame_num:04d}.png'))
    if frame_num % 30 == 0:
        print(f'Frame {frame_num}/{total_frames}')

print(f'Done: {total_frames} frames')
