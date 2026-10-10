import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from core.config import BOT_TOKEN
from tg_bot.handlers import start, show_products


logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

def run_bot():
	application = Application.builder().token(BOT_TOKEN).build()
	application.add_handler(CommandHandler("start", start))
	application.add_handler(CallbackQueryHandler(show_products, pattern="^cat:"))
	application.run_polling()