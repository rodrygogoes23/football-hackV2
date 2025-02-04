import os
import threading
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from Mukund import Mukund
from flask import Flask

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

def run_flask():
    web_app.run(host="0.0.0.0", port=8000)

# Initialize Mukund database
storage = Mukund("Vegeta")
db = storage.database("cric")

# Initialize Pyrogram bot
bot = Client(
    "pro",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    session_string=os.getenv("SESSION")
)

@bot.on_message(filters.photo & filters.user([7742832624]))
async def hacke(c: Client, m: Message):
    try:
        if m.caption and "/ᴄᴏʟʟᴇᴄᴛ" in m.caption:
            logging.info(f"Detected message with caption: {m.caption}")  # ✅ Log detected message
            file_data = db.get(f"{m.photo.file_unique_id}")

            if file_data:
                logging.info(f"Image ID {m.photo.file_unique_id} found in DB: {file_data['name']}")
                await m.reply(f"/collect {file_data['name']}")
            else:
                logging.warning(f"Image ID {m.photo.file_unique_id} not found in DB!")
    except Exception as e:
        logging.error(f"Error processing message: {e}")

# Start both Flask and Pyrogram using threading
if __name__ == "__main__":
    logging.info("Starting Flask server and Pyrogram bot...")
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run()
