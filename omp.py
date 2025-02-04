import os
from pyrogram import Client, filters
from flask import flask

web_app = Flask(__name__)

@web_app.route('/health')
def health_check():
    return "OK", 200

def run_flask():
    web_app.run(host="0.0.0.0", port=8000)

# Set up API credentials
API_ID = int(os.getenv("API_ID", "0"))  
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("image_id_bot",API_ID, API_HASH, BOT_TOKEN)

@app.on_message(filters.photo)
async def get_image_id(client, message):
    photo = message.photo
    file_id = photo.file_id  # This gives IDs like AgADx7UxG8GYPFI
    unique_id = photo.file_unique_id  # Unique ID (does not change)

    print(f"File ID: {file_id}")
    print(f"Unique File ID: {unique_id}")

    # Reply with the image ID
    await message.reply_text(f"**File ID:** `{file_id}`\n**Unique File ID:** `{unique_id}`")

app.run()
