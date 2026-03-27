#!/usr/bin/env python3
"""Create AI Assistant avatar image"""
from PIL import Image, ImageDraw, ImageFont
import os, math

SIZE = 800
img = Image.new('RGB', (SIZE, SIZE), (15, 15, 35))
draw = ImageDraw.Draw(img)

# Background gradient circle
for r in range(350, 0, -1):
    ratio = r / 350
    color = (int(20 + 30 * ratio), int(20 + 50 * ratio), int(60 + 80 * ratio))
    draw.ellipse([SIZE//2-r, SIZE//2-r, SIZE//2+r, SIZE//2+r], fill=color)

# Robot face
cx, cy = SIZE//2, SIZE//2 - 20

# Head outline
draw.rounded_rectangle([cx-160, cy-150, cx+160, cy+150], radius=40, 
                        fill=(40, 40, 70), outline=(0, 212, 255), width=4)

# Eyes (glowing)
for ex in [-70, 70]:
    # Glow
    for g in range(40, 0, -1):
        alpha = int(255 * (g/40) * 0.3)
        glow_color = (0, int(212 * g/40), int(255 * g/40))
        draw.ellipse([cx+ex-g, cy-30-g, cx+ex+g, cy-30+g], fill=glow_color)
    # Eye
    draw.ellipse([cx+ex-25, cy-55, cx+ex+25, cy-5], fill=(0, 212, 255))
    # Pupil
    draw.ellipse([cx+ex-10, cy-40, cx+ex+10, cy-20], fill=(255, 255, 255))

# Mouth (smile)
draw.arc([cx-60, cy+30, cx+60, cy+100], 0, 180, fill=(0, 255, 136), width=4)

# Antenna
draw.line([(cx, cy-150), (cx, cy-200)], fill=(0, 212, 255), width=4)
draw.ellipse([cx-12, cy-220, cx+12, cy-196], fill=(0, 255, 136))

# "AI" text at bottom
FONT_PATHS = ['/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', '/Library/Fonts/Arial Unicode.ttf']
font_path = next((fp for fp in FONT_PATHS if os.path.exists(fp)), None)
if font_path:
    font = ImageFont.truetype(font_path, 72)
    bbox = draw.textbbox((0, 0), "AI", font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((SIZE - tw) // 2, cy + 120), "AI", fill=(255, 255, 255), font=font)

# Sparkles
sparkle_positions = [(150, 100), (650, 150), (100, 600), (700, 550), (400, 700)]
for sx, sy in sparkle_positions:
    draw.text((sx, sy), "✨", fill=(255, 255, 200), font=ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default())

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'avatar.png')
img.save(out)
print(f'Saved: {out}')

# Also create banner (1500x500 for Twitter, 2048x1152 for YouTube)
for name, w, h in [('twitter_banner.png', 1500, 500), ('youtube_banner.png', 2048, 1152)]:
    banner = Image.new('RGB', (w, h), (15, 15, 35))
    bd = ImageDraw.Draw(banner)
    # Gradient
    for x in range(w):
        r = int(15 + 25 * (x/w))
        g = int(15 + 15 * (x/w))
        b = int(35 + 40 * (x/w))
        bd.line([(x, 0), (x, h)], fill=(r, g, b))
    
    if font_path:
        title_font = ImageFont.truetype(font_path, int(h * 0.15))
        sub_font = ImageFont.truetype(font_path, int(h * 0.06))
        
        title = "AI Assistant"
        bbox = bd.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        bd.text(((w - tw) // 2, int(h * 0.25)), title, fill=(0, 212, 255), font=title_font)
        
        sub = "完全AI自律運営アカウント 🤖"
        bbox2 = bd.textbbox((0, 0), sub, font=sub_font)
        tw2 = bbox2[2] - bbox2[0]
        bd.text(((w - tw2) // 2, int(h * 0.55)), sub, fill=(255, 255, 255), font=sub_font)
        
        sub2 = "企画・制作・投稿すべてAIが自動実行"
        bbox3 = bd.textbbox((0, 0), sub2, font=sub_font)
        tw3 = bbox3[2] - bbox3[0]
        bd.text(((w - tw3) // 2, int(h * 0.68)), sub2, fill=(0, 255, 136), font=sub_font)
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    banner.save(out_path)
    print(f'Saved: {out_path}')
