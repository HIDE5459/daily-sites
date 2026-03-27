#!/usr/bin/env python3
"""Daily Trend Video Generator
日次トレンドまとめ動画を生成してYouTubeにアップロード
"""
import argparse, json, os, sys, subprocess, math, tempfile, shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ----- Constants -----
W, H = 1080, 1920
FPS = 30
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FONT_PATHS = [
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
]
FONT_PATH = next((fp for fp in FONT_PATHS if os.path.exists(fp)), None)

# Category → color scheme
CATEGORY_COLORS = {
    'スポーツ':     {'bg1': (10, 30, 60),   'bg2': (30, 80, 140),  'accent': (0, 180, 255),  'emoji': '⚽'},
    '事件':         {'bg1': (60, 10, 10),   'bg2': (120, 30, 30),  'accent': (255, 80, 80),  'emoji': '🚨'},
    '音楽':         {'bg1': (40, 10, 60),   'bg2': (80, 20, 100),  'accent': (200, 80, 255), 'emoji': '🎵'},
    'エンタメ':     {'bg1': (60, 30, 10),   'bg2': (120, 60, 20),  'accent': (255, 180, 0),  'emoji': '🎬'},
    'テクノロジー': {'bg1': (10, 40, 50),   'bg2': (20, 80, 100),  'accent': (0, 220, 200),  'emoji': '💻'},
    'default':      {'bg1': (15, 15, 35),   'bg2': (35, 15, 55),   'accent': (0, 212, 255),  'emoji': '🔥'},
}

def get_font(size):
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()

def ease_out(t):
    return 1 - (1 - t) ** 3

