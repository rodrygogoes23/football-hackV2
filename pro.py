import os
import logging
import asyncio
import random
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from Mukund import Mukund

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Initialize Database
storage = Mukund("Vegeta")
db = storage.database("football")

# In-memory cache for quick lookups
player_cache = {}

# Preload players from the database at startup
def preload_players():
    global player_cache
    logging.info("Preloading player database into cache...")
    try:
        all_players = db.all()
        if isinstance(all_players, dict):
            player_cache = all_players
            logging.info(f"Loaded {len(player_cache)} players into cache.")
        else:
            logging.error("Database returned unexpected data format!")
    except Exception as e:
        logging.error(f"Failed to preload database: {e}")

API_ID = 17143425  
API_HASH = "30a4231769abd4308b12b2b36147b6d0"
SESSION_STRING = "BQEFloEAV3VkCrTzWsqODlCmZHYjAsswfvmE2EsmeFGqP97nwybgCBJzxufta_1mZWJZiYNttNMSIrfP39rQuFNdMMNnNZVIWrNzKhcLKDnw8qja71QuV8y2UE9JVwo3qjnoYUQBfoLiVCmEyzrPho2zg7t_-3vYz4-mjYGoLUssJ_yr1EEqKFw5OFlctNNbl19F_3kxfyasj_ake4kvw3Ay7XOJBewLxghHu__UqODR2HzkxJgVgLohlbNMl9LaNAZW-y5tD_NAkPtaLQ9nH4_RtN12BYwDIXjmab0UgpgQTtIkmPVJSJtkvxZH1eiXHLaFHJyCP0j0M8P95rYnpzd9T7NlRAAAAAGbAPHRAA"

bot = Client(
    "pro",
    api_id=int(API_ID),
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Group and Forwarding Channel
TARGET_GROUP_ID = -1002395952299  
EXCLUSIVE_CARDS_CHANNEL = -1002254491223  

# Rarities to Log & Forward
RARITIES_TO_LOG = ["Cosmic", "Limited Edition", "Exclusive", "Ultimate"]

# Control flag for collect function
collect_running = False

@bot.on_message(filters.command("startcollect") & filters.chat(TARGET_GROUP_ID) & filters.user([7508462500, 1710597756, 6895497681, 7859049019, 7435756663]))
async def start_collect(_, message: Message):
    global collect_running
    if not collect_running:
        collect_running = True
        await message.reply("✅ Collect function started!")
    else:
        await message.reply("⚠ Collect function is already running!")

@bot.on_message(filters.command("stopcollect") & filters.chat(TARGET_GROUP_ID) & filters.user([7508462500, 1710597756, 6895497681, 7859049019, 7435756663]))
async def stop_collect(_, message: Message):
    global collect_running
    collect_running = False
    await message.reply("🛑 Collect function stopped!")

@bot.on_message(filters.photo & filters.chat(TARGET_GROUP_ID) & filters.user([7522153272, 7946198415, 7742832624, 1710597756, 7859049019, 7828242164, 7957490622]))
async def hacke(c: Client, m: Message):
    global collect_running
    if not collect_running:
        return

    try:
        await asyncio.sleep(random.uniform(0.2, 0.6))

        if not m.caption:
            return  

        logging.debug(f"Received caption: {m.caption}")

        # Only process OG Player messages
        if "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴘʟᴀʏᴇʀ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ" not in m.caption:
            return  

        logging.info(f"Collecting player from message: {m.caption}")
        response = await bot.send_message(m.chat.id, f"/collect {m.caption.split(' ')[-1]}")

        await asyncio.sleep(2)  # Ensure the bot's reply is received

        async for reply in bot.get_chat_history(m.chat.id, limit=50):
            if not reply.text:
                continue  

            logging.info(f"✅ Checking reply message: {reply.text}")

            for rarity in RARITIES_TO_LOG:
                if f"🎯 Look You Collected A {rarity} Player !!" in reply.text:
                    logging.info(f"🎯 Detected {rarity} card, Forwarding...")

                    try:
                        await bot.forward_messages(EXCLUSIVE_CARDS_CHANNEL, reply.chat.id, reply.message_id)
                        logging.info(f"✅ Successfully forwarded {rarity} card")
                    except Exception as e:
                        logging.error(f"❌ Error forwarding message: {e}")

                    break  # Stop checking once a rarity match is found
            break  # Exit loop after processing the first valid message

    except FloodWait as e:
        wait_time = e.value + random.randint(1, 5)
        logging.warning(f"Rate limit hit! Waiting for {wait_time} seconds...")
        await asyncio.sleep(wait_time)
    except Exception as e:
        logging.error(f"Error processing message: {e}")

async def main():
    preload_players()
    await bot.start()
    logging.info("Bot started successfully!")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())