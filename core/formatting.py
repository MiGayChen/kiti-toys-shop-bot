import re
from core.texts import CART_TITLE, CART_TOTAL, ORDER_STATUS_LABELS, ORDER_CARD_HEAD

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

def parse_price(text):
    text = text.strip().replace(",", ".")
    if not re.fullmatch(r"[0-9]+(\.[0-9]{1,2})?", text):
        return None
    rub, _, kop = text.partition(".")
    price = int(rub) * 100 + int(kop.ljust(2, "0") or 0)
    if price <= 0 or price > 100_000_000:
        return None
    return price

def format_order(order, items):
    head = ORDER_CARD_HEAD.format(
        order_id=order["id"],
        status=ORDER_STATUS_LABELS.get(order["status"], order["status"]),
        name=order["name"] or "—",
        created=order["created_at"].astimezone().strftime("%d.%m.%Y %H:%M"),
    )
    lines = [head, ""]
    for item in items:
        lines.append(
            f"{item['name']} × {item['qty']} — {format_price(item['subtotal'])}"
        )
    lines.append("")
    lines.append(f"{CART_TOTAL} {format_price(order['total'])}")
    return "\n".join(lines)