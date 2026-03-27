#!/usr/bin/env python3
"""Post a tweet using Twitter API v2 with OAuth 1.0a"""
import sys, os, json, time, hashlib, hmac, base64, urllib.parse, uuid, secrets
import urllib.request

# Load env
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

def create_oauth_signature(method, url, params, consumer_secret, token_secret):
    sorted_params = '&'.join(f'{percent_encode(k)}={percent_encode(v)}' for k, v in sorted(params.items()))
    base_string = f'{method}&{percent_encode(url)}&{percent_encode(sorted_params)}'
    signing_key = f'{percent_encode(consumer_secret)}&{percent_encode(token_secret)}'
    signature = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
    return base64.b64encode(signature.digest()).decode()

def post_tweet(text):
    url = 'https://api.x.com/2/tweets'
    oauth_params = {
        'oauth_consumer_key': API_KEY,
        'oauth_nonce': secrets.token_hex(16),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': ACCESS_TOKEN,
        'oauth_version': '1.0',
    }
    
    signature = create_oauth_signature('POST', url, oauth_params, API_SECRET, ACCESS_SECRET)
    oauth_params['oauth_signature'] = signature
    
    auth_header = 'OAuth ' + ', '.join(
        f'{percent_encode(k)}="{percent_encode(v)}"' 
        for k, v in sorted(oauth_params.items())
    )
    
    data = json.dumps({'text': text}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', auth_header)
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f'Error {e.code}: {error_body}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: post.py "tweet text"', file=sys.stderr)
        sys.exit(1)
    post_tweet(sys.argv[1])
