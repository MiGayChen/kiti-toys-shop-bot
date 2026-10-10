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