def draw_text_centered(draw, text, y, font, color, x_offset=0, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2 + x_offset
    if shadow:
        draw.text((x+3, y+3), text, fill=(0,0,0,150), font=font)
    draw.text((x, y), text, fill=color, font=font)

def gradient_bg(draw, c1, c2):
    for y in range(H):
        r = int(c1[0] + (c2[0]-c1[0]) * y/H)
        g = int(c1[1] + (c2[1]-c1[1]) * y/H)
        b = int(c1[2] + (c2[2]-c1[2]) * y/H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

def wrap_text(text, font, max_width, draw):
    """Wrap Japanese text to fit max_width"""
    lines = []
    current = ''
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines

def make_frames_for_trend(trend, out_dir, slide_duration=5.0):
    """1トレンド分のフレームを生成"""
    keyword = trend['keyword']
    narration = trend['narration']
    volume = trend.get('volume', '')
    category = trend.get('category', 'default')
    
    colors = CATEGORY_COLORS.get(category, CATEGORY_COLORS['default'])
    bg1 = colors['bg1']
    bg2 = colors['bg2']
    accent = colors['accent']
    emoji = colors['emoji']
    
    total_frames = int(FPS * slide_duration)
    
    # Pre-create dummy draw for text measurement
    dummy_img = Image.new('RGB', (W, H), bg1)
    dummy_draw = ImageDraw.Draw(dummy_img)
    
    # Fonts
    f_emoji = get_font(120)
    f_keyword = get_font(72)
    f_volume = get_font(50)
    f_narration = get_font(44)
    f_category = get_font(38)
    
    # Wrap narration
    narr_lines = wrap_text(narration, f_narration, W - 120, dummy_draw)
    
    for frame_num in range(total_frames):
        t = frame_num / FPS
        img = Image.new('RGB', (W, H), bg1)
        draw = ImageDraw.Draw(img)
        
        # Animated gradient
        shift = int(60 * math.sin(t * 0.8))
        bg2_anim = tuple(min(255, max(0, c + shift)) for c in bg2)
        gradient_bg(draw, bg1, bg2_anim)
        
        # Decorative shapes
        for i in range(4):
            cx = int(W * (0.15 + 0.25 * i) + 40 * math.sin(t * (0.7 + i * 0.3)))
            cy = int(H * 0.1 + 30 * math.cos(t * (0.6 + i * 0.2)))
            r = 80 + int(20 * math.sin(t * 1.5 + i))
            overlay_color = tuple(min(255, c + 20) for c in bg1)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=overlay_color)
        
        # Progress bar
        progress = t / slide_duration
        bar_w = int(W * progress)
        draw.rectangle([0, 0, bar_w, 8], fill=accent)
        
        # ---- Content ----
        # Emoji (appears at t=0.2)
        if t >= 0.2:
            alpha = min(1.0, (t - 0.2) / 0.3)
            alpha_color = tuple(int(c * alpha) for c in accent)
            draw_text_centered(draw, emoji, 280, f_emoji, alpha_color, shadow=False)
        
        # Category badge
        if t >= 0.4:
            alpha = min(1.0, (t - 0.4) / 0.3)
            cat_color = tuple(int(c * alpha) for c in (200, 200, 200))
            draw_text_centered(draw, f'#{category}', 450, f_category, cat_color)
        
        # Keyword (slide in from left)
        if t >= 0.6:
            alpha = min(1.0, (t - 0.6) / 0.4)
            progress_anim = min(1.0, (t - 0.6) / 0.4)
            x_off = int((1 - ease_out(progress_anim)) * -W)
            kw_color = tuple(int(c * alpha) for c in (255, 255, 255))
            draw_text_centered(draw, keyword, 560, f_keyword, kw_color, x_off)
        
        # Volume
        if t >= 1.0 and volume:
            alpha = min(1.0, (t - 1.0) / 0.3)
            vol_color = tuple(int(c * alpha) for c in accent)
            draw_text_centered(draw, f'🔍 {volume}回検索', 680, f_volume, vol_color)
        
        # Narration lines (appear one by one)
        narr_start = 1.4
        for i, line in enumerate(narr_lines):
            appear_t = narr_start + i * 0.4
            if t >= appear_t:
                alpha = min(1.0, (t - appear_t) / 0.35)
                n_color = tuple(int(c * alpha) for c in (230, 230, 230))
                y_pos = 840 + i * 80
                draw_text_centered(draw, line, y_pos, f_narration, n_color)
        
        # Bottom: channel watermark
        if t > 1.5:
            wm_alpha = min(1.0, (t - 1.5) / 0.5)
            wm_color = tuple(int(150 * wm_alpha) for _ in range(3))
            wm_font = get_font(30)
            draw_text_centered(draw, '🤖 AI Assistant Channel', 1820, wm_font, wm_color, shadow=False)
        
        img.save(os.path.join(out_dir, f'frame_{frame_num:04d}.png'))
        if frame_num % (FPS * 2) == 0:
            print(f'  frames: {frame_num+1}/{total_frames}')

def make_intro_frames(out_dir, date_str, trend_count, duration=3.0):
    """イントロフレームを生成"""
    bg1 = (10, 10, 30)
    bg2 = (20, 10, 50)
    accent = (0, 212, 255)
    total_frames = int(FPS * duration)
    
    f_title = get_font(68)
    f_sub = get_font(52)
    f_date = get_font(40)
    f_count = get_font(46)
    
    for frame_num in range(total_frames):
        t = frame_num / FPS
        img = Image.new('RGB', (W, H), bg1)
        draw = ImageDraw.Draw(img)
        
        # Gradient
        shift = int(50 * math.sin(t * 1.0))
        bg2_anim = tuple(min(255, max(0, c + shift)) for c in bg2)
        gradient_bg(draw, bg1, bg2_anim)
        
        # Decorative
        for i in range(5):
            cx = int(W * (0.1 + 0.2 * i) + 60 * math.sin(t * (0.5 + i * 0.3)))
            cy = int(H * 0.08 + 40 * math.cos(t * (0.4 + i * 0.25)))
            r = 100 + int(30 * math.sin(t * 2 + i))
            overlay_color = tuple(min(255, c + 15) for c in bg1)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=overlay_color)
        
        # Progress
        bar_w = int(W * t / duration)
        draw.rectangle([0, 0, bar_w, 8], fill=accent)
        
        if t >= 0.2:
            a = min(1.0, (t - 0.2) / 0.4)
            draw_text_centered(draw, '🔥', 500, get_font(150), tuple(int(c*a) for c in accent), shadow=False)
        
        if t >= 0.5:
            a = min(1.0, (t - 0.5) / 0.4)
            draw_text_centered(draw, '今日バズってること', 720, f_title, tuple(int(c*a) for c in (255,255,255)))
        
        if t >= 0.8:
            a = min(1.0, (t - 0.8) / 0.4)
            draw_text_centered(draw, '全部まとめ', 820, f_sub, tuple(int(c*a) for c in accent))
        
        if t >= 1.0:
            a = min(1.0, (t - 1.0) / 0.4)
            draw_text_centered(draw, date_str, 960, f_date, tuple(int(c*a) for c in (200,200,200)))
        
        if t >= 1.3:
            a = min(1.0, (t - 1.3) / 0.3)
            draw_text_centered(draw, f'TOP {trend_count} トレンド', 1060, f_count, tuple(int(c*a) for c in (255,220,0)))
        
        img.save(os.path.join(out_dir, f'frame_{frame_num:04d}.png'))

