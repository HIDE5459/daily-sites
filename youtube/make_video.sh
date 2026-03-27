#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

DURATION=$(ffprobe -show_entries format=duration -v quiet -of csv=p=0 full_audio.mp3 | cut -d. -f1)
DURATION=$((DURATION + 2))

# Create YouTube Shorts vertical video (1080x1920) with animated text
ffmpeg -y \
  -f lavfi -i "color=c=0x1a1a2e:s=1080x1920:d=${DURATION}" \
  -i full_audio.mp3 \
  -filter_complex "
    [0:v]
    drawtext=text='🤖 AI Assistant':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=300:enable='gte(t,0)',
    drawtext=text='完全AI運営チャンネル':fontsize=52:fontcolor=0x00d4ff:x=(w-text_w)/2:y=420:enable='gte(t,0.5)',
    drawtext=text='企画 → AI':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=620:enable='gte(t,1)',
    drawtext=text='台本 → AI':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=700:enable='gte(t,1.5)',
    drawtext=text='編集 → AI':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=780:enable='gte(t,2)',
    drawtext=text='投稿 → AI':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=860:enable='gte(t,2.5)',
    drawtext=text='すべてAIがやります':fontsize=48:fontcolor=0x00ff88:x=(w-text_w)/2:y=1020:enable='gte(t,3.5)',
    drawtext=text='AI開発の裏側':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=1200:enable='gte(t,5)',
    drawtext=text='使えるテクニック':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=1280:enable='gte(t,5.5)',
    drawtext=text='最新AIニュース':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=1360:enable='gte(t,6)',
    drawtext=text='チャンネル登録':fontsize=56:fontcolor=red:x=(w-text_w)/2:y=1560:enable='gte(t,7)',
    drawtext=text='よろしくお願いします！':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=1650:enable='gte(t,7.5)'
    [v]" \
  -map "[v]" -map 1:a \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  -shortest \
  -movflags +faststart \
  video.mp4

echo "Done: video.mp4"
ls -lh video.mp4
