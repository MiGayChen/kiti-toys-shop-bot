from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from core.texts import BUT_BACK, BUT_ADD_TO_CART, BUT_CART


def categories_keyboard(categories):
    rows = []
    for category in categories:
        button = InlineKeyboardButton(
            category["name"],
            callback_data=f"cat:{category['id']}",
        )
        rows.append([button])
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