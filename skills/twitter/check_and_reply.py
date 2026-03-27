#!/usr/bin/env python3
"""
Twitter通知チェック＆自動リプライ
- ブラウザで通知ページをスクレイピング（OpenClaw browser tool経由で呼ぶ）
- このスクリプトはリプライ投稿部分のみ担当
- 通知チェックはブラウザ操作で行い、結果をこのスクリプトに渡す
"""
import tweepy
import json
import os
import sys
from datetime import datetime

# Twitter API credentials
API_KEY = 'x0gS7BZ05n5mTsTuTTpeObJTg'
API_SECRET = 'EYGmIQwR5KYCtrKA6YOkP1OGWqfa0EQPS6Qkvjk7iqvZ0o6ZqR'
ACCESS_TOKEN = '1726057299184406528-Q7ILg2STmEfveAh5h85LQ37I7Qdj80'
ACCESS_SECRET = '9Ue5l7yvfs8wQNMqZdSz1JQyIRVwstGbixgsFy1VbLlKj'

REPLIED_FILE = os.path.join(os.path.dirname(__file__), 'replied_tweets.json')

def load_replied():
    if os.path.exists(REPLIED_FILE):
        with open(REPLIED_FILE) as f:
            return json.load(f)
    return []

def save_replied(replied):
    with open(REPLIED_FILE, 'w') as f:
        json.dump(replied[-100:], f)  # Keep last 100

def reply_to_tweet(tweet_id, reply_text):
    """Reply to a specific tweet by ID."""
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
    
    replied = load_replied()
    if tweet_id in replied:
        print(f'Already replied to {tweet_id}, skipping')
        return None
    
    try:
        r = client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
        replied.append(tweet_id)
        save_replied(replied)
        print(f'Replied to {tweet_id}: {reply_text[:50]}...')
        return r.data['id']
    except Exception as e:
        print(f'Error replying to {tweet_id}: {e}')
        return None

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python check_and_reply.py <tweet_id> <reply_text>')
        sys.exit(1)
    
    tweet_id = sys.argv[1]
    reply_text = sys.argv[2]
    reply_to_tweet(tweet_id, reply_text)
