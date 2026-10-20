import logging

from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from core import db
from core.config import BOT_TOKEN
from tg_bot.handlers import start, show_products, back_to_categories, show_product_card, add_to_cart_button, show_cart, clear_cart_button, checkout_button
from core.config import BOT_TOKEN, ADMIN_IDS
from tg_bot.admin import admin_panel, admin_panel_button, admin_products, admin_toggle

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def on_startup(application):
    await db.init_pool()


async def on_shutdown(application):
    await db.close_pool()

async def on_error(update, context):
    logging.error("Ошибка в обработчике", exc_info=context.error)


def run_bot():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(20)
        .read_timeout(20)
        .write_timeout(20)
        .pool_timeout(20)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_products, pattern="^cat:"))
    application.add_handler(CallbackQueryHandler(back_to_categories, pattern="^back:cats$"))
    application.add_handler(CallbackQueryHandler(show_product_card, pattern="^prod:"))
    application.add_handler(CallbackQueryHandler(add_to_cart_button, pattern="^add:"))
    application.add_handler(CallbackQueryHandler(show_cart, pattern="^cart:view$"))
    application.add_handler(CallbackQueryHandler(clear_cart_button, pattern="^cart:clear$"))
    application.add_handler(CallbackQueryHandler(checkout_button, pattern="^order:create$"))
    application.add_error_handler(on_error)
    if ADMIN_IDS:
        application.add_handler(CommandHandler("admin", admin_panel))
        application.add_handler(CallbackQueryHandler(admin_panel_button, pattern="^admin:panel$"))
        application.add_handler(CallbackQueryHandler(admin_products, pattern="^admin:products$"))
        application.add_handler(CallbackQueryHandler(admin_toggle, pattern="^admin:toggle:"))
    application.run_polling()
