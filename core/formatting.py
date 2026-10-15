from core.texts import CART_TITLE, CART_TOTAL

def format_price(price):
	rub, kop = divmod(price, 100)
	return f"{rub},{kop:02d} ₽"

def format_products_list(products):
    lines = []
    for product in products:
        lines.append(f"{product['name']} — {format_price(product['price'])}")
    return "\n".join(lines)

def format_product_card(product):
    return (
        f"{product['name']}\n\n"
        f"{product['description']}\n\n"
        f"Цена: {format_price(product['price'])}"
        )

def format_cart(items):
    lines = [CART_TITLE, ""]
    total = 0
    for item in items:
        lines.append(
            f"{item['name']} × {item['qty']} — {format_price(item['subtotal'])}"
        )
        total += item["subtotal"]
    lines.append("")
    lines.append(f"{CART_TOTAL} {format_price(total)}")
    return "\n".join(lines)