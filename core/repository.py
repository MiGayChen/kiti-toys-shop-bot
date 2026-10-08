from core.seed_data import CATEGORIES, PRODUCTS

async def get_categories():
    return CATEGORIES


async def get_product(product_id):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None

async def get_products(category_id):
    result = []
    for product in PRODUCTS:
        if product["category_id"] == category_id:
            result.append(product)
    return result