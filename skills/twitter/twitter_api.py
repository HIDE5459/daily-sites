#!/usr/bin/env python3
"""Twitter/X API v2 utilities - follow, like, search, reply"""
import sys, os, json, time, hashlib, hmac, base64, urllib.parse, secrets
import urllib.request

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
USER_ID = ACCESS_TOKEN.split('-')[0]

def percent_encode(s):
    return urllib.parse.quote(str(s), safe='')

def oauth_signature(method, url, params):
    sorted_params = '&'.join(f'{percent_encode(k)}={percent_encode(v)}' for k, v in sorted(params.items()))
    base_string = f'{method}&{percent_encode(url)}&{percent_encode(sorted_params)}'
    signing_key = f'{percent_encode(API_SECRET)}&{percent_encode(ACCESS_SECRET)}'
    sig = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
    return base64.b64encode(sig.digest()).decode()

def oauth_header(method, url, extra_params=None):
    params = {
        'oauth_consumer_key': API_KEY,
        'oauth_nonce': secrets.token_hex(16),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': ACCESS_TOKEN,
        'oauth_version': '1.0',
    }
    if extra_params:
        params.update(extra_params)
    params['oauth_signature'] = oauth_signature(method, url, params)
    return 'OAuth ' + ', '.join(f'{percent_encode(k)}="{percent_encode(v)}"' for k, v in sorted(params.items()))

def api_request(method, url, data=None, query_params=None):
    if query_params:
        url_with_params = url + '?' + urllib.parse.urlencode(query_params)
    else:
        url_with_params = url
    
    auth = oauth_header(method, url, extra_params=query_params if method == 'GET' else None)
    
    if data:
        body = json.dumps(data).encode()
    else:
        body = None
    
    req = urllib.request.Request(url_with_params, data=body, method=method)
    req.add_header('Authorization', auth)
    if body:
        req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return {'error': e.code, 'detail': error_body}

def post_tweet(text, reply_to=None):
    data = {'text': text}
    if reply_to:
        data['reply'] = {'in_reply_to_tweet_id': reply_to}
    return api_request('POST', 'https://api.x.com/2/tweets', data)

def like_tweet(tweet_id):
    return api_request('POST', f'https://api.x.com/2/users/{USER_ID}/likes', {'tweet_id': tweet_id})

def follow_user(target_user_id):
    return api_request('POST', f'https://api.x.com/2/users/{USER_ID}/following', {'target_user_id': target_user_id})

def search_tweets(query, max_results=10):
    return api_request('GET', 'https://api.x.com/2/tweets/search/recent', 
                       query_params={'query': query, 'max_results': str(max_results),
                                    'tweet.fields': 'author_id,public_metrics,created_at',
                                    'expansions': 'author_id'})

def get_user_by_username(username):
    return api_request('GET', f'https://api.x.com/2/users/by/username/{username}',
                       query_params={'user.fields': 'public_metrics,description'})

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if cmd == 'post':
        print(json.dumps(post_tweet(sys.argv[2]), indent=2, ensure_ascii=False))
    elif cmd == 'like':
        print(json.dumps(like_tweet(sys.argv[2]), indent=2))
    elif cmd == 'follow':
        print(json.dumps(follow_user(sys.argv[2]), indent=2))
    elif cmd == 'search':
        print(json.dumps(search_tweets(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10), indent=2, ensure_ascii=False))
    elif cmd == 'user':
        print(json.dumps(get_user_by_username(sys.argv[2]), indent=2, ensure_ascii=False))
    else:
        print('Usage: twitter_api.py [post|like|follow|search|user] [args...]')
