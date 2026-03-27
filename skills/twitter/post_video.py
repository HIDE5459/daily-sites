#!/usr/bin/env python3
"""Post a tweet with video to Twitter/X using chunked media upload"""
import os, sys, json, time, hashlib, hmac, base64, urllib.parse, secrets
import urllib.request, math

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k] = v

API_KEY = os.environ['TWITTER_API_KEY']
API_SECRET = os.environ['TWITTER_API_SECRET']
ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']

def percent_encode(s):
    return urllib.parse.quote(str(s), safe='')

def oauth_sig(method, url, params):
    sp = '&'.join(f'{percent_encode(k)}={percent_encode(v)}' for k, v in sorted(params.items()))
    bs = f'{method}&{percent_encode(url)}&{percent_encode(sp)}'
    sk = f'{percent_encode(API_SECRET)}&{percent_encode(ACCESS_SECRET)}'
    return base64.b64encode(hmac.new(sk.encode(), bs.encode(), hashlib.sha1).digest()).decode()

def oauth_header(method, url, extra=None):
    p = {
        'oauth_consumer_key': API_KEY,
        'oauth_nonce': secrets.token_hex(16),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': ACCESS_TOKEN,
        'oauth_version': '1.0',
    }
    if extra: p.update(extra)
    p['oauth_signature'] = oauth_sig(method, url, p)
    return 'OAuth ' + ', '.join(f'{percent_encode(k)}="{percent_encode(v)}"' for k, v in sorted(p.items()))

UPLOAD_URL = 'https://upload.twitter.com/1.1/media/upload.json'
TWEET_URL = 'https://api.x.com/2/tweets'

def upload_video(video_path):
    file_size = os.path.getsize(video_path)
    print(f'Uploading {video_path} ({file_size} bytes)...')
    
    # INIT
    params = {'command': 'INIT', 'total_bytes': str(file_size), 'media_type': 'video/mp4', 'media_category': 'tweet_video'}
    auth = oauth_header('POST', UPLOAD_URL, params)
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(UPLOAD_URL, data=data, method='POST')
    req.add_header('Authorization', auth)
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    media_id = result['media_id_string']
    print(f'INIT ok, media_id={media_id}')
    
    # APPEND (chunked)
    CHUNK_SIZE = 4 * 1024 * 1024  # 4MB
    with open(video_path, 'rb') as f:
        segment = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            boundary = f'----WebKitFormBoundary{secrets.token_hex(8)}'
            body = b''
            for name, value in [('command', 'APPEND'), ('media_id', media_id), ('segment_index', str(segment))]:
                body += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
            body += f'--{boundary}\r\nContent-Disposition: form-data; name="media_data"\r\n\r\n'.encode()
            body += base64.b64encode(chunk) + f'\r\n--{boundary}--\r\n'.encode()
            
            auth = oauth_header('POST', UPLOAD_URL)
            req = urllib.request.Request(UPLOAD_URL, data=body, method='POST')
            req.add_header('Authorization', auth)
            req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
            urllib.request.urlopen(req)
            print(f'APPEND segment {segment} ok')
            segment += 1
    
    # FINALIZE
    params = {'command': 'FINALIZE', 'media_id': media_id}
    auth = oauth_header('POST', UPLOAD_URL, params)
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(UPLOAD_URL, data=data, method='POST')
    req.add_header('Authorization', auth)
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    print(f'FINALIZE ok')
    
    # Check processing status
    if 'processing_info' in result:
        state = result['processing_info']['state']
        while state in ('pending', 'in_progress'):
            wait = result['processing_info'].get('check_after_secs', 5)
            print(f'Processing... waiting {wait}s')
            time.sleep(wait)
            params = {'command': 'STATUS', 'media_id': media_id}
            auth = oauth_header('GET', UPLOAD_URL, params)
            url = UPLOAD_URL + '?' + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, method='GET')
            req.add_header('Authorization', auth)
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            state = result.get('processing_info', {}).get('state', 'succeeded')
        if state == 'failed':
            print(f'Processing FAILED: {result}')
            return None
    
    print(f'Video ready! media_id={media_id}')
    return media_id

def post_tweet_with_video(text, media_id):
    auth = oauth_header('POST', TWEET_URL)
    data = json.dumps({'text': text, 'media': {'media_ids': [media_id]}}).encode()
    req = urllib.request.Request(TWEET_URL, data=data, method='POST')
    req.add_header('Authorization', auth)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f'Tweet posted! id={result["data"]["id"]}')
            return result
    except urllib.error.HTTPError as e:
        print(f'Error {e.code}: {e.read().decode()}')
        return None

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: post_video.py <video_path> "tweet text"')
        sys.exit(1)
    video_path = sys.argv[1]
    text = sys.argv[2]
    media_id = upload_video(video_path)
    if media_id:
        post_tweet_with_video(text, media_id)
