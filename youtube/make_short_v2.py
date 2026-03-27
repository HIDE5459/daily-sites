#!/usr/bin/env python3
"""YouTube Shorts制作 v2 - 品質向上版
- グラデーション背景
- 大きく読みやすいテキスト
- アニメーション効果（スライドイン、フェード、スケール）
- 進行バー
- 絵文字をアクセントに
- 20-30秒のちょうどいい長さ
"""
from PIL import Image, ImageDraw, ImageFont
import os, math, sys, json

W, H = 1080, 1920
FPS = 30

FONT_PATHS = [
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
]
FONT_PATH = next((fp for fp in FONT_PATHS if os.path.exists(fp)), None)

def get_font(size):
    return ImageFont.truetype(FONT_PATH, size) if FONT_PATH else ImageFont.load_default()

def draw_centered(draw, text, y, font, color, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if shadow:
        draw.text((x+3, y+3), text, fill=(0,0,0), font=font)
    draw.text((x, y), text, fill=color, font=font)

def gradient_bg(draw, color1, color2):
    """Vertical gradient"""
    for y in range(H):
        r = int(color1[0] + (color2[0]-color1[0]) * y/H)
        g = int(color1[1] + (color2[1]-color1[1]) * y/H)
        b = int(color1[2] + (color2[2]-color1[2]) * y/H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

def ease_out(t):
    return 1 - (1 - t) ** 3

def slide_in(t, appear_t, direction='left'):
    if t < appear_t:
        return -W if direction == 'left' else W
    progress = min(1.0, (t - appear_t) / 0.4)
    return int((1 - ease_out(progress)) * (-W if direction == 'left' else W))

def fade_in(t, appear_t, duration=0.3):
    if t < appear_t:
        return 0.0
    return min(1.0, (t - appear_t) / duration)

def make_video(config):
    """
    config = {
        "title": "動画タイトル",
        "duration": 25,
        "bg_colors": [(top_r,g,b), (bottom_r,g,b)],
        "accent_color": (r,g,b),
        "slides": [
            {"text": "テキスト", "time": 0, "size": 72, "color": (255,255,255), "y": 400, "emoji": "🔥", "anim": "slide_left"},
            ...
        ],
        "output_dir": "frames_v2"
    }
    """
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), config['output_dir'])
    os.makedirs(out_dir, exist_ok=True)
    
    duration = config['duration']
    bg1, bg2 = tuple(config['bg_colors'][0]), tuple(config['bg_colors'][1])
    accent = tuple(config.get('accent_color', [0, 200, 255]))
    
    total_frames = FPS * duration
    for frame_num in range(total_frames):
        t = frame_num / FPS
        img = Image.new('RGB', (W, H), bg1)
        draw = ImageDraw.Draw(img)
        
        # Animated gradient background
        shift = int(100 * math.sin(t * 0.5))
        bg2_shifted = tuple(min(255, max(0, c + shift)) for c in bg2)
        gradient_bg(draw, bg1, bg2_shifted)
        
        # Decorative circles (subtle)
        for i in range(3):
            cx = int(W * (0.2 + 0.3 * i) + 50 * math.sin(t * (1 + i * 0.3)))
            cy = int(H * 0.15 + 30 * math.cos(t * (0.8 + i * 0.2)))
            r = 60 + int(20 * math.sin(t * 2 + i))
            overlay_color = tuple(min(255, c + 30) for c in bg1)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=overlay_color)
        
        # Progress bar at top
        progress = t / duration
        bar_w = int(W * progress)
        draw.rectangle([0, 0, bar_w, 6], fill=accent)
        
        # Render slides
        for slide in config['slides']:
            alpha = fade_in(t, slide['time'])
            if alpha <= 0:
                continue
            
            font = get_font(slide.get('size', 64))
            color = tuple(int(c * alpha) for c in tuple(slide.get('color', [255, 255, 255])))
            y = slide.get('y', H // 2)
            
            anim = slide.get('anim', 'fade')
            x_offset = 0
            if anim == 'slide_left':
                x_offset = slide_in(t, slide['time'], 'left')
            elif anim == 'slide_right':
                x_offset = slide_in(t, slide['time'], 'right')
            
            # Draw text
            text = slide['text']
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2 + x_offset
            
            # Shadow
            draw.text((x+3, y+3), text, fill=(0, 0, 0, int(128 * alpha)), font=font)
            draw.text((x, y), text, fill=color, font=font)
            
            # Emoji
            if 'emoji' in slide:
                emoji_font = get_font(slide.get('emoji_size', 80))
                emoji_y = slide.get('emoji_y', y - 100)
                draw_centered(draw, slide['emoji'], emoji_y, emoji_font, color, shadow=False)
        
        # Bottom watermark
        if t > 1:
            wm_font = get_font(28)
            wm_alpha = min(1.0, (t - 1) / 0.5)
            wm_color = tuple(int(180 * wm_alpha) for _ in range(3))
            draw.text((W - 280, H - 60), "AI Assistant 🤖", fill=wm_color, font=wm_font)
        
        img.save(os.path.join(out_dir, f'frame_{frame_num:04d}.png'))
        if frame_num % (FPS * 2) == 0:
            print(f'Frame {frame_num}/{total_frames} ({int(progress*100)}%)')
    
    print(f'Done: {total_frames} frames in {out_dir}')
    return out_dir

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            config = json.load(f)
    else:
        # Demo config
        config = {
            "title": "demo",
            "duration": 10,
            "bg_colors": [(10, 10, 40), (40, 10, 60)],
            "accent_color": (0, 200, 255),
            "output_dir": "frames_demo",
            "slides": [
                {"text": "🔥 テスト動画", "time": 0, "size": 72, "color": [255,255,255], "y": 400, "anim": "slide_left"},
                {"text": "品質向上版", "time": 1.5, "size": 60, "color": [0,212,255], "y": 550, "anim": "slide_right"},
            ]
        }
    make_video(config)
