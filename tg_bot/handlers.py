import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from core import repository
from core.config import OWNER_ID
from core.texts import WELCOME, CHOOSE_CATEGORY, CHOOSE_PRODUCT, PRODUCT_NOT_FOUND, ADDED_TO_CART, CART_EMPTY, CART_CLEARED, ORDER_CREATED, OWNER_NEW_ORDER, MAIN_MENU, HELP_TEXT, CATEGORY_EMPTY
from core.formatting import format_products_list, format_product_card, format_cart, format_price
from tg_bot.keyboards import categories_keyboard, products_keyboard, product_card_keyboard, cart_keyboard, main_menu_keyboard, back_to_menu_keyboard

async def edit_or_send(query, text, reply_markup):
    if query.message.photo:
        await query.message.delete()
        await query.message.chat.send_message(text, reply_markup=reply_markup)
    else:
        await query.edit_message_text(text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME + "\n\n" + MAIN_MENU,
        reply_markup=main_menu_keyboard(),
    )


async def help_command(update, context):
    await update.message.reply_text(HELP_TEXT, reply_markup=back_to_menu_keyboard())


async def help_button(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(HELP_TEXT, reply_markup=back_to_menu_keyboard())


async def main_menu_button(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(MAIN_MENU, reply_markup=main_menu_keyboard())

async def show_products(update, context):
    query = update.callback_query
    await query.answer()

    category_id = int(query.data.split(":")[1])
    products = await repository.get_products(category_id)
    if not products:
        await edit_or_send(query, CATEGORY_EMPTY, products_keyboard(products))
        return

    text = CHOOSE_PRODUCT + "\n\n" + format_products_list(products)
    keyboard = products_keyboard(products)

    await edit_or_send(query, text, keyboard)

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
        await edit_or_send(query, PRODUCT_NOT_FOUND, None)
        return

    text = format_product_card(product)
    keyboard = product_card_keyboard(product["id"], product["category_id"])

    if product["image"]:
        try:
            await query.message.chat.send_photo(
                product["image"], caption=text, reply_markup=keyboard,
            )
        except BadRequest:
            logging.exception("Не удалось отправить фото товара")
        else:
            await query.message.delete()
            return

    await edit_or_send(query, text, keyboard)

async def add_to_cart_button(update, context):
    query = update.callback_query

    product_id = int(query.data.split(":")[1])
    product = await repository.get_product(product_id)

    if product is None:
        await query.answer(PRODUCT_NOT_FOUND, show_alert=True)
        return

    user = update.effective_user
    user_id = await repository.get_or_create_user("tg", user.id, user.full_name)
    await repository.add_to_cart(user_id, product_id)

    await query.answer(ADDED_TO_CART)

async def show_cart(update, context):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    user_id = await repository.get_or_create_user("tg", user.id, user.full_name)
    items = await repository.get_cart(user_id)

    if not items:
        await edit_or_send(query, CART_EMPTY, cart_keyboard(False))
        return

    await edit_or_send(query, format_cart(items), cart_keyboard(True))

async def clear_cart_button(update, context):
    query = update.callback_query
    await query.answer(CART_CLEARED)

    user = update.effective_user
    user_id = await repository.get_or_create_user("tg", user.id, user.full_name)
    await repository.clear_cart(user_id)

    await query.edit_message_text(CART_EMPTY, reply_markup=cart_keyboard(False))

async def checkout_button(update, context):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    user_id = await repository.get_or_create_user("tg", user.id, user.full_name)
    order = await repository.create_order(user_id)

    if order is None:
        await query.edit_message_text(CART_EMPTY, reply_markup=cart_keyboard(False))
        return

    text = ORDER_CREATED.format(
        order_id=order["id"],
        total=format_price(order["total"]),
    )
    await query.edit_message_text(text, reply_markup=cart_keyboard(False))
    if OWNER_ID:
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=OWNER_NEW_ORDER.format(
                    order_id=order["id"],
                    name=user.full_name,
                    total=format_price(order["total"]),
                ),
            )
        except Exception:
            logging.exception("Не удалось уведомить владельца")
