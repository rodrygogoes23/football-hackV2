import os
import threading
import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from flask import Flask
import random
import re

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Create Flask app for health check
web_app = Flask(__name__)

@web_app.route('/health')
def health_check():
    return "OK", 200

async def run_flask():
    """ Runs Flask server for health checks """
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:8000"]
    await serve(web_app, config)

# Ensure required environment variables exist
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Channel ID where player data is stored

assert API_ID is not None, "Missing API_ID in environment variables!"
assert API_HASH is not None, "Missing API_HASH in environment variables!"
assert SESSION_STRING is not None, "Missing SESSION in environment variables!"
assert CHANNEL_ID is not None, "Missing CHANNEL_ID in environment variables!"

# Initialize Pyrogram bot
bot = Client(
    "pro",
    api_id=int(API_ID),
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workers=10,
    max_concurrent_transmissions=5
)

# Define restricted group IDs
restricted_groups = [-1002436920609]  # Replace with actual group IDs
collect_running = False  # Control flag for the function
db = {}  # Dictionary to store player data

async def load_database():
    """Fetches player data from the Telegram channel and stores it in a dictionary."""
    global db
    db.clear()
    
    async with bot:
        async for message in bot.get_chat_history(CHANNEL_ID, limit=0):
            if message.text:
                match = re.match(r"(.+?) - (AgA[A-Za-z0-9_-]+)", message.text)
                if match:
                    player_name, file_id = match.groups()
                    db[file_id] = player_name

    logging.info(f"✅ Loaded {len(db)} players from the database!")

@bot.on_message(filters.command("startcollect") & filters.user([7508462500, 1710597756, 6895497681, 7435756663]))
async def start_collect(_, message: Message):
    global collect_running
    if not collect_running:
        collect_running = True
        await message.reply("✅ Collect function started!")
    else:
        await message.reply("⚠ Collect function is already running!")

@bot.on_message(filters.command("stopcollect") & filters.user([7508462500, 1710597756, 6895497681, 7435756663]))
async def stop_collect(_, message: Message):
    global collect_running
    collect_running = False
    await message.reply("🛑 Collect function stopped!")

@bot.on_message(filters.photo & filters.user([7522153272, 7946198415, 7742832624, 1710597756, 7828242164, 7957490622]))
async def handle_photo(c: Client, m: Message):
    """Checks if the received photo matches a known player and sends the collect command."""
    global collect_running
    if not collect_running:
        return

    try:
        if m.chat.id in restricted_groups:
            logging.info(f"Ignoring message from restricted group: {m.chat.id}")
            return

        await asyncio.sleep(random.uniform(0.3, 0.8))

        file_unique_id = m.photo.file_unique_id
        player_name = db.get(file_unique_id)

        if player_name:
            logging.info(f"Recognized player: {player_name}")
            await bot.send_message(m.chat.id, f"/collect {player_name}")
        else:
            logging.warning(f"Unknown player (file ID: {file_unique_id})")

    except FloodWait as e:
        logging.warning(f"Rate limit hit! Waiting for {e.value} seconds...")
        await asyncio.sleep(e.value)
    except Exception as e:
        logging.error(f"Error processing message: {e}")

@bot.on_message(filters.command("fileid") & filters.reply & filters.user([7508462500, 1710597756, 6895497681, 7435756663]))
async def extract_file_id(_, message: Message):
    """Extracts and sends the unique file ID of a replied photo."""
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("⚠ Please reply to a photo to extract the file ID.")
        return
    
    file_unique_id = message.reply_to_message.photo.file_unique_id
    await message.reply(f"📂 **File Unique ID:** `{file_unique_id}`")

async def main():
    """Runs Pyrogram bot and Flask server concurrently"""
    await bot.start()
    logging.info("Bot started successfully!")

    # Load database from the channel
    await load_database()

    await asyncio.gather(run_flask(), idle())
    await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
