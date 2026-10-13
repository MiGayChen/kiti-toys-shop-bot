import logging

from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from core import db
from core.config import BOT_TOKEN
from tg_bot.handlers import start, show_products, back_to_categories, show_product_card


logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def on_startup(application):
    await db.init_pool()


async def on_shutdown(application):
    await db.close_pool()


def run_bot():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_products, pattern="^cat:"))
    application.add_handler(CallbackQueryHandler(back_to_categories, pattern="^back:cats$"))
    application.add_handler(CallbackQueryHandler(show_product_card, pattern="^prod:"))
    application.run_polling()