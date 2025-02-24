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
db = storage.database("cric")

# Create Flask app for health check
web_app = Flask(__name__)

@web_app.route('/health')
def health_check():
    return "OK", 200

async def run_flask():
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:8000"]
    await serve(web_app, config)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION")

assert API_ID, "Missing API_ID!"
assert API_HASH, "Missing API_HASH!"
assert SESSION_STRING, "Missing SESSION!"

bot = Client(
    "pro",
    api_id=int(API_ID),
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workers=10,
    max_concurrent_transmissions=5
)

restricted_groups = [-1002173442670]
collect_running = False

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

@bot.on_message(filters.photo & filters.user([7522153272, 7946198415, 7742832624, 1710597756]))
async def handle_photos(c: Client, m: Message):
    global collect_running
    if not collect_running:
        return

    try:
        if m.chat.id in restricted_groups:
            logging.info(f"Ignoring message from restricted group: {m.chat.id}")
            return

        await asyncio.sleep(random.uniform(0.7, 1.0))

        caption = m.caption or ""
        file_data = db.get(m.photo.file_unique_id)

        if "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴘʟᴀʏᴇʀ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ" in caption:
            command = "/collect"
        elif "🔮 ᴅᴏᴄᴛᴏʀ ꜱᴛʀᴀɴɢᴇ ꜱᴀᴡ 𝟣𝟦 ᴍɪʟʟɪᴏɴ ᴏᴜᴛᴄᴏᴍᴇꜱ… ɪɴ ᴏɴʟʏ ᴏɴᴇ, ʏᴏᴜ ᴄʟᴀɪᴍ ᴛʜɪꜱ ꜱᴜᴘᴇʀꜱᴛᴀʀ!" in caption:
            command = "/hunt"
        else:
            return

        if file_data:
            logging.info(f"Image ID {m.photo.file_unique_id} found: {file_data['name']}")
            collect_message = await m.reply(f"{command} {file_data['name']}")
            await asyncio.sleep(1)
            await collect_message.delete()
        else:
            logging.warning(f"Image ID {m.photo.file_unique_id} not found!")

    except FloodWait as e:
        logging.warning(f"Rate limit hit! Waiting {e.value} sec...")
        await asyncio.sleep(e.value)
    except Exception as e:
        logging.error(f"Error processing message: {e}")

async def main():
    await bot.start()
    logging.info("Bot started successfully!")
    await asyncio.gather(run_flask(), idle())
    await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
