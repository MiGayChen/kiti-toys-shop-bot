import os

import asyncpg

pool = None

async def init_pool():
	global pool
	pool = await asyncpg.create_pool(
		dsn=os.environ["DATABASE_URL"],
		min_size=1,
		max_size=5,
	)

async def close_pool():
	if pool is not None:
		await pool.close()