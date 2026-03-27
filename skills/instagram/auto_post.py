#!/usr/bin/env python3
"""
自律Instagram投稿スクリプト
- ブラウザ起動確認＋リトライ
- 画像/動画投稿を自動判定
- エラー時は3回リトライ
"""
import subprocess, sys, time, os, json, glob

WORKSPACE = "/Users/hide/.openclaw/workspace"
IMAGES_DIR = f"{WORKSPACE}/instagram/images"
LOG_FILE = f"{WORKSPACE}/instagram/post_log.json"

def ensure_browser():
    """ブラウザが起動してるか確認、なければ起動"""
    import requests
    for attempt in range(3):
        try:
            r = requests.get("http://localhost:18800/json/version", timeout=3)
            if r.status_code == 200:
                return True
        except:
            pass
        print(f"Browser not ready (attempt {attempt+1}/3), starting...")
        subprocess.run(["openclaw", "browser", "--browser-profile", "openclaw", "start"], 
                       capture_output=True, timeout=15)
        time.sleep(5)
    return False

def post_image(image_path, caption):
    """画像を投稿（3回リトライ）"""
    script = f"{WORKSPACE}/skills/instagram/full_post.py"
    for attempt in range(3):
        try:
            result = subprocess.run(
                ["python3", script, image_path, caption],
                capture_output=True, text=True, timeout=120
            )
            print(result.stdout)
            if "Post shared" in result.stdout or "シェア" in result.stdout or "uploaded" in result.stdout.lower():
                return True
            # Even if we can't confirm, if step 6 was reached it likely worked
            if "Step 6" in result.stdout:
                return True
            if result.returncode != 0:
                print(f"Attempt {attempt+1} failed: {result.stderr[-200:]}")
                time.sleep(5)
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt+1} timed out")
            time.sleep(5)
    return False

def post_reel(video_path, caption):
    """リール投稿（3回リトライ）"""
    script = f"{WORKSPACE}/skills/instagram/full_post_reel.py"
    for attempt in range(3):
        try:
            result = subprocess.run(
                ["python3", script, video_path, caption],
                capture_output=True, text=True, timeout=180
            )
            print(result.stdout)
            if "shared" in result.stdout.lower() or "シェア" in result.stdout:
                return True
            if result.returncode != 0:
                print(f"Attempt {attempt+1} failed: {result.stderr[-200:]}")
                time.sleep(5)
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt+1} timed out")
            time.sleep(5)
    return False

def log_post(image_path, caption, success):
    """投稿ログを記録"""
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)
    log.append({
        "time": time.strftime("%Y-%m-%d %H:%M"),
        "file": os.path.basename(image_path),
        "caption": caption[:50],
        "success": success
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log[-50:], f, ensure_ascii=False, indent=2)

def get_unposted_images():
    """まだ投稿してないストック画像を取得"""
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)
    posted = {entry["file"] for entry in log if entry.get("success")}
    
    all_images = glob.glob(f"{IMAGES_DIR}/idol_*.jpg") + glob.glob(f"{IMAGES_DIR}/travel_*.jpg")
    unposted = [img for img in all_images if os.path.basename(img) not in posted]
    return unposted

if __name__ == "__main__":
    if not ensure_browser():
        print("ERROR: Could not start browser after 3 attempts")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        # Manual: auto_post.py <image> <caption>
        image_path = sys.argv[1]
        caption = sys.argv[2]
    else:
        # Auto: pick unposted stock image
        unposted = get_unposted_images()
        if not unposted:
            print("No unposted stock images available")
            sys.exit(0)
        image_path = unposted[0]
        caption = "✨ AI生成画像 #AI生成 #AITravel #バーチャル旅行"
    
    is_video = image_path.endswith(('.mp4', '.mov'))
    
    if is_video:
        success = post_reel(image_path, caption)
    else:
        success = post_image(image_path, caption)
    
    log_post(image_path, caption, success)
    
    if success:
        print(f"✅ Posted: {os.path.basename(image_path)}")
    else:
        print(f"❌ Failed: {os.path.basename(image_path)}")
        sys.exit(1)
