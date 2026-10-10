from telegram import Update
from telegram.ext import ContextTypes

from core import repository
from core.texts import WELCOME, CHOOSE_CATEGORY, CHOOSE_PRODUCT, PRODUCT_NOT_FOUND
from core.formatting import format_products_list, format_product_card
from tg_bot.keyboards import categories_keyboard, products_keyboard, product_card_keyboard

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

async def back_to_categories(update, context):
    query = update.callback_query
    await query.answer()

    categories = await repository.get_categories()
    keyboard = categories_keyboard(categories)

    await query.edit_message_text(CHOOSE_CATEGORY, reply_markup=keyboard)

async def show_product_card(update, context):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split(":")[1])
    product = await repository.get_product(product_id)

    if product is None:
        await query.edit_message_text(PRODUCT_NOT_FOUND)
        return

    text = format_product_card(product)
    keyboard = product_card_keyboard(product["category_id"])
    await query.edit_message_text(text, reply_markup=keyboard)
