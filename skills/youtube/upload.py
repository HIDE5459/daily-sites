#!/usr/bin/env python3
"""Upload video to YouTube using OAuth2"""
import os, sys, json, pickle, http.server, threading, webbrowser
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET = os.path.join(SCRIPT_DIR, 'client_secret.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.pickle')
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']

def get_credentials(force_reauth=False):
    creds = None
    if not force_reauth and os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'rb') as f:
                creds = pickle.load(f)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                if creds.valid:
                    with open(TOKEN_FILE, 'wb') as f:
                        pickle.dump(creds, f)
                    return creds
        except Exception:
            pass
        creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
        creds = flow.run_local_server(port=8085, open_browser=False)
        print("\n>>> ブラウザで認証後、このウィンドウに戻ってください。\n")
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)
    return creds

def load_footer():
    footer_path = os.path.join(SCRIPT_DIR, 'description_footer.txt')
    if os.path.exists(footer_path):
        with open(footer_path) as f:
            return f.read()
    return ''

def upload_video(video_path, title, description='', tags=None, category='28', privacy='public', is_short=False):
    creds = get_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    if is_short:
        title = title if '#Shorts' in title else f'{title} #Shorts'
    
    # Append standard footer with links
    footer = load_footer()
    if footer and footer.strip() not in description:
        description = description.rstrip() + '\n' + footer
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': category,  # 28 = Science & Technology
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': False,
        }
    }
    
    media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f'Upload {int(status.progress() * 100)}%')
    
    video_id = response['id']
    print(f'\n✅ Upload complete!')
    print(f'Video ID: {video_id}')
    print(f'URL: https://youtube.com/watch?v={video_id}')
    return response

if __name__ == '__main__':
    if '--auth-only' in sys.argv or '-a' in sys.argv:
        print('YouTube OAuth トークンを再取得します。')
        print('ブラウザが開いたら Google アカウントでログインし、YouTube の利用を許可してください。\n')
        get_credentials(force_reauth=True)
        print('✅ トークンを保存しました。cron の YouTube アップロードはこれで動くはずです。')
        sys.exit(0)
    if len(sys.argv) < 3:
        print('Usage: upload.py <video_path> <title> [description] [tags_comma_separated]')
        print('       upload.py --auth-only   ... YouTube OAuth トークンのみ再取得（403 対策）')
        sys.exit(1)
    
    video_path = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else ''
    tags = sys.argv[4].split(',') if len(sys.argv) > 4 else []
    is_short = '--short' in sys.argv
    
    upload_video(video_path, title, description, tags, is_short=is_short)
