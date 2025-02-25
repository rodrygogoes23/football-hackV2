import os
import threading
import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from Mukund import Mukund
from flask import Flask
import random

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

storage = Mukund("Vegeta")
db = storage.database("merged")

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

assert API_ID is not None, "Missing API_ID in environment variables!"
assert API_HASH is not None, "Missing API_HASH in environment variables!"
assert SESSION_STRING is not None, "Missing SESSION in environment variables!"

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
restricted_groups = [-1002173442670]  # Replace with actual group IDs
collect_running = False  # Control flag for the function

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

@bot.on_message(filters.photo & filters.user([7522153272, 7946198415, 7742832624, 1710597756, 7828242164]))
async def hacke(c: Client, m: Message):
    global collect_running
    if not collect_running:
        return

    try:
        if m.chat.id in restricted_groups:
            logging.info(f"Ignoring message from restricted group: {m.chat.id}")
            return

        await asyncio.sleep(random.uniform(0.3, 0.8))

        if m.caption:
            logging.debug(f"Received caption: {m.caption}")

            if "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴘʟᴀʏᴇʀ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ" in m.caption:
                command = "/collect"
            elif "❄️ ʟᴏᴏᴋ ᴀɴ ᴀᴡsᴏᴍᴇ ᴄᴇʟᴇʙʀɪᴛʏ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜᴇʀ/ʜɪᴍ ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ" in m.caption:
                logging.info(f"Detected celebrity message: {m.caption}")
                command = "/collect"
            elif "🔮 ᴅᴏᴄᴛᴏʀ ꜱᴛʀᴀɴɢᴇ ꜱᴀᴡ 𝟣𝟦 ᴍɪʟʟɪᴏɴ ᴏᴜᴛᴄᴏᴍᴇꜱ… ɪɴ ᴏɴʟʏ ᴏɴᴇ, ʏᴏᴜ ᴄʟᴀɪᴍ ᴛʜɪꜱ ꜱᴜᴘᴇʀꜱᴛᴀʀ!" in m.caption:
                logging.info(f"Detected Doctor Strange message: {m.caption}")
                command = "/hunt"
            else:
                return  # Ignore if no matching caption

            file_data = db.get(m.photo.file_unique_id)

            if file_data:
                logging.info(f"Image ID {m.photo.file_unique_id} found in DB: {file_data['name']}")
                collect_message = await m.reply(f"{command} {file_data['name']}")
                await asyncio.sleep(1)
                await collect_message.delete()
            else:
                logging.warning(f"Image ID {m.photo.file_unique_id} not found in DB!")

    except FloodWait as e:
        logging.warning(f"Rate limit hit! Waiting for {e.value} seconds...")
        await asyncio.sleep(e.value)
    except Exception as e:
        logging.error(f"Error processing message: {e}")

@bot.on_message(filters.command("fileid") & filters.reply)
async def extract_file_id(_, message: Message):
    """ Extracts and sends the unique file ID of a replied photo """
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("⚠ Please reply to a photo to extract the file ID.")
        return
    
    file_unique_id = message.reply_to_message.photo.file_unique_id
    await message.reply(f"📂 **File Unique ID:** `{file_unique_id}`")

async def main():
    """ Runs Pyrogram bot and Flask server concurrently """
    await bot.start()
    logging.info("Bot started successfully!")
    await asyncio.gather(run_flask(), idle())
    await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
