# Twitter投稿 ブラウザツール手順（確定版）

## 動作確認済み（2026-03-12）

### 手順
1. ブラウザ起動: `browser start profile=openclaw`
2. ナビゲート: `browser navigate url=https://x.com/home`
3. スナップショット: textbox "Post text" の ref を取得
4. クリック: `browser act kind=click ref=<textbox_ref>`
5. 入力: `browser act kind=type ref=<textbox_ref> text="..."`（ASCII英語のみ）
6. 投稿: `browser act kind=evaluate fn="() => { document.querySelector('[data-testid=\"tweetButtonInline\"]').click(); return 'ok'; }"`

### 注意
- 日本語テキストは `kind:type` 非対応 → 英語で投稿
- `slowly:true` は使うな（ブラウザクラッシュ）
- refは時間で切れる → 投稿クリックはevaluateで直接
- 外部Playwrightスクリプト（browser_post.py）はCDP競合でNG
