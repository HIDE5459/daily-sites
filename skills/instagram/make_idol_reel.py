#!/usr/bin/env python3
"""
AIアイドルリール動画をPillow+ffmpegで軽量生成
Remotion不要、メモリ節約
"""
import subprocess, sys, os, glob, time
from PIL import Image, ImageDraw, ImageFont

WORKSPACE = "/Users/hide/.openclaw/workspace"
W, H = 1080, 1920
FPS = 30
SECONDS_PER_SLIDE = 2
FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

def create_frame(image_path, text, frame_in_slide, total_slide_frames, slide_index):
    """1フレーム生成"""
    img = Image.open(image_path).convert("RGB")
    
    # Crop to 9:16
    iw, ih = img.size
    target_ratio = W / H
    current_ratio = iw / ih
    if current_ratio > target_ratio:
        new_w = int(ih * target_ratio)
        left = (iw - new_w) // 2
        img = img.crop((left, 0, left + new_w, ih))
    else:
        new_h = int(iw / target_ratio)
        top = (ih - new_h) // 2
        img = img.crop((0, top, iw, top + new_h))
    
    # Ken Burns zoom
    progress = frame_in_slide / total_slide_frames
    scale = 1.0 + 0.08 * progress
    new_size = (int(W * scale), int(H * scale))
    img = img.resize(new_size, Image.LANCZOS)
    left = (img.width - W) // 2
    top = (img.height - H) // 2
    img = img.crop((left, top, left + W, top + H))
    
    draw = ImageDraw.Draw(img)
    
    # Gradient overlay at bottom
    for y in range(H - 400, H):
        alpha = int(180 * (y - (H - 400)) / 400)
        draw.rectangle([(0, y), (W, y + 1)], fill=(0, 0, 0, alpha))
    
    # Text with shadow
    try:
        font = ImageFont.truetype(FONT_PATH, 56)
        small_font = ImageFont.truetype(FONT_PATH, 28)
    except:
        font = ImageFont.load_default()
        small_font = font
    
    # Text pop-in effect
    text_progress = min(1.0, max(0, (frame_in_slide - 5) / 10))
    if text_progress > 0:
        text_y = int(H - 250 + (1 - text_progress) * 30)
        # Shadow
        draw.text((W // 2 + 3, text_y + 3), text, font=font, fill=(0, 0, 0), anchor="mm")
        draw.text((W // 2, text_y), text, font=font, fill="white", anchor="mm")
    
    # AI badge
    badge_text = "🤖 AI Generated"
    draw.rounded_rectangle([(30, 50), (280, 95)], radius=20, fill=(255, 105, 180, 200))
    draw.text((155, 72), badge_text, font=small_font, fill="white", anchor="mm")
    
    # White border
    draw.rectangle([(0, 0), (W - 1, H - 1)], outline="white", width=6)
    
    # Progress bar
    bar_w = int(W * (slide_index + progress) / 4)  # assuming 4 slides
    draw.rectangle([(0, H - 4), (bar_w, H)], fill=(255, 105, 180))
    
    return img

def make_reel(image_paths, texts, output_path):
    """画像リストからリール動画を生成"""
    frames_dir = f"{WORKSPACE}/instagram/tmp_frames"
    os.makedirs(frames_dir, exist_ok=True)
    
    # Clean old frames
    for f in glob.glob(f"{frames_dir}/*.jpg"):
        os.remove(f)
    
    total_slide_frames = FPS * SECONDS_PER_SLIDE
    frame_num = 0
    
    for slide_idx, (img_path, text) in enumerate(zip(image_paths, texts)):
        print(f"Slide {slide_idx + 1}/{len(image_paths)}: {os.path.basename(img_path)}")
        for f in range(total_slide_frames):
            frame = create_frame(img_path, text, f, total_slide_frames, slide_idx)
            frame.save(f"{frames_dir}/frame_{frame_num:05d}.jpg", quality=90)
            frame_num += 1
        
        # Flash transition (3 white frames)
        if slide_idx < len(image_paths) - 1:
            for f in range(3):
                white = Image.new("RGB", (W, H), "white")
                white.save(f"{frames_dir}/frame_{frame_num:05d}.jpg", quality=90)
                frame_num += 1
    
    print(f"Total frames: {frame_num}")
    
    # ffmpeg encode
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", f"{frames_dir}/frame_%05d.jpg",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "23",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    
    # Cleanup
    for f in glob.glob(f"{frames_dir}/*.jpg"):
        os.remove(f)
    os.rmdir(frames_dir)
    
    size = os.path.getsize(output_path)
    print(f"✅ Reel saved: {output_path} ({size / 1024 / 1024:.1f} MB)")

if __name__ == "__main__":
    # Default: use available idol images
    idol_images = sorted(glob.glob(f"{WORKSPACE}/instagram/images/idol_*.jpg"))
    
    if len(idol_images) < 2:
        print("Need at least 2 idol images")
        sys.exit(1)
    
    # Use up to 4 images
    images = idol_images[:4]
    default_texts = ["✌️ ピース！", "💕 かわいい？", "🌸 おでかけ日和", "✨ また明日ね！"]
    texts = default_texts[:len(images)]
    
    output = f"{WORKSPACE}/instagram/idol_reel_new.mp4"
    make_reel(images, texts, output)
