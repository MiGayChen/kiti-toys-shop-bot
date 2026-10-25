from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from core.texts import BUT_BACK, BUT_ADD_TO_CART, BUT_CART, BUT_CLEAR_CART, BUT_TO_CATALOG, BUT_CHECKOUT, BUT_CATALOG, BUT_HELP, BUT_TO_MENU

def categories_keyboard(categories):
    rows = []
    for category in categories:
        button = InlineKeyboardButton(
            category["name"],
            callback_data=f"cat:{category['id']}",
        )
        rows.append([button])
    rows.append([InlineKeyboardButton(BUT_TO_MENU, callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def products_keyboard(products):
    rows = []
    for product in products:
        text = product["name"]
        button = InlineKeyboardButton(
            text,
            callback_data=f"prod:{product['id']}",
        )
        rows.append([button])
    rows.append([InlineKeyboardButton(BUT_BACK, callback_data="back:cats")])

    return InlineKeyboardMarkup(rows)

def product_card_keyboard(product_id, category_id):
    rows = [
        [InlineKeyboardButton(BUT_ADD_TO_CART, callback_data=f"add:{product_id}")],
        [InlineKeyboardButton(BUT_CART, callback_data="cart:view")],
        [InlineKeyboardButton(BUT_BACK, callback_data=f"cat:{category_id}")],
    ]
    return InlineKeyboardMarkup(rows)

def cart_keyboard(has_items):
    rows = []
    if has_items:
        rows.append([InlineKeyboardButton(BUT_CHECKOUT, callback_data="order:create")])
        rows.append([InlineKeyboardButton(BUT_CLEAR_CART, callback_data="cart:clear")])
    rows.append([InlineKeyboardButton(BUT_TO_CATALOG, callback_data="back:cats")])
    rows.append([InlineKeyboardButton(BUT_TO_MENU, callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)

def main_menu_keyboard():
    rows = [
        [InlineKeyboardButton(BUT_CATALOG, callback_data="back:cats")],
        [InlineKeyboardButton(BUT_CART, callback_data="cart:view")],
        [InlineKeyboardButton(BUT_HELP, callback_data="menu:help")],
    ]
    return InlineKeyboardMarkup(rows)


def back_to_menu_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(BUT_TO_MENU, callback_data="menu:main")]])