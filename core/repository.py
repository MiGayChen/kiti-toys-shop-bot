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