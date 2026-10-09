from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
    return InlineKeyboardMarkup(rows)