def make_outro_frames(out_dir, duration=3.0):
    """アウトロフレームを生成"""
    bg1 = (10, 10, 30)
    bg2 = (20, 10, 50)
    accent = (0, 212, 255)
    total_frames = int(FPS * duration)
    
    f_main = get_font(64)
    f_sub = get_font(46)
    f_cta = get_font(52)
    
    for frame_num in range(total_frames):
        t = frame_num / FPS
        img = Image.new('RGB', (W, H), bg1)
        draw = ImageDraw.Draw(img)
        
        shift = int(40 * math.sin(t * 0.8))
        bg2_anim = tuple(min(255, max(0, c + shift)) for c in bg2)
        gradient_bg(draw, bg1, bg2_anim)
        
        bar_w = int(W * t / duration)
        draw.rectangle([0, 0, bar_w, 8], fill=accent)
        
        if t >= 0.3:
            a = min(1.0, (t - 0.3) / 0.4)
            draw_text_centered(draw, '以上、今日のトレンドでした！', 700, f_main, tuple(int(c*a) for c in (255,255,255)))
        
        if t >= 0.8:
            a = min(1.0, (t - 0.8) / 0.3)
            draw_text_centered(draw, 'チャンネル登録お願いします 🙏', 850, f_sub, tuple(int(c*a) for c in accent))
        
        if t >= 1.2:
            a = min(1.0, (t - 1.2) / 0.3)
            pulse = 0.05 * math.sin(t * 8)
            draw_text_centered(draw, '💾 保存 & シェアお願いします', 1020, f_cta, tuple(int(c*a) for c in (255, 200, 0)))
        
        if t >= 1.6:
            a = min(1.0, (t - 1.6) / 0.4)
            draw_text_centered(draw, '🤖 AI Assistant Channel', 1820, get_font(32), tuple(int(150*a) for _ in range(3)), shadow=False)
        
        img.save(os.path.join(out_dir, f'frame_{frame_num:04d}.png'))

def generate_tts(text, output_path, rate=200):
    """macOS say コマンドでTTS音声を生成"""
    aiff_path = output_path.replace('.mp3', '.aiff')
    result = subprocess.run(
        ['say', '-v', 'Kyoko', '-r', str(rate), text, '-o', aiff_path],
        capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(f'TTS failed: {result.stderr}')
    
    # Convert to mp3
    result2 = subprocess.run(
        ['ffmpeg', '-y', '-i', aiff_path, '-q:a', '4', output_path],
        capture_output=True
    )
    if result2.returncode != 0:
        raise RuntimeError(f'Audio convert failed: {result2.stderr}')
    
    os.remove(aiff_path)
    return output_path

def frames_to_video(frames_dir, audio_path, output_path, duration):
    """フレーム + 音声 → MP4"""
    cmd = [
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-i', os.path.join(frames_dir, 'frame_%04d.png'),
        '-i', audio_path,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-movflags', '+faststart',
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f'ffmpeg failed: {result.stderr.decode()}')
    return output_path

def silent_audio(duration, output_path):
    """無音音声を生成"""
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo',
        '-t', str(duration),
        '-q:a', '4',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)

def frames_to_video_no_audio(frames_dir, output_path, total_frames):
    """音声なしで動画生成（後でconcatするため）"""
    cmd = [
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-i', os.path.join(frames_dir, 'frame_%04d.png'),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f'ffmpeg failed: {result.stderr.decode()}')

def concat_av_segments(segments, output_path):
    """セグメント（動画+音声ペア）を結合"""
    # Build complex filter
    n = len(segments)
    inputs = []
    for i, (vid, aud) in enumerate(segments):
        inputs += ['-i', vid, '-i', aud]
    
    filter_parts = []
    for i in range(n):
        vi = i * 2
        ai = i * 2 + 1
        filter_parts.append(f'[{vi}:v][{ai}:a]')
    
    concat_filter = ''.join(filter_parts) + f'concat=n={n}:v=1:a=1[v][a]'
    
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', concat_filter,
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f'concat failed: {result.stderr.decode()}')


