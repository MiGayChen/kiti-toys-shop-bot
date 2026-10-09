from telegram import Update
from telegram.ext import ContextTypes

from core import repository
from core.texts import WELCOME, CHOOSE_CATEGORY
from tg_bot.keyboards import categories_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	categories = await repository.get_categories()
	keyboard = categories_keyboard(categories)
	await update.message.reply_text(
		WELCOME + "\n\n" + CHOOSE_CATEGORY,
		reply_markup=keyboard,
		)
