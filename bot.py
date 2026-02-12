# bot.py - Trenches rug alert bot (low-resource for Railway free/trial)

import os
import time
import sys
import requests
from anthropic import Anthropic
import tweepy
from datetime import datetime

print("=== BOT STARTUP DEBUG ===")
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("First 15 environment variables:", list(os.environ.keys())[:15])

# Give Railway a few seconds to fully inject environment variables
print("Waiting 5 seconds for env vars to be available...")
time.sleep(5)

# Load secrets from env vars (set in Railway)
HELIUS_KEY = os.getenv("HELIUS_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# Debug: show what we actually got
print("\n=== DEBUG - ENVIRONMENT VARIABLES CHECK ===")
print(f"HELIUS_KEY:      {'YES' if HELIUS_KEY else 'MISSING / EMPTY'}")
print(f"ANTHROPIC_KEY:   {'YES' if ANTHROPIC_KEY else 'MISSING / EMPTY'}")
print(f"X_API_KEY:       {'YES' if X_API_KEY else 'MISSING / EMPTY'}")
print(f"X_API_SECRET:    {'YES' if X_API_SECRET else 'MISSING / EMPTY'}")
print(f"X_ACCESS_TOKEN:  {'YES' if X_ACCESS_TOKEN else 'MISSING / EMPTY'}")
print(f"X_ACCESS_SECRET: {'YES' if X_ACCESS_SECRET else 'MISSING / EMPTY'}")

# Only warn instead of crashing - so we can see what happens next
missing = []
if not HELIUS_KEY: missing.append("HELIUS_KEY")
if not ANTHROPIC_KEY: missing.append("ANTHROPIC_KEY")
if not X_API_KEY: missing.append("X_API_KEY")
if not X_API_SECRET: missing.append("X_API_SECRET")
if not X_ACCESS_TOKEN: missing.append("X_ACCESS_TOKEN")
if not X_ACCESS_SECRET: missing.append("X_ACCESS_SECRET")

if missing:
    print(f"WARNING: The following variables are missing: {', '.join(missing)}")
    print("Bot will continue running, but API calls will fail until fixed.")
else:
    print("All required environment variables are present - good to go!")

# Proceed with client initialization
try:
    ai_client = Anthropic(api_key=ANTHROPIC_KEY)
    print("Anthropic client initialized successfully")
except Exception as e:
    print(f"Failed to initialize Anthropic client: {e}")

try:
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_SECRET
    )
    print("Tweepy client initialized successfully")
except Exception as e:
    print(f"Failed to initialize Tweepy client: {e}")

print("=== Bot initialized - starting polling loop ===")

# ----------------------------------------------------------------------
# Your original polling logic goes here (the rest of the code)
# ----------------------------------------------------------------------

def get_new_pairs_stub():
    return [
        {"address": "So11111111111111111111111111111111111111112", "symbol": "SOL-TEST"},
    ]

def get_deployer_stub(token_addr):
    return "9gP2kCy3wA1ctvYWQk75guqS5f1cW2U5zJ2k3L4m5n6p"

def get_funded_by(address):
    if not HELIUS_KEY:
        print("HELIUS_KEY missing - cannot call API")
        return {"error": "HELIUS_KEY missing"}
    url = f"https://api.helius.xyz/v1/wallet/{address}/funded-by?api-key={HELIUS_KEY}"
    try:
        resp = requests.get(url, timeout=12).json()
        return resp
    except Exception as e:
        print(f"Helius error: {e}")
        return {"error": str(e)}

def generate_tweet(funded_data, symbol, addr):
    if not ANTHROPIC_KEY:
        print("ANTHROPIC_KEY missing - cannot generate tweet")
        return None
    if "error" in funded_data:
        return None

    prompt = f"""Short X tweet for Solana trenches rug alert.
Token: {symbol} ({addr[:6]}...)
Deployer funded-by: {funded_data}

Blunt style, emojis, quick rug risk take.
End exactly with: NFA - save the trenches! #Solana Powered by @heliuslabs"""

    try:
        msg = ai_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=120,
            messages=[{"role": "user", "content": prompt}]
        )
        tweet_text = msg.content[0].text.strip()
        return tweet_text[:280]
    except Exception as e:
        print(f"Claude AI error: {e}")
        return None

daily_posts = 0
MAX_DAILY_POSTS = 3

while True:
    now = datetime.now()
    if now.hour == 0:
        daily_posts = 0

    if daily_posts >= MAX_DAILY_POSTS:
        print("Daily post limit reached - sleeping 1 hour")
        time.sleep(3600)
        continue

    pairs = get_new_pairs_stub()[:2]
    for pair in pairs:
        deployer = get_deployer_stub(pair["address"])
        if not deployer:
            continue

        funded = get_funded_by(deployer)
        tweet = generate_tweet(funded, pair["symbol"], pair["address"])

        if tweet:
            try:
                response = client.create_tweet(text=tweet)
                print(f"Posted tweet! ID: {response.data['id']}")
                print(f"Tweet text: {tweet}")
                daily_posts += 1
            except Exception as e:
                print(f"X posting failed: {e}")

    print("Poll finished - sleeping 30 minutes")
    time.sleep(1800)
