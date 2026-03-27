# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

### Browser

- Profile: `openclaw` (自動起動、Chrome拡張不要)
- CDP Port: 18800
- Googleアカウント: appmake2000@gmail.com でログイン済み
- Gmail, Google Calendar, その他Googleサービスにアクセス可能
- `openclaw browser --browser-profile openclaw start` で手動起動も可

### Twitter/X
- アカウント: @Appmakeaa (AI Assistant)
- API: Free tier（投稿のみ、月1,500件）
- スキル: `skills/twitter/twitter_api.py`
- キー: `skills/twitter/.env`
- いいね/フォロー: ブラウザ経由（APIはBasic $200/月が必要）
- 改行多い長文は403 → 改行少なめに

### YouTube
- チャンネル: KAN HIDE (appmake2000@gmail.com)
- OAuth2: `skills/youtube/token.pickle` / `client_secret.json`
- アップロード: `skills/youtube/upload.py <video> <title> [desc] [tags] [--short]`
- 動画制作: Pillow(フレーム) + ffmpeg(合成) + TTS(音声)
- drawtextは使えない（libfreetype無し）→ Pillowで代替

### TikTok
- アカウント: @newsai830 (AI NEWS)
- ログイン: Googleアカウント（appmake2000@gmail.com）
- アップロード: TikTok Studio（ブラウザ経由）
- スキル: `skills/tiktok/SKILL.md`

### Agent Stability / Troubleshooting

**既知の問題と対策:**
- タスク途中で無言停止 → サブエージェントに分割して依頼。1つの指示で複数ステップを詰め込まない
- 長い会話でコンテキスト溢れ → `/compact` でコンテキスト圧縮、`/new` で新セッション
- ツール呼び出しでハング → `timeoutSeconds: 120` を設定済み（デフォルト600秒から短縮）
- 権限エラーで動かなくなった → `openclaw doctor --fix` を実行

**設定（2026-03-25適用済み）:**
- `contextPruning.mode: "cache-ttl"` / `ttl: "1h"` / `keepLastAssistants: 5`
- `timeoutSeconds: 120`
- `compaction.mode: "safeguard"`

**復旧手順（困ったらこの順で）:**
1. `openclaw doctor --fix`
2. `openclaw gateway restart`
3. Telegramで `/new` を送って新セッション開始
4. それでもダメなら `openclaw logs --follow` でエラーを確認

**長いタスクのベストプラクティス:**
- 指示は1ステップずつ分割する（「まず○○して」→完了後→「次に△△して」）
- 結果をファイルに書き出させる（コンテキスト節約）
- 複雑なタスクはサブエージェント活用

### Auth / Claude MAX

- 認証方式: Claude MAX OAuthトークン (`sk-ant-oat01-...`)
- トークン有効期限: 1年間（2027年3月頃更新必要）
- 更新方法: ターミナルで `claude setup-token` → `openclaw models auth paste-token --provider anthropic`
- 注意: MAXサブスクリプションのOAuth使用はグレーゾーン。規約変更リスクあり

---

Add whatever helps you do your job. This is your cheat sheet.
