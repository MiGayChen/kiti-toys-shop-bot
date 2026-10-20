from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from core import repository
from core.config import ADMIN_IDS
from core.formatting import format_price, format_product_card, parse_price
from core.texts import (
    ADMIN_PANEL,
    BUT_ADMIN_PRODUCTS,
    BUT_ADMIN_BACK,
    BUT_ADMIN_ADD,
    BUT_CANCEL,
    BUT_SAVE,
    ADMIN_PRODUCTS_TITLE,
    PRODUCT_NOT_FOUND,
    PRODUCT_HIDDEN,
    PRODUCT_SHOWN,
    ADD_ASK_NAME,
    ADD_BAD_NAME,
    ADD_CANCELLED,
    ADD_ASK_DESC,
    ADD_BAD_DESC,
    ADD_ASK_PRICE,
    ADD_BAD_PRICE,
    ADD_ASK_CATEGORY,
    ADD_NO_CATEGORY,
    ADD_CONFIRM,
    ADD_DONE,
)

NAME, DESCRIPTION, PRICE, CATEGORY, CONFIRM = range(5)

def is_admin(update):
    user = update.effective_user
    return user is not None and user.id in ADMIN_IDS


def panel_keyboard():
    rows = [
        [InlineKeyboardButton(BUT_ADMIN_PRODUCTS, callback_data="admin:products")],
        [InlineKeyboardButton(BUT_ADMIN_ADD, callback_data="admin:add")],
    ]
    return InlineKeyboardMarkup(rows)

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
def cancel_keyboard():
    button = InlineKeyboardButton(BUT_CANCEL, callback_data="admin:cancel")
    return InlineKeyboardMarkup([[button]])


def categories_pick_keyboard(categories):
    rows = []
    for category in categories:
        rows.append([InlineKeyboardButton(
            category["name"],
            callback_data=f"admin:cat:{category['id']}",
        )])
    rows.append([InlineKeyboardButton(BUT_CANCEL, callback_data="admin:cancel")])
    return InlineKeyboardMarkup(rows)


def confirm_keyboard():
    rows = [
        [InlineKeyboardButton(BUT_SAVE, callback_data="admin:save")],
        [InlineKeyboardButton(BUT_CANCEL, callback_data="admin:cancel")],
    ]
    return InlineKeyboardMarkup(rows)


async def add_start(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return ConversationHandler.END

    context.user_data["new_product"] = {}
    await query.edit_message_text(ADD_ASK_NAME, reply_markup=cancel_keyboard())
    return NAME


async def add_name(update, context):
    if not is_admin(update):
        return ConversationHandler.END

    name = update.message.text.strip()
    if not name or len(name) > 100:
        await update.message.reply_text(ADD_BAD_NAME, reply_markup=cancel_keyboard())
        return NAME

    context.user_data["new_product"]["name"] = name
    await update.message.reply_text(ADD_ASK_DESC, reply_markup=cancel_keyboard())
    return DESCRIPTION


async def add_description(update, context):
    if not is_admin(update):
        return ConversationHandler.END

    description = update.message.text.strip()
    if not description or len(description) > 500:
        await update.message.reply_text(ADD_BAD_DESC, reply_markup=cancel_keyboard())
        return DESCRIPTION

    context.user_data["new_product"]["description"] = description
    await update.message.reply_text(ADD_ASK_PRICE, reply_markup=cancel_keyboard())
    return PRICE


async def add_price(update, context):
    if not is_admin(update):
        return ConversationHandler.END

    price = parse_price(update.message.text)
    if price is None:
        await update.message.reply_text(ADD_BAD_PRICE, reply_markup=cancel_keyboard())
        return PRICE

    context.user_data["new_product"]["price"] = price
    categories = await repository.get_categories()
    await update.message.reply_text(
        ADD_ASK_CATEGORY,
        reply_markup=categories_pick_keyboard(categories),
    )
    return CATEGORY


async def add_category(update, context):
    query = update.callback_query
    if not is_admin(update):
        await query.answer()
        return ConversationHandler.END

    category_id = int(query.data.split(":")[2])
    categories = await repository.get_categories()
    category = next((c for c in categories if c["id"] == category_id), None)
    if category is None:
        await query.answer(ADD_NO_CATEGORY, show_alert=True)
        return CATEGORY

    await query.answer()
    data = context.user_data["new_product"]
    data["category_id"] = category["id"]

    text = ADD_CONFIRM.format(
        card=format_product_card(data),
        category=category["name"],
    )
    await query.edit_message_text(text, reply_markup=confirm_keyboard())
    return CONFIRM


async def add_save(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return ConversationHandler.END

    data = context.user_data.pop("new_product", {})
    if not all(key in data for key in ("name", "description", "price", "category_id")):
        await query.edit_message_text(ADD_CANCELLED, reply_markup=panel_keyboard())
        return ConversationHandler.END

    product_id = await repository.add_product(
        data["category_id"], data["name"], data["description"], data["price"],
    )
    await query.edit_message_text(
        ADD_DONE.format(product_id=product_id),
        reply_markup=panel_keyboard(),
    )
    return ConversationHandler.END


async def add_cancel(update, context):
    if not is_admin(update):
        return ConversationHandler.END

    context.user_data.pop("new_product", None)
    if update.callback_query:
        await update.callback_query.answer()
    await update.effective_message.reply_text(ADD_CANCELLED, reply_markup=panel_keyboard())
    return ConversationHandler.END


def add_product_conversation():
    text_filter = filters.TEXT & ~filters.COMMAND
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_start, pattern="^admin:add$")],
        states={
            NAME: [MessageHandler(text_filter, add_name)],
            DESCRIPTION: [MessageHandler(text_filter, add_description)],
            PRICE: [MessageHandler(text_filter, add_price)],
            CATEGORY: [CallbackQueryHandler(add_category, pattern="^admin:cat:")],
            CONFIRM: [CallbackQueryHandler(add_save, pattern="^admin:save$")],
        },
        fallbacks=[
            CommandHandler("cancel", add_cancel),
            CallbackQueryHandler(add_cancel, pattern="^admin:cancel$"),
        ],
    )