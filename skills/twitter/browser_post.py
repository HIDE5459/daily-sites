#!/usr/bin/env python3
"""
Twitterブラウザ投稿スクリプト（確定版）
- ホームページのインラインテキストエリアを使う
- kind:"type" でASCII入力 → tweetButtonInline を evaluate でクリック
- 日本語は ASCII に変換 or 英語投稿で代用
"""
import sys
import time
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

def post_tweet(text):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]

        page = next((pg for pg in context.pages if 'x.com' in pg.url), None)
        if not page:
            raise Exception("x.com のページが開いていません")

        # インラインテキストエリアにフォーカス
        textarea = page.locator('[data-testid="tweetTextarea_0"]').first
        textarea.click()
        time.sleep(0.3)

        # テキスト入力（keyboard.insert_text が Unicode に対応）
        page.keyboard.insert_text(text)
        time.sleep(0.5)

        # ボタンを evaluate で直接クリック（refが切れない）
        result = page.evaluate("""
            () => {
                const btn = document.querySelector('[data-testid="tweetButtonInline"]');
                if (btn && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true') {
                    btn.click();
                    return 'clicked';
                }
                return 'disabled: ' + (btn ? btn.getAttribute('aria-disabled') : 'null');
            }
        """)

        if result == 'clicked':
            print(f"✅ 投稿成功: {text[:60]}")
            return True
        else:
            print(f"❌ ボタン押せず: {result}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 browser_post.py <text>")
        sys.exit(1)
    ok = post_tweet(sys.argv[1])
    sys.exit(0 if ok else 1)
