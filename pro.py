import os
import logging
import asyncio
import random
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from Mukund import Mukund
from flask import Flask
from collections import defaultdict

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Initialize Database
storage = Mukund("Vegeta")
db = storage.database("football")

# In-memory cache for quick lookups (to handle 1,200 players efficiently)
player_cache = {}

# Preload players from the database at startup
def preload_players():
    global player_cache
    logging.info("Preloading player database into cache...")
    try:
        all_players = db.all()  # This returns a dictionary, not a list
        if isinstance(all_players, dict):  # Ensure it's a dictionary
            player_cache = all_players  # Directly assign to cache
            logging.info(f"Loaded {len(player_cache)} players into cache.")
        else:
            logging.error("Database returned unexpected data format!")
    except Exception as e:
        logging.error(f"Failed to preload database: {e}")

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

API_ID = 17143425  # Replace with your actual API ID
API_HASH = "30a4231769abd4308b12b2b36147b6d0"  # Replace with your actual API hash
SESSION_STRING = "BQEFloEAV3VkCrTzWsqODlCmZHYjAsswfvmE2EsmeFGqP97nwybgCBJzxufta_1mZWJZiYNttNMSIrfP39rQuFNdMMNnNZVIWrNzKhcLKDnw8qja71QuV8y2UE9JVwo3qjnoYUQBfoLiVCmEyzrPho2zg7t_-3vYz4-mjYGoLUssJ_yr1EEqKFw5OFlctNNbl19F_3kxfyasj_ake4kvw3Ay7XOJBewLxghHu__UqODR2HzkxJgVgLohlbNMl9LaNAZW-y5tD_NAkPtaLQ9nH4_RtN12BYwDIXjmab0UgpgQTtIkmPVJSJtkvxZH1eiXHLaFHJyCP0j0M8P95rYnpzd9T7NlRAAAAAGbAPHRAA"  # Replace with your actual session string

# Initialize Pyrogram bot
bot = Client(
    "pro",
    api_id=int(API_ID),
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workers=20,  
    max_concurrent_transmissions=10  
)

# Define Target Group (Replace with actual group ID)
TARGET_GROUP_ID = -1002395952299  

# Channel where rare cards should be logged
EXCLUSIVE_CARDS_CHANNEL = -1002254491223  

# List of rarities to log
RARITIES_TO_LOG = {"Cosmic", "Limited Edition", "Exclusive", "Ultimate"}

# Control flag for collect function
collect_running = False

@bot.on_message(filters.command("startcollect") & filters.chat(TARGET_GROUP_ID) & filters.user([7508462500, 1710597756, 6895497681, 7435756663, 7859049019]))
async def start_collect(_, message: Message):
    global collect_running
    if not collect_running:
        collect_running = True
        await message.reply("✅ Collect function started!")
    else:
        await message.reply("⚠ Collect function is already running!")

@bot.on_message(filters.command("stopcollect") & filters.chat(TARGET_GROUP_ID) & filters.user([7508462500, 1710597756, 6895497681, 7435756663, 7859049019]))
async def stop_collect(_, message: Message):
    global collect_running
    collect_running = False
    await message.reply("🛑 Collect function stopped!")

@bot.on_message(filters.photo & filters.chat(TARGET_GROUP_ID) & filters.user([7522153272, 7946198415, 7742832624, 1710597756, 7828242164, 7957490622, 7859049019]))
async def hacke(c: Client, m: Message):
    global collect_running
    if not collect_running:
        return

    try:
        await asyncio.sleep(random.uniform(0.2, 0.6))  

        if not m.caption:
            return  

        logging.debug(f"Received caption: {m.caption}")

        if "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴘʟᴀʏᴇʀ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ" not in m.caption:
            return  

        file_id = m.photo.file_unique_id

        if file_id in player_cache:
            player_name = player_cache[file_id]['name']
        else:
            file_data = db.get(file_id)
            if file_data:
                player_name = file_data['name']
                player_cache[file_id] = file_data  
            else:
                logging.warning(f"Image ID {file_id} not found in DB!")
                return

        logging.info(f"Collecting player: {player_name}")
        response = await bot.send_message(m.chat.id, f"/collect {player_name}")

        await asyncio.sleep(2)  

        async for reply in bot.iter_history(m.chat.id, limit=15):
            if reply.reply_to_message and reply.reply_to_message.message_id == response.message_id:
                for rarity in RARITIES_TO_LOG:
                    if f"🟡 Rarity : {rarity}" in reply.text:
                        logging.info(f"Logging {rarity} card: {player_name}")
                        await bot.forward_messages(EXCLUSIVE_CARDS_CHANNEL, reply.chat.id, reply.message_id)
                        break
                break  

    except FloodWait as e:
        wait_time = e.value + random.randint(1, 5)  
        logging.warning(f"Rate limit hit! Waiting for {wait_time} seconds...")
        await asyncio.sleep(wait_time)
    except Exception as e:
        logging.error(f"Error processing message: {e}")

@bot.on_message(filters.command("fileid") & filters.chat(TARGET_GROUP_ID) & filters.reply & filters.user([7508462500, 1710597756, 6895497681, 7435756663]))
async def extract_file_id(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("⚠ Please reply to a photo to extract the file ID.")
        return
    
    file_unique_id = message.reply_to_message.photo.file_unique_id
    await message.reply(f"📂 **File Unique ID:** `{file_unique_id}`")

async def main():
    preload_players()  
    await bot.start()
    logging.info("Bot started successfully!")
    await asyncio.gather(run_flask(), idle())
    await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())