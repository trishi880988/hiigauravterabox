import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not TELEGRAM_BOT_TOKEN or not RAPIDAPI_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or RAPIDAPI_KEY. Please set them in the .env file.")

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Terabox API Configuration
TERABOX_API_URL = "https://terabox-downloader-direct-download-link-generator2.p.rapidapi.com/url"
HEADERS = {
    "x-rapidapi-host": "terabox-downloader-direct-download-link-generator2.p.rapidapi.com",
    "x-rapidapi-key": RAPIDAPI_KEY
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("👋 Welcome to the Terabox Video Downloader Bot!\n\nSend me a Terabox link, and I'll fetch the direct download link for you.")

def get_download_link(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.strip()
    
    if not user_message.startswith("http") or "terabox.com" not in user_message:
        update.message.reply_text("⚠️ Please send a valid Terabox link!")
        return
    
    try:
        response = requests.get(TERABOX_API_URL, headers=HEADERS, params={"url": user_message})
        response.raise_for_status()
        data = response.json()
        
        if "download_link" in data and data['download_link']:
            update.message.reply_text(f"📥 Download Link:\n{data['download_link']}")
        else:
            update.message.reply_text("⚠️ Could not fetch the download link. Please try again later!")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Terabox link: {e}")
        update.message.reply_text("⚠️ API Error: Unable to fetch the download link. Try again later!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        update.message.reply_text("⚠️ An unexpected error occurred. Please try again later!")

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("💡 *How to Use:*\nJust send a valid Terabox link, and I will generate a direct download link for you!\n\n🔹 Example: https://terabox.com/s/xyz123\n\n⚠️ If you face any issues, try again later.", parse_mode='Markdown')

def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_download_link))
    dp.add_error_handler(error)
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
