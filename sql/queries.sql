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

-- get_or_create_user(platform, platform_user_id, name): найти или создать пользователя, вернуть его id
-- ON CONFLICT: пара (platform, platform_user_id) уникальна, повторный /start не создаёт дубль
INSERT INTO users (platform, platform_user_id, name)
VALUES ('tg', 123456789, 'Тест')
ON CONFLICT (platform, platform_user_id) DO UPDATE SET name = EXCLUDED.name
RETURNING id;

-- get_all_products(): все товары для админки, включая скрытые
-- Без фильтра is_active: админ должен видеть и выключенные товары, чтобы вернуть их
SELECT id, name, price, is_active
FROM products
ORDER BY id;

-- toggle_product(product_id): скрыть или вернуть товар одним запросом
-- NOT is_active переворачивает значение: TRUE становится FALSE и наоборот
-- RETURNING сразу отдаёт новое состояние; если товара нет, вернётся 0 строк (в Python это None)
UPDATE products
SET is_active = NOT is_active
WHERE id = 1
RETURNING id, name, is_active;

-- add_to_cart(user_id, product_id): добавить товар в корзину
-- ON CONFLICT: такой товар уже в корзине, тогда qty увеличивается на 1
INSERT INTO cart_items (user_id, product_id, qty)
VALUES (1, 1, 1)
ON CONFLICT (user_id, product_id)
DO UPDATE SET qty = cart_items.qty + 1;

-- get_cart(user_id): содержимое корзины с суммой по каждой строке
-- p.is_active = TRUE: выключенные товары в корзине не показываем
SELECT p.id AS product_id, p.name, p.price, ci.qty,
       p.price * ci.qty AS subtotal
FROM cart_items ci
JOIN products p ON p.id = ci.product_id
WHERE ci.user_id = 1 AND p.is_active = TRUE
ORDER BY p.id;

-- clear_cart(user_id): очистить корзину пользователя
DELETE FROM cart_items WHERE user_id = 1;

-- create_order(user_id): оформить заказ, выполняется в ОДНОЙ транзакции
-- 1) шапка заказа с итогом (HAVING COUNT(*) > 0: пустую корзину не оформляем)
-- 2) строки заказа с копией названия и цены
-- 3) очистка корзины
BEGIN;

INSERT INTO orders (user_id, total)
SELECT 1, SUM(p.price * ci.qty)
FROM cart_items ci
JOIN products p ON p.id = ci.product_id
WHERE ci.user_id = 1 AND p.is_active = TRUE
HAVING COUNT(*) > 0
RETURNING id, total;

-- Дальше подставляется id из RETURNING вместо 2
INSERT INTO order_items (order_id, product_id, name, price, qty)
SELECT 2, p.id, p.name, p.price, ci.qty
FROM cart_items ci
JOIN products p ON p.id = ci.product_id
WHERE ci.user_id = 1 AND p.is_active = TRUE;

DELETE FROM cart_items WHERE user_id = 1;

COMMIT;

-- get_open_orders(): заказы в работе (новые и подтверждённые), сначала свежие
-- JOIN users: берём имя покупателя; LIMIT 10: в админке показываем не больше десяти
SELECT o.id, o.status, o.total, o.created_at, u.name
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.status IN ('new', 'confirmed')
ORDER BY o.created_at DESC
LIMIT 10;

-- get_order_items(order_id): состав одного заказа
-- name и price взяты из копии в order_items, а не из каталога: цены в старых заказах не меняются
SELECT name, price, qty, price * qty AS subtotal
FROM order_items
WHERE order_id = 3
ORDER BY id;

-- set_order_status(order_id, status): сменить статус заказа
-- Допустимы только new, confirmed, shipped, done, cancelled: остальное отклонит CHECK в базе
-- RETURNING отдаёт новое состояние; если заказа нет, вернётся 0 строк (в Python это None)
UPDATE orders
SET status = 'confirmed'
WHERE id = 3
RETURNING id, status;

-- get_order(order_id): шапка одного заказа
SELECT o.id, o.status, o.total, o.created_at, u.name
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.id = 3;

-- add_category(name): добавить категорию, вернуть её id и название
-- ON CONFLICT DO NOTHING: название уникально, при повторе вернётся 0 строк (в Python это None, то есть «уже есть»)
INSERT INTO categories (name)
VALUES ('Тест')
ON CONFLICT (name) DO NOTHING
RETURNING id, name;


-- rename_category(category_id, name): переименовать категорию
-- Если категории нет, вернётся 0 строк (в Python это None)
-- Если название занято, база вернёт ошибку UNIQUE (в Python это UniqueViolationError)
UPDATE categories
SET name = 'Тест3'
WHERE id = 1
RETURNING id, name;