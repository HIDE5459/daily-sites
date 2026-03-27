#!/usr/bin/env python3
"""Just upload a file via the already-open Instagram dialog."""
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
        
        print(f"Tab: {page.url}")
        
        # File chooser: click button and intercept
        with page.expect_file_chooser(timeout=10000) as fc_info:
            page.locator('button:text("コンピューターから選択")').click(timeout=5000)
        
        fc = fc_info.value
        fc.set_files(image_path)
        print("✅ File uploaded!")

if __name__ == "__main__":
    main(sys.argv[1])
