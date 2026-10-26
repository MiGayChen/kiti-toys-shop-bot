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
from core.formatting import format_price, format_product_card, format_order, parse_price
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
    ORDER_STATUS_LABELS,
    BUT_ADMIN_ORDERS,
    BUT_ORDERS_BACK,
    ADMIN_ORDERS_TITLE,
    ADMIN_NO_ORDERS,
    ORDER_NOT_FOUND,
    ORDER_STATUS_CHANGED, 
    BUT_ADMIN_ADD_CATEGORY, 
    CAT_ASK_NAME, 
    CAT_BAD_NAME, 
    CAT_EXISTS, 
    CAT_DONE, 
    CAT_CANCELLED,
    BUT_ADMIN_RENAME_CATEGORY,
    CAT_RENAME_PICK,
    CAT_RENAME_ASK,
    CAT_RENAME_DONE,
    CAT_NOT_FOUND,
    BUT_ADMIN_DELETE_CATEGORY,
    CAT_DELETE_PICK,
    CAT_DELETE_CONFIRM,
    BUT_CONFIRM_DELETE,
    CAT_DELETE_DONE,
    CAT_NOT_EMPTY,
    CAT_DELETE_CANCELLED,
)

NAME, DESCRIPTION, PRICE, CATEGORY, CONFIRM = range(5)

def is_admin(update):
    user = update.effective_user
    return user is not None and user.id in ADMIN_IDS


