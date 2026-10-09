from telegram.ext import Application, CommandHandler

from core.config import BOT_TOKEN
from tg_bot.handlers import start

def run_bot():
	application = Application.builder().token(BOT_TOKEN).build()
	application.add_handler(CommandHandler("start", start))
	application.run_polling()