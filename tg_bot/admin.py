from core.config import ADMIN_IDS
from core.texts import ADMIN_PANEL

def is_admin(update):
	user = update.effective_user
	return user is not None and user.id in ADMIN_IDS

async def admin_panel(update, context):
	if not is_admin(update):
		return
	await update.message.reply_text(ADMIN_PANEL)