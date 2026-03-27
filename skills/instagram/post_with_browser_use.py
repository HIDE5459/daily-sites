#!/usr/bin/env python3
"""
Instagram自動投稿 - Browser Use Agent版
CDP直接接続でOpenClawブラウザを操作
"""
import asyncio
import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime

# env
WORKSPACE = Path(__file__).parent.parent.parent
env_path = Path(__file__).parent / ".env"
for line in env_path.read_text().strip().split("\n"):
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

CDP_URL = "http://127.0.0.1:18800"
LOG_FILE = WORKSPACE / "instagram" / "post_log.json"
IMAGES_DIR = WORKSPACE / "instagram" / "images"

# 投稿ログ読み込み
def load_log():
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text())
        except:
            return []
    return []

def save_log(logs):
    LOG_FILE.write_text(json.dumps(logs, ensure_ascii=False, indent=2))

def get_next_image():
    """未投稿または最も古い画像を選ぶ"""
    logs = load_log()
    posted = {l.get("file", "") for l in logs if l.get("success")}
    images = sorted(IMAGES_DIR.glob("*.jpg")) + sorted(IMAGES_DIR.glob("*.png"))
    
    # 未投稿を優先
    for img in images:
        if img.name not in posted:
            return img
    
    # 全部投稿済みなら最も古いものを再投稿
    if images:
        return images[0]
    return None

def make_caption(filename: str) -> str:
    """ファイル名からキャプション生成"""
    name = Path(filename).stem.lower()
    
    if "kyoto" in name or "京都" in name:
        return "🎋 AIが旅する京都\n嵐山の竹林、静寂の中で時間を忘れる✨\n\n#AITravel #京都 #嵐山 #バーチャル旅行 #AI生成 #Japan"
    elif "beach" in name or "bikini" in name or "summer" in name:
        return "🏖️ AI的夏の1シーン\n海と空と、特別な時間🌊\n\n#夏 #AIモデル #AI生成 #PhotoAI #夏グラム"
    elif "night" in name or "dress" in name:
        return "🌙 夜景に溶け込む\n東京の夜は特別な輝きがある💜\n\n#夜景 #AIモデル #AI生成 #夜スタグラム"
    elif "idol" in name:
        return "✨ AIアイドルの日常\nどんな毎日も輝かせたい🎤\n\n#AIアイドル #AI生成 #PhotoAI #グラビア風"
    elif "travel" in name:
        return "🌍 AI Travelerが行く\n世界中を旅する夢、AIで叶えよう✈️\n\n#AITravel #バーチャル旅行 #AI生成 #旅スタグラム"
    else:
        return f"✨ AI Generated\n今日も素敵な1枚をお届け🎨\n\n#AI生成 #AIアート #PhotoAI #デジタルアート"

async def post_to_instagram(image_path: Path, caption: str) -> bool:
    """Browser Use AgentでInstagramに投稿"""
    try:
        from browser_use import Agent, Browser, BrowserProfile
        from langchain_anthropic import ChatAnthropic
    except ImportError as e:
        print(f"Import error: {e}")
        # フォールバック: 直接Playwrightで投稿
        return await post_direct_playwright(image_path, caption)
    
    profile = BrowserProfile(cdp_url=CDP_URL)
    browser = Browser(browser_profile=profile)
    
    llm = ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
    )
    
    task = f"""
Instagramに画像を投稿してください。

手順:
1. https://www.instagram.com/ を開く
2. 「+」ボタン（新規投稿）をクリック
3. 「コンピューターからアップロード」でファイルを選択: {image_path}
4. 「次へ」→「次へ」と進む
5. キャプション欄に以下を入力:
{caption}
6. 「シェア」ボタンをクリックして投稿

注意: すでにログイン済みです。ログイン操作は不要。
"""
    
    agent = Agent(task=task, llm=llm, browser=browser)
    try:
        result = await agent.run(max_steps=20)
        print(f"Agent result: {result}")
        return True
    except Exception as e:
        print(f"Agent error: {e}")
        return False
    finally:
        await browser.close()

async def post_direct_playwright(image_path: Path, caption: str) -> bool:
    """Playwright CDP接続で直接投稿（フォールバック）"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("playwright not available")
        return False
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        
        # Instagramタブを探す
        ctx = browser.contexts[0]
        page = None
        for pg in ctx.pages:
            if "instagram.com" in pg.url:
                page = pg
                break
        
        if not page:
            page = await ctx.new_page()
            await page.goto("https://www.instagram.com/", wait_until="networkidle")
            await page.wait_for_timeout(3000)
        
        try:
            # 新規投稿ボタン
            new_post = await page.query_selector('a[href="/create/style/"]') or \
                       await page.query_selector('svg[aria-label="新規投稿"]') or \
                       await page.query_selector('[aria-label="New post"]')
            
            if not new_post:
                # SVGアイコンの親要素を探す
                new_post = await page.query_selector('a[href*="create"]')
            
            if new_post:
                await new_post.click()
            else:
                # 直接URLへ
                await page.goto("https://www.instagram.com/")
                await page.wait_for_timeout(2000)
                await page.keyboard.press("c")  # ショートカット
            
            await page.wait_for_timeout(2000)
            
            # ファイルアップロード
            async with page.expect_file_chooser() as fc_info:
                # 「コンピューターからアップロード」ボタン探す
                upload_btn = await page.query_selector('button:has-text("コンピューターからアップロード")') or \
                             await page.query_selector('button:has-text("Select from computer")')
                if upload_btn:
                    await upload_btn.click()
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(str(image_path))
            await page.wait_for_timeout(3000)
            
            # 次へ × 2
            for _ in range(2):
                next_btn = await page.query_selector('div[role="button"]:has-text("次へ")') or \
                           await page.query_selector('button:has-text("Next")')
                if next_btn:
                    await next_btn.click()
                    await page.wait_for_timeout(2000)
            
            # キャプション入力
            caption_area = await page.query_selector('div[aria-label="キャプションを入力..."]') or \
                          await page.query_selector('div[aria-label="Write a caption..."]') or \
                          await page.query_selector('textarea[aria-label*="caption"]')
            
            if caption_area:
                await caption_area.click()
                await page.keyboard.type(caption, delay=30)
                await page.wait_for_timeout(1000)
            
            # シェア
            share_btn = await page.query_selector('div[role="button"]:has-text("シェア")') or \
                       await page.query_selector('button:has-text("Share")')
            if share_btn:
                await share_btn.click()
                await page.wait_for_timeout(5000)
                print(f"✅ Posted: {image_path.name}")
                return True
            else:
                print("❌ Share button not found")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback; traceback.print_exc()
            return False

async def main():
    image = get_next_image()
    if not image:
        print("No images to post")
        return
    
    caption = make_caption(image.name)
    print(f"📸 Posting: {image.name}")
    print(f"📝 Caption: {caption[:50]}...")
    
    success = await post_to_instagram(image, caption)
    
    # ログ記録
    logs = load_log()
    logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "filename": image.name,
        "caption": caption[:100],
        "success": success,
    })
    save_log(logs)
    
    print(f"{'✅ Success' if success else '❌ Failed'}")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
