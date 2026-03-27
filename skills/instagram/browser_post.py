#!/usr/bin/env python3
"""Post an image to Instagram via existing CDP browser session."""
import sys
import time
from playwright.sync_api import sync_playwright

def post_to_instagram(image_path: str, caption: str):
    with sync_playwright() as p:
        # Connect to existing OpenClaw browser
        browser = p.chromium.connect_over_cdp("http://localhost:18800")
        context = browser.contexts[0]
        
        # Find Instagram tab or create one
        page = None
        for pg in context.pages:
            if "instagram.com" in pg.url:
                page = pg
                break
        if not page:
            page = context.new_page()
            page.goto("https://www.instagram.com/aiinsta26/")
            page.wait_for_load_state("networkidle")
        
        # Close any existing dialogs first
        try:
            close_btn = page.locator('[aria-label="閉じる"]')
            if close_btn.count() > 0:
                close_btn.first.click()
                time.sleep(1)
        except:
            pass
        
        # Click "新しい投稿 作成" button in sidebar
        try:
            new_post = page.locator('svg[aria-label="新規投稿"]').first
            new_post.click()
        except:
            # Try alternate: the link/button with 新規投稿
            new_post = page.locator('[aria-label="新規投稿を作成"]').first
            if new_post.count() == 0:
                # Try clicking the sidebar create button
                page.locator('text=作成').first.click()
            else:
                new_post.click()
        
        time.sleep(2)
        
        # Upload file via file chooser
        with page.expect_file_chooser() as fc_info:
            page.locator('text=コンピューターから選択').click()
        file_chooser = fc_info.value
        file_chooser.set_files(image_path)
        
        time.sleep(3)
        print("Image uploaded, waiting for preview...")
        
        # Click 次へ (Next) - may need to click twice (crop -> filter -> caption)
        for step in range(3):
            try:
                next_btn = page.locator('text=次へ').first
                if next_btn.is_visible():
                    next_btn.click()
                    time.sleep(2)
                    print(f"Clicked 次へ (step {step+1})")
            except:
                pass
        
        # Now we should be on the caption screen
        # Type caption
        time.sleep(1)
        try:
            caption_area = page.locator('[aria-label="キャプションを入力…"]').first
            if not caption_area.is_visible():
                caption_area = page.locator('[aria-label="キャプションを入力"]').first
            caption_area.click()
            caption_area.fill(caption)
            print("Caption entered")
        except Exception as e:
            print(f"Caption input error: {e}")
            # Try contenteditable div
            try:
                caption_area = page.locator('[contenteditable="true"]').first
                caption_area.click()
                caption_area.fill(caption)
                print("Caption entered (contenteditable)")
            except Exception as e2:
                print(f"Caption fallback error: {e2}")
        
        time.sleep(1)
        
        # Click シェア (Share)
        try:
            share_btn = page.locator('text=シェア').first
            if not share_btn.is_visible():
                share_btn = page.locator('text=シェアする').first
            share_btn.click()
            print("Clicked シェア!")
        except Exception as e:
            print(f"Share button error: {e}")
            return False
        
        # Wait for completion
        time.sleep(5)
        
        # Check for success message
        try:
            page.wait_for_selector('text=投稿がシェアされました', timeout=15000)
            print("✅ Post shared successfully!")
            return True
        except:
            print("⚠️ Could not confirm success, check manually")
            return True
        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 browser_post.py <image_path> <caption>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    caption = sys.argv[2]
    post_to_instagram(image_path, caption)
