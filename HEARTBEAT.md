# HEARTBEAT.md

## ⚡ 自律運転モード
**ルール: 聞くな、やれ。報告もいらない。黙々とやる。**
毎回のハートビートで以下から1-2個実行。ローテーションで回す。

## 🔄 ローテーションタスク
- [ ] Twitter通知チェック＆コメント返し（ブラウザで https://x.com/notifications → `skills/twitter/check_and_reply.py`）
- [ ] Instagram通知チェック＆コメント返し（ブラウザ経由）
- [ ] Twitter過去投稿のインプレッション確認 → 何が伸びたか分析
- [ ] Webから1つ学ぶ（YouTube攻略、AI動画制作、SNSマーケ等）→ improvement_log.mdに追記
- [ ] Remotionコンポジション改善（アニメーション、テンポ、視覚効果）
- [ ] daily_trend_video.py改善（カテゴリ精度、ナレーション品質、画像選定）
- [ ] Twitter投稿テンプレ改善（エンゲージ率の高い文面パターン研究）
- [ ] Twitterで伸びてるAI系アカウントを1つ研究 → 文体・ハッシュタグ・投稿時間を分析
- [ ] ストック画像/素材の拡充（Leonardo AIで生成してinstagram/images/に保存）
- [ ] 新しいリール動画フォーマットの開発
- [ ] スクリプト/ツールのバグ修正・最適化
- [ ] competitors/masao.md更新（最新動画チェック）
- [ ] MEMORY.md整理（古い情報の整理、重要な学びの昇格）
- [ ] AIアイドル用の新画像を1枚生成（次回投稿用にストック）
- [ ] Instagram投稿のパフォーマンス確認（リーチ、いいね数）

## 🏗 毎日のサイト制作（最優先）
毎朝8時以降の最初のハートビートで実行：
1. web_searchで「web design trends 2026」をリサーチ（勉強）
2. /Users/hide/.openclaw/workspace/sites/ に day{N}-{ジャンル}/ を6本作成
   - Day番号: Day1=3/25, Day2=3/26, Day3=3/27, Day4=3/28...（日付から自動計算）
   - 既に当日分があればスキップ
3. 各サイトをスナップショットで自己レビュー → 改善 × 3周
4. sites/index.html にDayセクション追記
5. git add -A && git commit && git push origin main
6. scripts/self_check.md の完了欄に追記

## ルール
- 学んだことは必ずファイルに書く（improvement_log.md, competitors/, skills/）
- コード改善したらログを残す
- かんさんに報告不要（聞かれたら答える）。黙々とやる。
- 判断に迷ったら「やる」を選ぶ。聞かない。
- エラーが出たら自分で直す。直せなかったらログに残す。

## 週次PDCA（日曜夜に実行）
- YouTube Studio でアナリティクス確認
- Twitter プロフィール確認（フォロワー数）
- Instagram投稿パフォーマンス確認
- skills/twitter/pdca_log.md に新しいCycleを追記
- 改善点をcronジョブの指示に反映
