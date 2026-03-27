#!/usr/bin/env python3
"""Upload image to Instagram using CDP connection to existing browser."""
import sys
import time
from playwright.sync_api import sync_playwright

def main(image_path, caption):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:18800")
        context = browser.contexts[0]
        
        page = None
        for pg in context.pages:
            if "instagram.com" in pg.url:
                page = pg
                break
        
        if not page:
            page = context.new_page()
            page.goto("https://www.instagram.com/aiinsta26/")
            page.wait_for_load_state("networkidle")
        
        print(f"Tab: {page.url}")
        
        # Click the + (create) button in sidebar
        create_btn = page.locator('svg[aria-label="新規投稿"]')
        if create_btn.count() == 0:
            # Try the sidebar link with "作成"
            create_btn = page.locator('a[href="#"]').filter(has=page.locator('svg'))
            # Just click the + icon in sidebar - it's the 8th link roughly
            # Let's use a more reliable selector
            create_btn = page.locator('[class*="x1i10hfl"]').filter(has_text="作成")
        
        # Most reliable: use the aria-label on the SVG
        print("Looking for create button...")
        
        # Use file chooser approach: set up listener BEFORE triggering
        with page.expect_file_chooser(timeout=15000) as fc_info:
            # Click the sidebar create/new post button, then click "コンピューターから選択"
            # First open the create dialog
            page.evaluate("""
                // Find and click the "新規投稿を作成" or create button
                const svgs = document.querySelectorAll('svg[aria-label]');
                for (const svg of svgs) {
                    const label = svg.getAttribute('aria-label');
                    if (label && (label.includes('新規投稿') || label.includes('作成'))) {
                        svg.closest('a, button, div[role="button"]').click();
                        break;
                    }
                }
            """)
            time.sleep(2)
            
            # Now click "コンピューターから選択"
            page.locator('button').filter(has_text="コンピューターから選択").click()
        
        file_chooser = fc_info.value
        file_chooser.set_files(image_path)
        print("✅ File selected!")
        time.sleep(3)
        
        # Screenshot to see state
        page.screenshot(path="/tmp/ig_debug1.png")
        print("Debug screenshot saved")
        
        # Click 次へ buttons
        for i in range(3):
            time.sleep(2)
            try:
                # Try multiple selectors for "次へ" button
                nxt = page.get_by_role("button", name="次へ")
                if nxt.count() > 0 and nxt.first.is_visible():
                    nxt.first.click()
                    print(f"Clicked 次へ ({i+1})")
                    continue
            except:
                pass
            
            # Try div with text
            try:
                nxt = page.locator('div[role="button"]:has-text("次へ")')
                if nxt.count() > 0:
                    nxt.first.click()
                    print(f"Clicked 次へ div ({i+1})")
            except:
                print(f"No 次へ found at step {i+1}")
        
        time.sleep(2)
        page.screenshot(path="/tmp/ig_debug2.png")
        
        # Enter caption
        try:
            cap = page.locator('[aria-label*="キャプション"]').first
            cap.click()
            time.sleep(0.5)
            page.keyboard.type(caption, delay=10)
            print("✅ Caption entered")
        except Exception as e:
            print(f"Caption error: {e}")
            try:
                cap = page.locator('div[contenteditable="true"]').first
                cap.click()
                time.sleep(0.5)
                page.keyboard.type(caption, delay=10)
                print("✅ Caption entered (fallback)")
            except Exception as e2:
                print(f"Caption fallback error: {e2}")
        
        time.sleep(1)
        
        # Click シェア
        try:
            share = page.get_by_role("button", name="シェア")
            if share.count() > 0:
                share.first.click()
                print("✅ Clicked シェア!")
            else:
                share = page.locator('div[role="button"]:has-text("シェアする")')
                share.first.click()
                print("✅ Clicked シェアする!")
        except Exception as e:
            print(f"Share error: {e}")
            page.screenshot(path="/tmp/ig_debug3.png")
        
        # Wait for success
        time.sleep(10)
        try:
            success = page.locator('text=投稿がシェアされました')
            if success.count() > 0:
                print("🎉 Post shared successfully!")
            else:
                print("⚠️ Check browser for result")
        except:
            print("⚠️ Check browser for result")
        
        page.screenshot(path="/tmp/ig_debug_final.png")

if __name__ == "__main__":
    img = sys.argv[1]
    cap = sys.argv[2]
    main(img, cap)
