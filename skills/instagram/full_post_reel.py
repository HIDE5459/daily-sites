#!/usr/bin/env python3
"""Instagram reel post via Playwright CDP - handles video upload."""
import sys, time
from playwright.sync_api import sync_playwright

def main(video_path, caption):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:18800")
        ctx = browser.contexts[0]
        
        page = None
        for pg in ctx.pages:
            if "instagram.com" in pg.url:
                page = pg
                break
        
        if not page:
            page = ctx.new_page()
            page.goto("https://www.instagram.com/aiinsta26/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
        
        print(f"Tab: {page.url}")
        
        # Step 1: Click create
        print("Step 1: Opening create dialog...")
        try:
            page.locator('a:has-text("作成")').first.click(timeout=5000)
        except:
            try:
                page.locator('svg[aria-label="新しい投稿"]').click(timeout=5000)
            except:
                page.locator('a[href="#"]:has-text("作成")').click(timeout=5000)
        time.sleep(3)
        
        # Step 2: Upload video file
        print("Step 2: Uploading video...")
        with page.expect_file_chooser(timeout=15000) as fc_info:
            page.locator('button:has-text("コンピューターから選択")').click(timeout=5000)
        fc = fc_info.value
        fc.set_files(video_path)
        print("✅ Video uploaded!")
        time.sleep(8)  # Video processing takes longer
        
        # Step 3: Click 次へ (crop/trim)
        print("Step 3: Next (trim)...")
        page.locator('div[role="button"]:has-text("次へ"), button:has-text("次へ")').first.click(timeout=10000)
        time.sleep(3)
        
        # Step 4: Click 次へ (filter -> caption) - may or may not appear
        print("Step 4: Next (filter)...")
        try:
            page.locator('div[role="button"]:has-text("次へ"), button:has-text("次へ")').first.click(timeout=5000)
            time.sleep(2)
        except:
            print("  (no filter step, continuing...)")
        
        # Step 5: Type caption
        print("Step 5: Typing caption...")
        try:
            caption_area = page.locator('div[aria-label="キャプションを入力…"]')
            if caption_area.count() == 0:
                caption_area = page.locator('[contenteditable="true"]')
            caption_area.first.click()
            time.sleep(0.5)
            for i, line in enumerate(caption.split('\n')):
                if i > 0:
                    page.keyboard.press('Enter')
                page.keyboard.type(line, delay=15)
        except Exception as e:
            print(f"  Caption error: {e}")
        time.sleep(1)
        
        # Step 6: Click シェア
        print("Step 6: Sharing...")
        page.locator('div[role="button"]:has-text("シェア"), button:has-text("シェア")').first.click(timeout=5000)
        
        # Wait longer for video processing
        print("Waiting for video processing...")
        time.sleep(30)
        
        success = page.locator('text=リール動画がシェアされました, text=投稿をシェアしました')
        if success.count() > 0:
            print("🎉 Reel shared successfully!")
            try:
                page.locator('button:has-text("閉じる")').first.click(timeout=3000)
            except:
                pass
        else:
            print("⚠️ Check manually - may still be processing")
            page.screenshot(path="/Users/hide/.openclaw/workspace/instagram/debug_reel.png")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python full_post_reel.py <video_path> <caption>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
