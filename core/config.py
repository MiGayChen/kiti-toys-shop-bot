import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
	raise SystemExit("Задай токен в .env")


OWNER_ID = int(os.getenv("OWNER_ID", "0"))