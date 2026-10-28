from core import db
import asyncpg

async def get_categories():
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name FROM categories ORDER BY id")
    return [dict(r) for r in rows]


async def get_product(product_id):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, category_id, name, description, price, image "
            "FROM products WHERE id = $1 AND is_active = TRUE ",
            product_id,
        )
    return dict(row) if row else None


async def get_products(category_id):
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, category_id, name, description, price, image "
            "FROM products WHERE category_id = $1 AND is_active = TRUE "
            "ORDER BY id ",
            category_id,
        )
    return [dict(r) for r in rows]

async def get_or_create_user(platform, platform_user_id, name):
    async with db.pool.acquire() as conn:
        return await conn.fetchval(
            "INSERT INTO users (platform, platform_user_id, name) "
            "VALUES ($1, $2, $3) "
            "ON CONFLICT (platform, platform_user_id) "
            "DO UPDATE SET name = EXCLUDED.name "
            "RETURNING id",
            platform, platform_user_id, name,
        )


async def add_to_cart(user_id, product_id):
    async with db.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO cart_items (user_id, product_id, qty) "
            "VALUES ($1, $2, 1) "
            "ON CONFLICT (user_id, product_id) "
            "DO UPDATE SET qty = cart_items.qty + 1 ",
            user_id, product_id,
        )


async def get_cart(user_id):
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT p.id AS product_id, p.name, p.price, ci.qty, "
            "p.price * ci.qty AS subtotal "
            "FROM cart_items ci "
            "JOIN products p ON p.id = ci.product_id "
            "WHERE ci.user_id = $1 AND p.is_active = TRUE "
            "ORDER BY p.id",
            user_id,
        )
    return [dict(r) for r in rows]


async def clear_cart(user_id):
    async with db.pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM cart_items WHERE user_id = $1",
            user_id,
        )

async def create_order(user_id):
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            order = await conn.fetchrow(
                "INSERT INTO orders (user_id, total) "
                "SELECT $1::int, SUM(p.price * ci.qty) "
                "FROM cart_items ci "
                "JOIN products p ON p.id = ci.product_id "
                "WHERE ci.user_id = $1 AND p.is_active = TRUE "
                "HAVING COUNT(*) > 0 "
                "RETURNING id, total ",
                user_id,
            )
            if order is None:
                return None

            await conn.execute(
                "INSERT INTO order_items (order_id, product_id, name, price, qty) "
                "SELECT $1, p.id, p.name, p.price, ci.qty "
                "FROM cart_items ci "
                "JOIN products p ON p.id = ci.product_id "
                "WHERE ci.user_id = $2 AND p.is_active = TRUE ",
                order["id"], user_id,
            )
            await conn.execute(
                "DELETE FROM cart_items WHERE user_id = $1",
                user_id,
            )
    return dict(order)

async def get_all_products():
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, name, price, is_active "
            "FROM products ORDER BY id "
            )
        return [dict(r) for r in rows]

async def toggle_product(product_id):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE products SET is_active = NOT is_active "
            "WHERE id = $1 "
            "RETURNING id, name, is_active ",
            product_id,
        )
    return dict(row) if row else None

async def add_product(category_id, name, description, price):
    async with db.pool.acquire() as conn:
        return await conn.fetchval(
            "INSERT INTO products (category_id, name, description, price) "
            "VALUES ($1, $2, $3, $4) "
            "RETURNING id ",
            category_id, name, description, price,
        )

async def get_open_orders():
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT o.id, o.status, o.total, o.created_at, u.name "
            "FROM orders o "
            "JOIN users u ON u.id = o.user_id "
            "WHERE o.status IN ('new', 'confirmed') "
            "ORDER BY o.created_at DESC "
            "LIMIT 10"
        )
    return [dict(r) for r in rows]


async def get_order(order_id):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT o.id, o.status, o.total, o.created_at, u.name "
            "FROM orders o "
            "JOIN users u ON u.id = o.user_id "
            "WHERE o.id = $1",
            order_id,
        )
    return dict(row) if row else None


async def get_order_items(order_id):
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT name, price, qty, price * qty AS subtotal "
            "FROM order_items "
            "WHERE order_id = $1 "
            "ORDER BY id",
            order_id,
        )
    return [dict(r) for r in rows]


async def set_order_status(order_id, status):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE orders SET status = $2 "
            "WHERE id = $1 "
            "RETURNING id, status",
            order_id, status,
        )
    return dict(row) if row else None

async def add_category(name):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO categories (name) "
            "VALUES ($1) "
            "ON CONFLICT (name) DO NOTHING "
            "RETURNING id, name",
            name,
        )
    return dict(row) if row else None


class CategoryExists(Exception):
    pass


async def rename_category(category_id, name):
    async with db.pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "UPDATE categories SET name = $2 "
                "WHERE id = $1 "
                "RETURNING id, name",
                category_id, name,
            )
        except asyncpg.UniqueViolationError:
            raise CategoryExists
    return dict(row) if row else None


class CategoryNotEmpty(Exception):
    pass


async def delete_category(category_id):
    async with db.pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "DELETE FROM categories "
                "WHERE id = $1 "
                "RETURNING id, name",
                category_id,
            )
        except asyncpg.ForeignKeyViolationError:
            raise CategoryNotEmpty
    return dict(row) if row else None


async def get_product_admin(product_id):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, category_id, name, description, price, image, is_active "
            "FROM products WHERE id = $1",
            product_id,
        )
    return dict(row) if row else None


async def update_product(product_id, name=None, description=None, price=None):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE products "
            "SET name = COALESCE($2, name), "
            "description = COALESCE($3, description), "
            "price = COALESCE($4, price) "
            "WHERE id = $1 "
            "RETURNING id, name, description, price",
            product_id, name, description, price,
        )
    return dict(row) if row else None


async def delete_product(product_id):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "DELETE FROM products "
            "WHERE id = $1 "
            "RETURNING id, name",
            product_id,
        )
    return dict(row) if row else None


async def set_product_image(product_id, image):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE products SET image = $2 "
            "WHERE id = $1 "
            "RETURNING id, name, image",
            product_id, image,
        )
    return dict(row) if row else None