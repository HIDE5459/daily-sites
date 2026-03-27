#!/usr/bin/env python3
"""Instagram full post via Playwright CDP - open dialog, upload, caption, share."""
import sys, time
from playwright.sync_api import sync_playwright

def main(image_path, caption):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:18800")
        ctx = browser.contexts[0]
        
        # Find or open Instagram tab
        page = None
        for pg in ctx.pages:
            if "instagram.com" in pg.url:
                page = pg
                break
        
        if not page:
            page = ctx.new_page()
            page.goto("https://www.instagram.com/aiinsta26/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
        
        print(f"Tab: {page.url}")
        
        # Step 1: Click "新しい投稿" (Create) in sidebar
        print("Step 1: Opening create dialog...")
        create_btn = page.locator('a:has-text("作成"), a:has-text("新しい投稿"), [aria-label="新しい投稿"]')
        if create_btn.count() > 0:
            create_btn.first.click(timeout=5000)
        else:
            # Try SVG icon approach
            page.locator('svg[aria-label="新しい投稿"]').click(timeout=5000)
        time.sleep(2)
        
        # Step 2: Upload file
        print("Step 2: Uploading file...")
        with page.expect_file_chooser(timeout=10000) as fc_info:
            select_btn = page.locator('button:has-text("コンピューターから選択")')
            if select_btn.count() > 0:
                select_btn.click(timeout=5000)
            else:
                # Fallback: click the dialog area
                page.locator('text=コンピューターから選択').click(timeout=5000)
        fc = fc_info.value
        fc.set_files(image_path)
        print("✅ File uploaded!")
        time.sleep(3)
        
        # Step 3: Click 次へ (crop -> filter)
        print("Step 3: Next (crop)...")
        page.locator('div[role="button"]:has-text("次へ"), button:has-text("次へ")').first.click(timeout=5000)
        time.sleep(2)
        
        # Step 4: Click 次へ (filter -> caption)
        print("Step 4: Next (filter)...")
        page.locator('div[role="button"]:has-text("次へ"), button:has-text("次へ")').first.click(timeout=5000)
        time.sleep(2)
        
        # Step 5: Type caption
        print("Step 5: Typing caption...")
        caption_area = page.locator('div[aria-label="キャプションを入力…"], textarea[aria-label="キャプションを入力…"], [contenteditable="true"]')
        if caption_area.count() > 0:
            caption_area.first.click()
            time.sleep(0.5)
            # Type line by line to handle newlines
            for i, line in enumerate(caption.split('\n')):
                if i > 0:
                    page.keyboard.press('Enter')
                page.keyboard.type(line, delay=20)
        else:
            print("⚠️ Caption area not found, trying fallback...")
            page.locator('div[role="textbox"]').first.click()
            page.keyboard.type(caption.replace('\n', ' '), delay=20)
        time.sleep(1)
        
        # Step 6: Click シェア
        print("Step 6: Sharing...")
        share_btn = page.locator('div[role="button"]:has-text("シェア"), button:has-text("シェア")')
        share_btn.first.click(timeout=5000)
        time.sleep(20)
        
        # Check for success
        success = page.locator('text=投稿をシェアしました, text=シェアされました')
        if success.count() > 0:
            print("🎉 Post shared successfully!")
            # Close dialog
            close_btn = page.locator('button:has-text("閉じる"), div[role="button"]:has-text("閉じる")')
            if close_btn.count() > 0:
                close_btn.first.click()
        else:
            print("⚠️ Could not confirm success, check manually")
            # Take screenshot for debug
            page.screenshot(path="/Users/hide/.openclaw/workspace/instagram/debug_post.png")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python full_post.py <image_path> <caption>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
