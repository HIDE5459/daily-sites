# MEMORY.md - マギの長期記憶

## かんさんについて
- MacBook Air M1 8GB / iPhone SE 3
- Tailscale使用、ブラウザはBrave
- 日本語メイン、丁寧めの口調が好み
- プロジェクトを並行で進めたい人（グループ＝プロジェクトワークスペース）
- 自律運営を望む（「任せました」「自分でやっていってよ」）
- 反感を買うコンテンツNG、フェイク人物NG

## プロジェクト

### ミャクミャクウォッチャー
- 大阪万博ミャクミャク情報収集iOSアプリ
- Swift + SwiftUI + Firebase (Firestore, FCM, Cloud Functions)
- パス: `~/Desktop/Projects/20260210myakumyaku`
- TestFlight配信中（build #8）
- Team ID: 96G4346HTN / Bundle ID: com.myakumyaku.watcher

### YouTube (@ainews-mw1xf / AINEWS-sm)
- 登録者: 5人 / 総再生: 5,882回 / 動画: 10本
- トップ: 世界旅行(1,891回/48h) → AI運営(279) → CLAUDE.md(203)
- **ビジュアル系が技術系の10倍伸びる** ← 最重要学び
- 水中ホテル動画は視聴率4.9%（冒頭フック致命的に弱い）
- Remotionパイプライン稼働中（1080x1920縦型）
- daily_trend_video.py: Googleトレンド→30秒ショート自動生成
- upload.py: OAuth2 + フッター自動挿入
- TTS: `say -v Kyoko` → ffmpeg → wav

### Twitter (@Appmakeaa)
- フォロワー: 1人 / フォロー: 20人 / 投稿: 25件
- Free tier（POST/DELETEのみ、1日17ツイート上限）
- いいね/フォロー: ブラウザ経由（API制限）
- **方針転換(2/26): ジャンル不問でバズ狙い。AI特化やめ。トレンド乗り+3選型**
- スキル: `skills/twitter/`

### Instagram (@aiinsta26 / AI Traveler 🌍)
- 投稿: 14件 / フォロワー: 2人 / フォロー: 12人
- コンセプト: AI仮想旅行（透明性あり、#AI生成タグ必須）
- Leonardo AI API: トークン残3,178、Flux Devモデル
- 投稿フロー: ブラウザUI操作 + just_upload.py(Playwright CDP)
- 水中ホテル画像5枚生成済み（リール化未完）
- スキル: `skills/instagram/`

### TikTok (@newsai830 / AI NEWS)
- アカウント作成済み、動画ゼロ（初投稿待ち）
- ログイン: Googleアカウント経由

## コンテンツ戦略の学び
- **ビジュアル系 >>> 技術系**: AI画像スライドが一般層にリーチ
- **冒頭0.5秒のフックが命**: 視聴率4.9%の失敗から学んだ
- **「3選」フォーマットが有効**: 競合分析で3-5x効果確認
- **HBP構成**: Hook(0-2秒) → Build(中盤) → Payoff(最後)
- **コンセプト駆動 > 量産**: rune_visions 26投稿で21万フォロワー
- **競合から学ぶがパクらない**: パターン抽出→オリジナルに適用
- **クロスポストOK**: 自作コンテンツは全プラットフォームに展開
- **(2/26) ジャンル不問でバズ優先**: YouTube/Twitterはバズるものなら何でもOK。AI特化をやめる
- **Sora使える**: 無料プランでも動画生成可能。縦型9:16対応。クオリティ高い
- **Kling AI**: クレジット不足（16/50必要）、Soraの方が使いやすい

## 運用メモ
- **Sora**: 無料プランでも動画生成可能。縦型9:16対応。クオリティ高い
- **Instagram初リール投稿完了(2/26)**: Sora桜動画。Playwrightでアップ成功

## cron体制（7ジョブ）
- 朝リサーチ(7時) / モーニングブリーフ(9時) / Twitter(8,12,19時)
- YouTubeトレンド(20時) / デイリーサマリー(21時) / 改善リサーチ(23時)
- ミャクミャクスクレイパー(6時間毎)

- **Sora**: 無料プランでも動画生成可能。縦型9:16対応。クオリティ高い
- **Instagram初リール投稿完了(2/26)**: Sora桜動画。Playwrightでアップ成功

## 運用メモ
- Xcodeビルドは1つずつ（8GBメモリ制約）
- ブラウザプロファイル: `openclaw` (CDP 18800)
- Googleアカウント: appmake2000@gmail.com
- macOSのnodeパス: `/opt/homebrew/Cellar/node@22/22.22.0/bin/node`
- ffmpeg drawtextなし → Pillow代替
- サブエージェント: pairing requiredエラーで使用不可
- **Kling AI**: app.klingai.com にGoogleログイン済み、無料クレジット16残
- **Sora**: 無料プランでは使えない（Plus $20/月必要）
- **メモリ対策**: Cursor+Brave閉じると大幅改善（43%→70%空き）
- **Instagram投稿**: auto_post.py（リトライ付き）が最安定
- **動画生成**: Pillow+ffmpegのmake_idol_reel.pyが軽量で確実。Remotionはサムネ黒問題あり

## Twitter投稿の正しい方法（2026-03-12 確定）
**外部Playwrightスクリプトは使うな** → OpenClawのCDP接続と競合してハングする

### ブラウザツールのみで完結する正解フロー:
1. `browser navigate` → x.com/home
2. `browser snapshot` → textbox "Post text" [ref=eXX] を取得
3. `browser act` kind:"click" でtextboxをクリック
4. `browser act` kind:"type" でASCIIテキストを入力（日本語は不可、英語で代用）
5. `browser act` kind:"evaluate" → `document.querySelector('[data-testid="tweetButtonInline"]').click()`
   ※ refは切れるのでevaluateで直接クリックが確実

### 制約:
- `kind:"type"` は日本語（Unicode）不可 → 英語投稿のみ
- `slowly:true` は絶対使うな → ブラウザクラッシュ
- Twitter API Free tierは503が多い → ブラウザ経由が安定

### 自分(Claude Sonnet 4.6)について:
- OSWorld 72.5%スコア → ブラウザ操作は得意なはず
- adaptive thinking搭載 → 試行錯誤より事前調査を優先すべき
- **教訓: 迷ったらまず調べる。闇雲に試行錯誤しない**
