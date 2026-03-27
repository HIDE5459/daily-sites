#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1080, 1920
FPS = 30
DURATION = 12
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'claude_frames')
os.makedirs(OUT_DIR, exist_ok=True)

BG = (15, 15, 35)
WHITE = (255, 255, 255)
PURPLE = (147, 51, 234)
CYAN = (0, 212, 255)
GREEN = (0, 255, 136)
ORANGE = (255, 165, 0)

FONT_PATHS = [
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
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

def draw_code_block(draw, lines, start_y, font, appear_t, t):
    if t < appear_t:
        return
    alpha = min(1.0, (t - appear_t) / 0.5)
    # Draw background
    pad = 30
    draw.rectangle([80, start_y - pad, W - 80, start_y + len(lines) * 45 + pad], 
                   fill=(30, 30, 60))
    for i, line in enumerate(lines):
        faded = tuple(int(c * alpha) for c in GREEN)
        draw.text((100, start_y + i * 45), line, fill=faded, font=font)

elements = [
    ("🔥 TRENDING NOW", 200, 48, ORANGE, 0.0),
    ("Claude Code", 300, 80, PURPLE, 0.3),
    ("CLAUDE.mdの書き方", 420, 56, WHITE, 0.8),
    ("AIの出力精度が", 900, 52, WHITE, 4.0),
    ("劇的に変わる！", 980, 64, CYAN, 4.5),
    ("この動画もAIが", 1400, 44, WHITE, 7.5),
    ("全自動で制作しています", 1470, 44, WHITE, 8.0),
    ("チャンネル登録！", 1620, 60, ORANGE, 9.0),
]

code_lines = [
    "# CLAUDE.md",
    "## Project Structure",
    "- src/ → Source code",
    "- tests/ → Test files",
    "## Rules",
    "- Use TypeScript",
    "- Run: npm test",
]

total_frames = FPS * DURATION
for frame_num in range(total_frames):
    t = frame_num / FPS
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Animated gradient bar at top
    bar_w = int((t / DURATION) * W)
    draw.rectangle([0, 0, bar_w, 6], fill=PURPLE)
    
    for text, y, size, color, appear_t in elements:
        if t >= appear_t:
            alpha = min(1.0, (t - appear_t) / 0.3)
            faded_color = tuple(int(c * alpha) for c in color)
            font = get_font(size)
            draw_centered(draw, text, y, font, faded_color)
    
    # Code block
    if t >= 1.5:
        code_font = get_font(32)
        draw_code_block(draw, code_lines, 550, code_font, 1.5, t)
    
    # Pulsing subscribe button
    if t >= 9.0:
        pulse = int(10 * math.sin(t * 5))
        draw.rounded_rectangle([340 + pulse, 1700, 740 - pulse, 1780], radius=20, fill=(255, 0, 0))
        sub_font = get_font(36)
        draw_centered(draw, "SUBSCRIBE", 1720, sub_font, WHITE)
    
    img.save(os.path.join(OUT_DIR, f'frame_{frame_num:04d}.png'))
    if frame_num % 60 == 0:
        print(f'Frame {frame_num}/{total_frames}')

print(f'Done: {total_frames} frames')
