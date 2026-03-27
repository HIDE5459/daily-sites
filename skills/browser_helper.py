#!/usr/bin/env python3
"""ブラウザ自動リカバリヘルパー。落ちたら再起動して続行。"""
import subprocess, time, requests

def ensure_browser(max_retries=3):
    """ブラウザが生きてるか確認。死んでたら再起動。"""
    for i in range(max_retries):
        try:
            r = requests.get("http://localhost:18800/json/version", timeout=3)
            if r.ok:
                return True
        except:
            pass
        print(f"Browser down, restarting (attempt {i+1}/{max_retries})...")
        subprocess.run(["openclaw", "browser", "--browser-profile", "openclaw", "start"],
                       capture_output=True, timeout=20)
        time.sleep(5)
    return False

def get_page(playwright_browser, url=None):
    """ページ取得。なければ新規作成。URLあればナビゲート。"""
    ctx = playwright_browser.contexts[0]
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    if url:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
    return page

def safe_run(fn, max_retries=2):
    """関数を実行。ブラウザが落ちたらリカバリして再実行。"""
    for i in range(max_retries):
        try:
            return fn()
        except Exception as e:
            err = str(e)
            if "closed" in err.lower() or "target" in err.lower() or "timeout" in err.lower():
                print(f"Browser error (attempt {i+1}): {err[:100]}")
                ensure_browser()
                time.sleep(3)
            else:
                raise
    raise RuntimeError(f"Failed after {max_retries} retries")
