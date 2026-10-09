def format_price(price):
	rub, kop = divmod(price, 100)
	return f"{rub},{kop:02d} ₽"
