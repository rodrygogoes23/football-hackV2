import os
import json
import re
import asyncio
from flask import Flask
from pyrogram import Client

# Environment Variables (Make sure these are set in Koyeb)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Your channel ID

assert API_ID and API_HASH and SESSION_STRING and CHANNEL_ID, "Missing required environment variables!"

# Initialize Pyrogram client
bot = Client(
    "extractor",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Flask app for health check
web_app = Flask(__name__)

@web_app.route('/health')
def health_check():
    return "OK", 200

async def run_flask():
    """Run Flask server for health checks (port 8000)"""
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:8000"]
    await serve(web_app, config)

async def extract_players():
    """Fetch player data from the channel and save it to a JSON file."""
    players = {}

    async with bot:
        async for message in bot.get_chat_history(CHANNEL_ID, limit=0):
            if message.text:
                match = re.match(r"(.+?) - (AgA[A-Za-z0-9_-]+)", message.text)
                if match:
                    player_name, file_id = match.groups()
                    players[file_id] = player_name  # Store file_id as key

    # Save to JSON file
    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, indent=4, ensure_ascii=False)

    print(f"✅ Extracted {len(players)} players and saved to players.json!")

async def main():
    """Run the player extraction and Flask health check concurrently"""
    await bot.start()
    await extract_players()
    await asyncio.gather(run_flask())

if __name__ == "__main__":
    asyncio.run(main())
