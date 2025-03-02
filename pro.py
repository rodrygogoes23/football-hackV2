import os
import logging
import asyncio
import random
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from Mukund import Mukund
from flask import Flask

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Initialize Database
storage_shahzeb = Mukund("Shahzeb")  # Initialize storage for Shahzeb
storage_jotaro = Mukund("Jotaro")    # Initialize storage for Jotaro

# Initialize databases for both
db_shahzeb = storage_shahzeb.database("football")  # Initialize the database for football
db_jotaro = storage_jotaro.database("premium")      # Initialize the database for premium

# Track active database (use db_shahzeb as default database)
current_db = db_shahzeb  # Default database
current_db_name = "Shahzeb"  # Track the name for response message

# In-memory cache for quick lookups
player_cache = {}

# Ensure that the database is properly initialized before usage
if db_shahzeb is None or db_jotaro is None:
    logging.error("Database initialization failed! Please check the Mukund database configuration.")
else:
    logging.info("Databases initialized successfully.")


# Preload players from the database at startup
def preload_players():
    global player_cache
    logging.info("Preloading player database into cache...")
    try:
        all_players = current_db.all()  # Use current_db instead of db
        if isinstance(all_players, dict):
            player_cache = all_players
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

# Bot Credentials
API_ID = "17143425"
API_HASH = "30a4231769abd4308b12b2b36147b6d0"
SESSION_STRING = "BQEFloEAV3VkCrTzWsqODlCmZHYjAsswfvmE2EsmeFGqP97nwybgCBJzxufta_1mZWJZiYNttNMSIrfP39rQuFNdMMNnNZVIWrNzKhcLKDnw8qja71QuV8y2UE9JVwo3qjnoYUQBfoLiVCmEyzrPho2zg7t_-3vYz4-mjYGoLUssJ_yr1EEqKFw5OFlctNNbl19F_3kxfyasj_ake4kvw3Ay7XOJBewLxghHu__UqODR2HzkxJgVgLohlbNMl9LaNAZW-y5tD_NAkPtaLQ9nH4_RtN12BYwDIXjmab0UgpgQTtIkmPVJSJtkvxZH1eiXHLaFHJyCP0j0M8P95rYnpzd9T7NlRAAAAAGbAPHRAA"

# Initialize Pyrogram bot
bot = Client(
    "pro",
    api_id=int(API_ID),
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workers=20,
    max_concurrent_transmissions=10
)

# Define Target Group and Forwarding Channel
TARGET_GROUP_ID = -1002395952299  
FORWARD_CHANNEL_ID = -1002254491223  

# Control flag for collect function
collect_running = False

@bot.on_message(filters.command("switchdb") & filters.chat(TARGET_GROUP_ID) & filters.user([7508462500, 1710597756, 6895497681, 7859049019, 7435756663]))
async def switch_database(_, message: Message):
    """Switch between Shahzeb and Jotaro databases."""
    global current_db, current_db_name, player_cache

    new_db_name = message.text.split(maxsplit=1)[1].strip().lower() if len(message.text.split()) > 1 else ""
    
    if new_db_name == "jotaro":
        current_db = db_jotaro
        current_db_name = "Jotaro"
    elif new_db_name == "shahzeb":
        current_db = db_shahzeb
        current_db_name = "Shahzeb"
    else:
        await message.reply("⚠ Invalid database! Use: `/switchdb shahzeb` or `/switchdb jotaro`")
        return

    preload_players()  # Reload cache with new database
    await message.reply(f"✅ Switched to **{current_db_name}** database.")

@bot.on_message(filters.command("startcollect") & filters.chat(TARGET_GROUP_ID) & filters.user([7508462500, 1710597756, 6895497681, 7859049019, 7435756663]))
async def start_collect(_, message: Message):
    global collect_running
    if not collect_running:
        collect_running = True
        await message.reply(f"✅ Collect function started using '{current_db_name}' database!")
    else:
        await message.reply("⚠ Collect function is already running!")

@bot.on_message(filters.command("stopcollect") & filters.chat(TARGET_GROUP_ID) & filters.user([7508462500, 1710597756, 6895497681, 7859049019, 7435756663]))
async def stop_collect(_, message: Message):
    global collect_running
    collect_running = False
    await message.reply("🛑 Collect function stopped!")

@bot.on_message(filters.photo & filters.chat(TARGET_GROUP_ID) & filters.user([7522153272, 7946198415, 7742832624, 7859049019, 1710597756, 7828242164, 7957490622]))
async def collect_celebrity(c: Client, m: Message):
    global collect_running
    if not collect_running:
        return

    try:
        await asyncio.sleep(random.uniform(0.2, 0.6))

        if not m.caption:
            return  

        logging.debug(f"Received caption: {m.caption}")

        # Only process OG Celebrity messages
        if "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴘʟᴀʏᴇʀ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ" not in m.caption:
            return  

        file_id = m.photo.file_unique_id

        # Use cache for quick lookup
        if file_id in player_cache:
            player_name = player_cache[file_id]['name']
        else:
            file_data = current_db.get(file_id)  # Use current_db instead of db
            if file_data:
                player_name = file_data['name']
                player_cache[file_id] = file_data  
            else:
                logging.warning(f"Image ID {file_id} not found in DB!")
                return

        logging.info(f"Collecting celebrity: {player_name}")
        await bot.send_message(m.chat.id, f"/collect {player_name}")

    except FloodWait as e:
        wait_time = e.value + random.randint(1, 5)  
        logging.warning(f"Rate limit hit! Waiting for {wait_time} seconds...")
        await asyncio.sleep(wait_time)
    except Exception as e:
        logging.error(f"Error processing message: {e}")

# Forward messages with specific rarities
RARITIES_TO_FORWARD = ["Cosmic", "Limited Edition", "Exclusive", "Ultimate"]

@bot.on_message(filters.chat(TARGET_GROUP_ID))
async def check_rarity_and_forward(_, message: Message):
    if not message.text:
        return  

    if "🎯 Look You Collected A" in message.text:
        logging.info(f"Checking message for rarity:\n{message.text}")

        for rarity in RARITIES_TO_FORWARD:
            if f"Rarity : {rarity}" in message.text:
                logging.info(f"Detected {rarity} celebrity! Forwarding...")
                await bot.send_message(FORWARD_CHANNEL_ID, message.text)
                break  

@bot.on_message(filters.command("fileid") & filters.chat(TARGET_GROUP_ID) & filters.reply & filters.user([7508462500, 1710597756, 6895497681, 7435756663]))
async def extract_file_id(_, message: Message):
    """Extracts and sends the unique file ID of a replied photo"""
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("⚠ Please reply to a photo to extract the file ID.")
        return
    
    file_unique_id = message.reply_to_message.photo.file_unique_id
    await message.reply(f"📂 **File Unique ID:** `{file_unique_id}`")

async def main():
    """ Runs Pyrogram bot and Flask server concurrently """
    preload_players()
    await bot.start()
    logging.info("Bot started successfully!")
    await asyncio.gather(run_flask(), idle())
    await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
