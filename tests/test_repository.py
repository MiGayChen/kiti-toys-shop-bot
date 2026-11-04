import pytest

from core import repository


async def make_product(price=10000, name="Мячик"):
    category = await repository.add_category("Мячики")
    product_id = await repository.add_product(category["id"], name, "Описание", price)
    return category["id"], product_id


async def make_user():
    return await repository.get_or_create_user("tg", 1, "Тест")


async def test_add_category_duplicate_returns_none(clean_db):
    assert await repository.add_category("Мячики") is not None
    assert await repository.add_category("Мячики") is None


async def test_rename_category_duplicate_raises(clean_db):
    await repository.add_category("Мячики")
    other = await repository.add_category("Мышки")
    with pytest.raises(repository.CategoryExists):
        await repository.rename_category(other["id"], "Мячики")


async def test_cart_sums_quantity(clean_db):
    _, product_id = await make_product()
    user_id = await make_user()
    await repository.add_to_cart(user_id, product_id)
    await repository.add_to_cart(user_id, product_id)
    cart = await repository.get_cart(user_id)
    assert cart[0]["qty"] == 2
    assert cart[0]["subtotal"] == 20000


async def test_create_order_empty_cart_returns_none(clean_db):
    user_id = await make_user()
    assert await repository.create_order(user_id) is None


async def test_create_order_copies_items_and_clears_cart(clean_db):
    _, product_id = await make_product()
    user_id = await make_user()
    await repository.add_to_cart(user_id, product_id)
    await repository.add_to_cart(user_id, product_id)

    order = await repository.create_order(user_id)
    assert order["total"] == 20000
    assert await repository.get_cart(user_id) == []

    await repository.update_product(product_id, price=99900)
    items = await repository.get_order_items(order["id"])
    assert items[0]["price"] == 10000
    assert items[0]["qty"] == 2


async def test_hidden_product_is_not_ordered(clean_db):
    _, product_id = await make_product()
    user_id = await make_user()
    await repository.add_to_cart(user_id, product_id)
    await repository.toggle_product(product_id)
    assert await repository.get_cart(user_id) == []
    assert await repository.create_order(user_id) is None


async def test_delete_category_with_products_raises(clean_db):
    category_id, _ = await make_product()
    with pytest.raises(repository.CategoryNotEmpty):
        await repository.delete_category(category_id)


async def test_delete_product_keeps_old_orders(clean_db):
    _, product_id = await make_product()
    user_id = await make_user()
    await repository.add_to_cart(user_id, product_id)
    order = await repository.create_order(user_id)
    await repository.add_to_cart(user_id, product_id)

    assert await repository.delete_product(product_id) is not None

    items = await repository.get_order_items(order["id"])
    assert items[0]["name"] == "Мячик"
    assert await repository.get_cart(user_id) == []


async def test_update_product_changes_only_given_field(clean_db):
    _, product_id = await make_product()
    product = await repository.update_product(product_id, name="Новое имя")
    assert product["name"] == "Новое имя"
    assert product["price"] == 10000
