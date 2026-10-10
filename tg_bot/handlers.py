from telegram import Update
from telegram.ext import ContextTypes

from core import repository
from core.texts import WELCOME, CHOOSE_CATEGORY, CHOOSE_PRODUCT
from core.formatting import format_products_list
from tg_bot.keyboards import categories_keyboard, products_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	categories = await repository.get_categories()
	keyboard = categories_keyboard(categories)
	await update.message.reply_text(
		WELCOME + "\n\n" + CHOOSE_CATEGORY,
		reply_markup=keyboard,
		)

async def show_products(update, context):
    query = update.callback_query
    await query.answer()

    category_id = int(query.data.split(":")[1])
    products = await repository.get_products(category_id)

    text = CHOOSE_PRODUCT + "\n\n" + format_products_list(products)
    keyboard = products_keyboard(products)

    await query.edit_message_text(text, reply_markup=keyboard)