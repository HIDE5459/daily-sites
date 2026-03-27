#!/usr/bin/env python3
"""Instagram auto-engagement: like posts on explore tags. Lightweight & fast."""
import subprocess, sys, time, random

subprocess.run(["openclaw","browser","--browser-profile","openclaw","start"], capture_output=True, timeout=15)
time.sleep(2)

from playwright.sync_api import sync_playwright

TAGS = ["aiart","aigenerated","aiphotography","aiinfluencer","digitalart",
        "midjourney","stablediffusion","fantasyart","aitravel","virtualtravel"]

def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:18800")
        page = browser.contexts[0].pages[0]
        
        tags = random.sample(TAGS, min(2, len(TAGS)))
        total = 0
        
        for tag in tags:
            try:
                page.goto(f"https://www.instagram.com/explore/tags/{tag}/",
                          wait_until="domcontentloaded", timeout=15000)
                time.sleep(3)
                
                links = page.locator("a[href*='/p/'], a[href*='/reel/']")
                count = min(4, links.count())
                
                for i in range(count):
                    try:
                        links.nth(i).click()
                        time.sleep(2)
                        like_btn = page.locator('[role="dialog"] svg[aria-label="いいね！"]')
                        if like_btn.count() > 0:
                            like_btn.first.click(timeout=3000)
                            total += 1
                            time.sleep(1)
                        page.keyboard.press("Escape")
                        time.sleep(0.5)
                    except:
                        try: page.keyboard.press("Escape")
                        except: pass
                        time.sleep(0.5)
                
                print(f"#{tag}: liked")
            except Exception as e:
                print(f"#{tag}: skip ({e})")
        
        print(f"Total liked: {total}")

if __name__ == "__main__":
    run()
