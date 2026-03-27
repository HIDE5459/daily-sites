# Twitter/X Skill

## 概要
Twitter/X API v2 を使った投稿・運用ツール。

## ファイル
- `twitter_api.py` — API操作（post/like/follow/search/user）
- `post.py` — シンプル投稿スクリプト
- `.env` — APIキー（秘密）

## 使い方
```bash
# 投稿
python3 twitter_api.py post "ツイート内容"

# 検索（Free tierは制限あり）
python3 twitter_api.py search "キーワード" 10
```

## 制限（Free tier）
- 投稿: 月1,500件
- 検索: 1リクエスト/15分
- いいね/フォロー/リプライ: **API不可**（ブラウザ経由で対応）
- 改行多めの長文は403エラーになることがある

## アカウント
- @Appmakeaa (AI Assistant)
- プロフィール: AIアシスタント自主運営アカウント

## 運用方針
- 反感を買わない、有益なコンテンツ
- トレンドに自然に乗る
- AI/開発/テック系の情報発信
- 1日2-3投稿ペース
