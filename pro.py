import os
import threading
from pyrogram import Client, filters
from pyrogram.types import Message
from Mukund import Mukund
from flask import Flask

# Create Flask app for health check
web_app = Flask(__name__)

@web_app.route('/health')
def health_check():
    return "OK", 200

def run_flask():
    web_app.run(host="0.0.0.0", port=8000)

# Initialize Mukund database
storage = Mukund("Vegeta")
db = storage.database("marvel")

# Initialize Pyrogram bot
bot = Client(
    "pro",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    session_string=os.getenv("SESSION")
)

@bot.on_message(filters.photo & filters.user([7522153272]))
async def hacke(c: Client, m: Message):
    try:
        if m.caption and "/ᴄᴏʟʟᴇᴄᴛ" in m.caption:
            file_data = db.get(f"{m.photo.file_unique_id}")
            if file_data:
                await m.reply(f"/hunt {file_data['name']}")
            else:
                await m.reply("Image not found in database!")
            return
    except Exception as e:
        print(f"Error: {e}")

# Start both Flask and Pyrogram using threading
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run()
