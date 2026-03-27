#!/usr/bin/env python3
"""Follow AI/travel accounts and like their posts via CDP."""
import time, random
from playwright.sync_api import sync_playwright

ACCOUNTS_TO_FOLLOW = [
    "higgsfield.ai",
    "midjourney",  
    "openaidalle",
    "beautifuldestinations",
    "earthpix",
    "discoverearth",
    "natgeotravel",
    "ai_images_daily",
    "aiartcommunity",
    "luxurytravel",
]

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:18800")
        context = browser.contexts[0]
        
        # Find or create Instagram tab
        page = None
        for pg in context.pages:
            if "instagram.com" in pg.url:
                page = pg
                break
        if not page:
            page = context.new_page()
        
        followed = []
        liked = []
        
        for account in ACCOUNTS_TO_FOLLOW:
            try:
                page.goto(f"https://www.instagram.com/{account}/", timeout=15000)
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(2)
                
                # Check if account exists
                if "ページが見つかりません" in page.content() or "Sorry, this page" in page.content():
                    print(f"❌ {account} not found")
                    continue
                
                # Click follow button
                follow_btn = page.locator('button:has-text("フォロー")').first
                if follow_btn.is_visible(timeout=3000):
                    text = follow_btn.text_content()
                    if text and "フォロー中" not in text and "リクエスト" not in text:
                        follow_btn.click()
                        followed.append(account)
                        print(f"✅ Followed @{account}")
                        time.sleep(random.uniform(2, 4))
                    else:
                        print(f"⏭️ Already following @{account}")
                
                # Like first post
                try:
                    first_post = page.locator('main a[href*="/p/"], main a[href*="/reel/"]').first
                    if first_post.is_visible(timeout=3000):
                        first_post.click()
                        time.sleep(2)
                        
                        like_btn = page.locator('svg[aria-label="いいね！"]').first
                        if like_btn.is_visible(timeout=3000):
                            like_btn.click()
                            liked.append(account)
                            print(f"❤️ Liked post from @{account}")
                            time.sleep(random.uniform(1, 3))
                        
                        # Close post dialog
                        close_btn = page.locator('svg[aria-label="閉じる"]').first
                        if close_btn.is_visible(timeout=2000):
                            close_btn.click()
                            time.sleep(1)
                except Exception as e:
                    print(f"Like error for {account}: {e}")
                
                # Random delay between accounts
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"Error with {account}: {e}")
        
        print(f"\n📊 Results: Followed {len(followed)}, Liked {len(liked)}")
        print(f"Followed: {', '.join(followed)}")
        print(f"Liked: {', '.join(liked)}")

if __name__ == "__main__":
    main()
