from datetime import datetime, timezone

from core.formatting import format_cart, format_order, format_price, parse_price


def test_parse_price_valid():
    assert parse_price("499") == 49900
    assert parse_price("499,50") == 49950
    assert parse_price("499.5") == 49950
    assert parse_price("  10  ") == 1000


def test_parse_price_invalid():
    for text in ["abc", "", "0", "-5", "1.234", "12,", "1000000.01"]:
        assert parse_price(text) is None


def test_format_price():
    assert format_price(49900) == "499,00 ₽"
    assert format_price(5) == "0,05 ₽"


def test_format_cart_total():
    items = [
        {"name": "Мячик", "qty": 2, "subtotal": 20000},
        {"name": "Мышка", "qty": 1, "subtotal": 5000},
    ]
    text = format_cart(items)
    assert "Мячик × 2" in text
    assert "250,00 ₽" in text


def test_format_order_uses_shop_timezone():
    order = {
        "id": 7,
        "status": "new",
        "name": "Тест",
        "total": 100,
        "created_at": datetime(2026, 10, 29, 15, 0, tzinfo=timezone.utc),
    }
    text = format_order(order, [])
    assert "Заказ №7" in text
    assert "29.10.2026 15:00" in text
