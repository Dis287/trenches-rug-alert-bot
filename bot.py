# bot.py - Trenches rug alert bot (low-resource for Railway free/trial)

import os
import time
import requests
from anthropic import Anthropic
import tweepy
from datetime import datetime

print("=== BOT STARTUP DEBUG ===")
print("Python version:", sys.version)
print("Current working dir:", os.getcwd())
print("os.environ keys:", list(os.environ.keys())[:10])  # first 10 to see if anything is there

# Give Railway a moment to inject env vars (sometimes delayed)
time.sleep(5)

# Load secrets
HELIUS_KEY = os.getenv("HELIUS_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

print("\n=== DEBUG - ENV VARS LOADED? ===")
print("HELIUS_KEY:", "YES" if HELIUS_KEY else "NO / EMPTY")
print("ANTHROPIC_KEY:", "YES" if ANTHROPIC_KEY else "NO / EMPTY")
print("X_API_KEY:", "YES" if X_API_KEY else "NO / EMPTY")
print("X_API_SECRET:", "YES" if X_API_SECRET else "NO / EMPTY")
print("X_ACCESS_TOKEN:", "YES" if X_ACCESS_TOKEN else "NO / EMPTY")
print("X_ACCESS_SECRET:", "YES" if X_ACCESS_SECRET else "NO / EMPTY")

# Only exit if ALL are missing (more forgiving)
missing = [k for k, v in {
    "HELIUS_KEY": HELIUS_KEY,
    "ANTHROPIC_KEY": ANTHROPIC_KEY,
    "X_API_KEY": X_API_KEY,
    "X_API_SECRET": X_API_SECRET,
    "X_ACCESS_TOKEN": X_ACCESS_TOKEN,
    "X_ACCESS_SECRET": X_ACCESS_SECRET
}.items() if not v]

if missing:
    print(f"WARNING: Missing variables: {', '.join(missing)}")
    print("Bot will continue but API calls will fail until fixed.")
    # Do NOT exit(1) anymore - let it run for debugging
else:
    print("All required env vars present - good to go!")

# Proceed with clients
ai_client = Anthropic(api_key=ANTHROPIC_KEY)

client = tweepy.Client(
    consumer_key=X_API_KEY,
    consumer_secret=X_API_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_SECRET
)

print("=== Bot initialized - starting polling loop ===")

# ... the rest of your code remains the same ...
