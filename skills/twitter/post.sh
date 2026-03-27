#!/bin/bash
# Twitter/X post script using OAuth 1.0a
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.env"

TEXT="$1"

# Generate OAuth 1.0a signature and post using curl
NONCE=$(openssl rand -hex 16)
TIMESTAMP=$(date +%s)

# URL encode function
urlencode() {
  python3 -c "import urllib.parse; print(urllib.parse.quote('$1', safe=''))"
}

ENCODED_TEXT=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$TEXT")

# OAuth parameters
OAUTH_PARAMS="oauth_consumer_key=$TWITTER_API_KEY&oauth_nonce=$NONCE&oauth_signature_method=HMAC-SHA256&oauth_timestamp=$TIMESTAMP&oauth_token=$TWITTER_ACCESS_TOKEN&oauth_version=1.0"

# Create signature base string
SIG_BASE="POST&$(python3 -c "import urllib.parse; print(urllib.parse.quote('https://api.x.com/2/tweets', safe=''))")&$(python3 -c "import urllib.parse; print(urllib.parse.quote('$OAUTH_PARAMS', safe=''))")"

# Create signing key
SIGNING_KEY="$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TWITTER_API_SECRET', safe=''))")&$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TWITTER_ACCESS_SECRET', safe=''))")"

# Generate signature
SIGNATURE=$(echo -n "$SIG_BASE" | openssl dgst -sha256 -hmac "$SIGNING_KEY" -binary | base64)
ENCODED_SIG=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SIGNATURE', safe=''))")

# Build Authorization header
AUTH_HEADER="OAuth oauth_consumer_key=\"$TWITTER_API_KEY\", oauth_nonce=\"$NONCE\", oauth_signature=\"$ENCODED_SIG\", oauth_signature_method=\"HMAC-SHA256\", oauth_timestamp=\"$TIMESTAMP\", oauth_token=\"$TWITTER_ACCESS_TOKEN\", oauth_version=\"1.0\""

curl -s -X POST "https://api.x.com/2/tweets" \
  -H "Authorization: $AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{\"text\": $(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$TEXT")}"
