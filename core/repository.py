from core import db


async def get_categories():
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name FROM categories ORDER BY id")
    return [dict(r) for r in rows]


async def get_product(product_id):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, category_id, name, description, price, image "
            "FROM products WHERE id = $1 AND is_active = TRUE",
            product_id,
        )
    return dict(row) if row else None


async def get_products(category_id):
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, category_id, name, description, price, image "
            "FROM products WHERE category_id = $1 AND is_active = TRUE "
            "ORDER BY id",
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
            "DO UPDATE SET qty = cart_items.qty + 1",
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
                "RETURNING id, total",
                user_id,
            )
            if order is None:
                return None

            await conn.execute(
                "INSERT INTO order_items (order_id, product_id, name, price, qty) "
                "SELECT $1, p.id, p.name, p.price, ci.qty "
                "FROM cart_items ci "
                "JOIN products p ON p.id = ci.product_id "
                "WHERE ci.user_id = $2 AND p.is_active = TRUE",
                order["id"], user_id,
            )
            await conn.execute(
                "DELETE FROM cart_items WHERE user_id = $1",
                user_id,
            )
    return dict(order)