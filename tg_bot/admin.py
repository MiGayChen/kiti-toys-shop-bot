from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core import repository
from core.config import ADMIN_IDS
from core.formatting import format_price
from core.texts import (
    ADMIN_PANEL,
    BUT_ADMIN_PRODUCTS,
    BUT_ADMIN_BACK,
    ADMIN_PRODUCTS_TITLE,
    PRODUCT_NOT_FOUND,
    PRODUCT_HIDDEN,
    PRODUCT_SHOWN,
)


def is_admin(update):
    user = update.effective_user
    return user is not None and user.id in ADMIN_IDS


def panel_keyboard():
    button = InlineKeyboardButton(BUT_ADMIN_PRODUCTS, callback_data="admin:products")
    return InlineKeyboardMarkup([[button]])


def products_admin_keyboard(products):
    rows = []
    for product in products:
        mark = "✅" if product["is_active"] else "🚫"
        text = f"{mark} {product['name']} — {format_price(product['price'])}"
        rows.append([InlineKeyboardButton(text, callback_data=f"admin:toggle:{product['id']}")])
    rows.append([InlineKeyboardButton(BUT_ADMIN_BACK, callback_data="admin:panel")])
    return InlineKeyboardMarkup(rows)


async def admin_panel(update, context):
    if not is_admin(update):
        return
    await update.message.reply_text(ADMIN_PANEL, reply_markup=panel_keyboard())


async def admin_panel_button(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return
    await query.edit_message_text(ADMIN_PANEL, reply_markup=panel_keyboard())


async def admin_products(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return
    products = await repository.get_all_products()
    await query.edit_message_text(
        ADMIN_PRODUCTS_TITLE,
        reply_markup=products_admin_keyboard(products),
    )


async def admin_toggle(update, context):
    query = update.callback_query
    if not is_admin(update):
        await query.answer()
        return

    product_id = int(query.data.split(":")[2])
    product = await repository.toggle_product(product_id)
    if product is None:
        await query.answer(PRODUCT_NOT_FOUND, show_alert=True)
        return

    await query.answer(PRODUCT_SHOWN if product["is_active"] else PRODUCT_HIDDEN)
    products = await repository.get_all_products()
    await query.edit_message_text(
        ADMIN_PRODUCTS_TITLE,
        reply_markup=products_admin_keyboard(products),
    )