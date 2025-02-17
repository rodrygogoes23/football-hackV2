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

@bot.on_message(filters.photo & filters.user([7522153272, 7946198415, 7742832624]))
async def hacke(c: Client, m: Message):
    try:
        # Ignore messages from restricted groups
        if m.chat.id in restricted_groups:
            logging.info(f"Ignoring message from restricted group: {m.chat.id}")
            return

        await asyncio.sleep(random.uniform(0.5, 1.0))  # Small delay

        if m.caption and "/ᴄᴏʟʟᴇᴄᴛ" in m.caption:
            logging.info(f"Detected message with caption: {m.caption}")

            # Send /collect command
            await m.reply(f"/collect {m.photo.file_unique_id}")

            # Wait a bit before sending reaction message
            await asyncio.sleep(random.uniform(2.0, 4.0))  

            # Fun responses
            fun_responses = [
                "Camping ke fayde ",
                "Successfully chori kr liya",
                "OP",
                "OP bhai OP ",
                "Hell yeah! ",
                "Fuck yeah! "
            ]
            await m.reply(random.choice(fun_responses))

    except FloodWait as e:
        logging.warning(f"Rate limit hit! Waiting for {e.value} seconds...")
        await asyncio.sleep(e.value)

    except Exception as e:
        logging.error(f"Error processing message: {e}")

async def main():
    """ Runs Pyrogram bot and Flask server concurrently """
    await bot.start()
    logging.info("Bot started successfully!")
    await asyncio.gather(run_flask(), idle())
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