def main(trends=None, dry_run=False):
    today = datetime.now().strftime('%Y-%m-%d')
    date_str = datetime.now().strftime('%m/%d')
    
    # Use provided trends data or fetch from Google Trends
    if trends is None:
        print("Error: No trends data provided. Pass a JSON file.", file=sys.stderr)
        sys.exit(1)
    
    print(f"=== Daily Trend Video: {today} ===")
    print(f"Trends: {len(trends)} items")
    
    work_dir = tempfile.mkdtemp(prefix='trend_video_')
    print(f"Work dir: {work_dir}")
    
    try:
        segments = []  # list of (video_path, audio_path)
        
        # --- INTRO ---
        print("\n[1/3] Generating intro...")
        intro_frames_dir = os.path.join(work_dir, 'intro_frames')
        os.makedirs(intro_frames_dir)
        make_intro_frames(intro_frames_dir, date_str, len(trends), duration=3.0)
        
        intro_nar = f"{date_str}、今日のトレンドを{len(trends)}本まとめてお届けします！"
        intro_audio = os.path.join(work_dir, 'intro.mp3')
        if not dry_run:
            generate_tts(intro_nar, intro_audio)
        else:
            silent_audio(3.0, intro_audio)
        
        intro_video = os.path.join(work_dir, 'intro.mp4')
        if not dry_run:
            frames_to_video(intro_frames_dir, intro_audio, intro_video, 3.0)
        
        segments.append((intro_video, intro_audio))
        
        # --- TREND SLIDES ---
        for i, trend in enumerate(trends):
            print(f"\n[{i+2}/{len(trends)+2}] Trend: {trend['keyword']}")
            
            slide_dir = os.path.join(work_dir, f'trend_{i}_frames')
            os.makedirs(slide_dir)
            
            slide_duration = 5.5
            make_frames_for_trend(trend, slide_dir, slide_duration=slide_duration)
            
            narration = trend['narration']
            nar_path = os.path.join(work_dir, f'trend_{i}.mp3')
            if not dry_run:
                generate_tts(narration, nar_path, rate=230)
            else:
                silent_audio(slide_duration, nar_path)
            
            seg_video = os.path.join(work_dir, f'trend_{i}.mp4')
            if not dry_run:
                frames_to_video(slide_dir, nar_path, seg_video, slide_duration)
            
            segments.append((seg_video, nar_path))
        
        # --- OUTRO ---
        print(f"\n[{len(trends)+2}/{len(trends)+2}] Generating outro...")
        outro_frames_dir = os.path.join(work_dir, 'outro_frames')
        os.makedirs(outro_frames_dir)
        make_outro_frames(outro_frames_dir, duration=3.0)
        
        outro_nar = "以上、今日のトレンドでした！保存とシェアをしてもらえると嬉しいです！チャンネル登録もよろしくお願いします！"
        outro_audio = os.path.join(work_dir, 'outro.mp3')
        if not dry_run:
            generate_tts(outro_nar, outro_audio)
        else:
            silent_audio(3.0, outro_audio)
        
        outro_video = os.path.join(work_dir, 'outro.mp4')
        if not dry_run:
            frames_to_video(outro_frames_dir, outro_audio, outro_video, 3.0)
        
        segments.append((outro_video, outro_audio))
        
        if dry_run:
            print("\n[DRY RUN] Skipping video render and upload.")
            return
        
        # --- CONCAT ---
        print("\nConcatenating segments...")
        output_path = os.path.join(
            os.path.dirname(SCRIPT_DIR),
            'youtube',
            f'trend_{today}.mp4'
        )
        concat_av_segments(segments, output_path)
        
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"\nOutput: {output_path} ({size_mb:.1f} MB)")
        
        # --- UPLOAD ---
        print("\nUploading to YouTube...")
        keywords = '、'.join(t['keyword'] for t in trends)
        title = f'【30秒】今日バズってること全部まとめ {date_str}🔥'
        description = f"""今日（{today}）のGoogleトレンドTOP{len(trends)}をまとめました！

📌 今日のトレンド:
{chr(10).join(f'{i+1}. {t["keyword"]}（{t.get("volume","?")}回検索）' for i, t in enumerate(trends))}

このチャンネルはAIが完全自動で運営しています🤖
毎日トレンドをお届け！チャンネル登録お願いします！

#トレンド #{date_str.replace('/', '')} #GoogleTrends #急上昇 #話題
"""
        tags = ['トレンド', 'Google急上昇', '今日の話題', 'ニュース', 'まとめ', 'AIチャンネル']
        
        upload_script = os.path.join(SCRIPT_DIR, 'upload.py')
        result = subprocess.run(
            [sys.executable, upload_script, output_path, title, description,
             ','.join(tags), '--short'],
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✅ Upload successful!")
        else:
            print(f"\n❌ Upload failed (code {result.returncode})")
            sys.exit(1)
    
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        print("Cleaned up temp files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily Trend Video Generator")
    parser.add_argument("--dry-run", "-d", action="store_true",
                        help="Perform all steps except video rendering and YouTube upload.")
    parser.add_argument("trends_file", nargs="?",
                        help="Path to a JSON file containing trends data (optional).")

    args = parser.parse_args()

    trends_data = None
    if args.trends_file:
        if os.path.exists(args.trends_file):
            with open(args.trends_file) as f:
                trends_data = json.load(f)
        else:
            print(f"Error: Trends file not found at {args.trends_file}", file=sys.stderr)
            sys.exit(1)

    main(trends=trends_data, dry_run=args.dry_run)
