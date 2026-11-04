import os
from pathlib import Path
from urllib.parse import urlparse

import pytest_asyncio
from dotenv import dotenv_values

os.environ.setdefault("BOT_TOKEN", "test-token")
os.environ["SHOP_TIMEZONE"] = "UTC"

_env_file = Path(__file__).resolve().parent.parent / ".env.test"
_url = dotenv_values(_env_file).get("DATABASE_URL")
if not _url or not urlparse(_url).path.lstrip("/").endswith("_test"):
    raise SystemExit("Тесты запускаются только на базе, имя которой заканчивается на _test")
os.environ["DATABASE_URL"] = _url

from core import db  # noqa: E402


@pytest_asyncio.fixture
async def clean_db():
    await db.init_pool()
    async with db.pool.acquire() as conn:
        name = await conn.fetchval("SELECT current_database()")
        assert name.endswith("_test"), "Очистка разрешена только в тестовой базе"
        await conn.execute(
            "TRUNCATE order_items, orders, cart_items, products, categories, users "
            "RESTART IDENTITY CASCADE"
        )
    yield
    await db.close_pool()
