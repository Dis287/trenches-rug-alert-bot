# bot.py - Trenches rug alert bot (low-resource for Railway free/trial)
import os
import time
import requests
from anthropic import Anthropic
import tweepy
from datetime import datetime

# Load secrets from env vars (set in Railway)
HELIUS_KEY = os.getenv("HELIUS_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

if not all([HELIUS_KEY, ANTHROPIC_KEY, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
    print("ERROR: Missing one or more environment variables. Add them in Railway Variables.")
    exit(1)

ai_client = Anthropic(api_key=ANTHROPIC_KEY)

client = tweepy.Client(
    consumer_key=X_API_KEY,
    consumer_secret=X_API_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_SECRET
)

def get_new_pairs_stub():
    # Later: replace with real DexScreener/Birdeye fetch
    # For now: simulate one test item
    return [
        {"address": "So11111111111111111111111111111111111111112", "symbol": "SOL-TEST"},
    ]

def get_deployer_stub(token_addr):
    # Later: real fetch from Birdeye or tx history
    return "9gP2kCy3wA1ctvYWQk75guqS5f1cW2U5zJ2k3L4m5n6p"  # fake example deployer

def get_funded_by(address):
    url = f"https://api.helius.xyz/v1/wallet/{address}/funded-by?api-key={HELIUS_KEY}"
    try:
        resp = requests.get(url, timeout=12).json()
        return resp
    except Exception as e:
        print(f"Helius error: {e}")
        return {"error": str(e)}

def generate_tweet(funded_data, symbol, addr):
    if "error" in funded_data:
        print("No funded data - skipping tweet")
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

print("Starting trenches rug alert bot - polling every 30 min...")
daily_posts = 0
MAX_DAILY_POSTS = 3  # Conservative for trial credits

while True:
    now = datetime.now()
    if now.hour == 0:
        daily_posts = 0

    if daily_posts >= MAX_DAILY_POSTS:
        print("Daily post limit reached - sleeping 1 hour")
        time.sleep(3600)
        continue

    pairs = get_new_pairs_stub()[:2]  # limit to save credits
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