def panel_keyboard():
    rows = [
        [InlineKeyboardButton(BUT_ADMIN_PRODUCTS, callback_data="admin:products")],
        [InlineKeyboardButton(BUT_ADMIN_ADD, callback_data="admin:add")],
        [InlineKeyboardButton(BUT_ADMIN_ORDERS, callback_data="admin:orders")],
        [InlineKeyboardButton(BUT_ADMIN_ADD_CATEGORY, callback_data="admin:addcat")],
        [InlineKeyboardButton(BUT_ADMIN_RENAME_CATEGORY, callback_data="admin:rencat")],
        [InlineKeyboardButton(BUT_ADMIN_DELETE_CATEGORY, callback_data="admin:delcat")],
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

def orders_keyboard(orders):
    rows = []
    for order in orders:
        label = ORDER_STATUS_LABELS.get(order["status"], order["status"])
        name = order["name"] or "—"
        text = f"№{order['id']} · {label} · {format_price(order['total'])} · {name}"
        rows.append([InlineKeyboardButton(text, callback_data=f"admin:order:{order['id']}")])
    rows.append([InlineKeyboardButton(BUT_ADMIN_BACK, callback_data="admin:panel")])
    return InlineKeyboardMarkup(rows)


def order_card_keyboard(order):
    rows = []
    for status, label in ORDER_STATUS_LABELS.items():
        if status != order["status"]:
            rows.append([InlineKeyboardButton(
                f"→ {label}",
                callback_data=f"admin:status:{order['id']}:{status}",
            )])
    rows.append([InlineKeyboardButton(BUT_ORDERS_BACK, callback_data="admin:orders")])
    return InlineKeyboardMarkup(rows)


async def render_order(query, order_id):
    order = await repository.get_order(order_id)
    if order is None:
        return False
    items = await repository.get_order_items(order_id)
    await query.edit_message_text(
        format_order(order, items),
        reply_markup=order_card_keyboard(order),
    )
    return True


async def admin_orders(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return

    orders = await repository.get_open_orders()
    text = ADMIN_ORDERS_TITLE if orders else ADMIN_NO_ORDERS
    await query.edit_message_text(text, reply_markup=orders_keyboard(orders))


async def admin_order(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return

    order_id = int(query.data.split(":")[2])
    if not await render_order(query, order_id):
        await query.edit_message_text(ORDER_NOT_FOUND, reply_markup=orders_keyboard([]))


async def admin_status(update, context):
    query = update.callback_query
    if not is_admin(update):
        await query.answer()
        return

    _, _, order_id, status = query.data.split(":")
    order_id = int(order_id)
    if status not in ORDER_STATUS_LABELS:
        await query.answer()
        return

    result = await repository.set_order_status(order_id, status)
    if result is None:
        await query.answer(ORDER_NOT_FOUND, show_alert=True)
        return

    await query.answer(ORDER_STATUS_CHANGED)
    await render_order(query, order_id)

CAT_NAME = 0


async def addcat_start(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return ConversationHandler.END

    await query.edit_message_text(CAT_ASK_NAME, reply_markup=cancel_keyboard())
    return CAT_NAME


async def addcat_name(update, context):
    if not is_admin(update):
        return ConversationHandler.END

    name = update.message.text.strip()
    if not name or len(name) > 50:
        await update.message.reply_text(CAT_BAD_NAME, reply_markup=cancel_keyboard())
        return CAT_NAME

    category = await repository.add_category(name)
    if category is None:
        await update.message.reply_text(CAT_EXISTS, reply_markup=cancel_keyboard())
        return CAT_NAME

    await update.message.reply_text(
        CAT_DONE.format(name=category["name"], category_id=category["id"]),
        reply_markup=panel_keyboard(),
    )
    return ConversationHandler.END


async def addcat_cancel(update, context):
    if not is_admin(update):
        return ConversationHandler.END

    if update.callback_query:
        await update.callback_query.answer()
    await update.effective_message.reply_text(CAT_CANCELLED, reply_markup=panel_keyboard())
    return ConversationHandler.END


def add_category_conversation():
    text_filter = filters.TEXT & ~filters.COMMAND
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(addcat_start, pattern="^admin:addcat$")],
        states={
            CAT_NAME: [MessageHandler(text_filter, addcat_name)],
        },
        fallbacks=[
            CommandHandler("cancel", addcat_cancel),
            CallbackQueryHandler(addcat_cancel, pattern="^admin:cancel$"),
        ],
    )

REN_PICK, REN_NAME = range(2)


def rename_pick_keyboard(categories):
    rows = []
    for category in categories:
        rows.append([InlineKeyboardButton(
            category["name"],
            callback_data=f"admin:rencat:{category['id']}",
        )])
    rows.append([InlineKeyboardButton(BUT_CANCEL, callback_data="admin:cancel")])
    return InlineKeyboardMarkup(rows)


async def rename_start(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return ConversationHandler.END

    categories = await repository.get_categories()
    await query.edit_message_text(CAT_RENAME_PICK, reply_markup=rename_pick_keyboard(categories))
    return REN_PICK


async def rename_pick(update, context):
    query = update.callback_query
    if not is_admin(update):
        await query.answer()
        return ConversationHandler.END

    category_id = int(query.data.split(":")[2])
    categories = await repository.get_categories()
    category = next((c for c in categories if c["id"] == category_id), None)
    if category is None:
        await query.answer(CAT_NOT_FOUND, show_alert=True)
        return REN_PICK

    await query.answer()
    context.user_data["rename_category_id"] = category["id"]
    await query.edit_message_text(
        CAT_RENAME_ASK.format(name=category["name"]),
        reply_markup=cancel_keyboard(),
    )
    return REN_NAME


async def rename_name(update, context):
    if not is_admin(update):
        return ConversationHandler.END

    name = update.message.text.strip()
    if not name or len(name) > 50:
        await update.message.reply_text(CAT_BAD_NAME, reply_markup=cancel_keyboard())
        return REN_NAME

    category_id = context.user_data.get("rename_category_id")
    if category_id is None:
        await update.message.reply_text(CAT_CANCELLED, reply_markup=panel_keyboard())
        return ConversationHandler.END

    try:
        category = await repository.rename_category(category_id, name)
    except repository.CategoryExists:
        await update.message.reply_text(CAT_EXISTS, reply_markup=cancel_keyboard())
        return REN_NAME

    context.user_data.pop("rename_category_id", None)
    if category is None:
        await update.message.reply_text(CAT_NOT_FOUND, reply_markup=panel_keyboard())
        return ConversationHandler.END

    await update.message.reply_text(
        CAT_RENAME_DONE.format(name=category["name"]),
        reply_markup=panel_keyboard(),
    )
    return ConversationHandler.END


async def rename_cancel(update, context):
    if not is_admin(update):
        return ConversationHandler.END

    context.user_data.pop("rename_category_id", None)
    if update.callback_query:
        await update.callback_query.answer()
    await update.effective_message.reply_text(CAT_CANCELLED, reply_markup=panel_keyboard())
    return ConversationHandler.END


def rename_category_conversation():
    text_filter = filters.TEXT & ~filters.COMMAND
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(rename_start, pattern="^admin:rencat$")],
        states={
            REN_PICK: [CallbackQueryHandler(rename_pick, pattern="^admin:rencat:")],
            REN_NAME: [MessageHandler(text_filter, rename_name)],
        },
        fallbacks=[
            CommandHandler("cancel", rename_cancel),
            CallbackQueryHandler(rename_cancel, pattern="^admin:cancel$"),
        ],
    )

def delete_pick_keyboard(categories):
    rows = []
    for category in categories:
        rows.append([InlineKeyboardButton(
            category["name"],
            callback_data=f"admin:delcat:{category['id']}",
        )])
    rows.append([InlineKeyboardButton(BUT_ADMIN_BACK, callback_data="admin:panel")])
    return InlineKeyboardMarkup(rows)


def delete_confirm_keyboard(category_id):
    rows = [
        [InlineKeyboardButton(BUT_CONFIRM_DELETE, callback_data=f"admin:delcat_yes:{category_id}")],
        [InlineKeyboardButton(BUT_CANCEL, callback_data="admin:delcat")],
    ]
    return InlineKeyboardMarkup(rows)


async def delete_category_list(update, context):
    query = update.callback_query
    await query.answer()
    if not is_admin(update):
        return

    categories = await repository.get_categories()
    await query.edit_message_text(
        CAT_DELETE_PICK,
        reply_markup=delete_pick_keyboard(categories),
    )


async def delete_category_ask(update, context):
    query = update.callback_query
    if not is_admin(update):
        await query.answer()
        return

    category_id = int(query.data.split(":")[2])
    categories = await repository.get_categories()
    category = next((c for c in categories if c["id"] == category_id), None)
    if category is None:
        await query.answer(CAT_NOT_FOUND, show_alert=True)
        return

    await query.answer()
    await query.edit_message_text(
        CAT_DELETE_CONFIRM.format(name=category["name"]),
        reply_markup=delete_confirm_keyboard(category["id"]),
    )


async def delete_category_yes(update, context):
    query = update.callback_query
    if not is_admin(update):
        await query.answer()
        return

    category_id = int(query.data.split(":")[2])
    try:
        category = await repository.delete_category(category_id)
    except repository.CategoryNotEmpty:
        await query.answer(CAT_NOT_EMPTY, show_alert=True)
        return

    if category is None:
        await query.answer(CAT_NOT_FOUND, show_alert=True)
        return

    await query.answer()
    await query.edit_message_text(
        CAT_DELETE_DONE.format(name=category["name"]),
        reply_markup=panel_keyboard(),
    )