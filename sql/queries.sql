-- Запросы каталога для core/repository.py
-- Значения в условиях здесь для примера. В Python вместо них будут параметры.

-- get_categories(): все категории, по порядку
SELECT id, name
FROM categories
ORDER BY id;

-- get_products(category_id): активные товары одной категории
-- is_active = TRUE: выключенные товары не показываем
SELECT id, category_id, name, description, price, image
FROM products
WHERE category_id = 1 AND is_active = TRUE
ORDER BY id;

-- get_product(product_id): один активный товар
-- Если товара нет или он выключен, вернётся 0 строк (в Python это None)
SELECT id, category_id, name, description, price, image
FROM products
WHERE id = 2 AND is_active = TRUE;