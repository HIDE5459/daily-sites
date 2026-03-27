#!/usr/bin/env python3
"""Set Instagram profile photo via CDP."""
import sys, time
from playwright.sync_api import sync_playwright

def main(image_path):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:18800")
        page = None
        for pg in browser.contexts[0].pages:
            if "instagram.com" in pg.url:
                page = pg
                break
        if not page:
            print("No Instagram tab!"); return
        
        # Navigate to edit profile if not already there
        if "/accounts/edit" not in page.url:
            page.goto("https://www.instagram.com/accounts/edit/")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
        
        # Click "写真を変更" and intercept file chooser
        with page.expect_file_chooser(timeout=10000) as fc_info:
            page.locator('button:has-text("写真を変更")').click()
        
        fc = fc_info.value
        fc.set_files(image_path)
        print("✅ Profile photo uploaded!")
        time.sleep(5)

if __name__ == "__main__":
    main(sys.argv[1])
