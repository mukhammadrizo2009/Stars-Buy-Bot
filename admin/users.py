from telegram import Update
from telegram.ext import CallbackContext

from database.database import LocalSession
from database.models import User

def admin_users(update: Update, context: CallbackContext):
    with LocalSession() as session:
        users = session.query(User).order_by(User.id.desc()).limit(10).all()

    text = "👥 Oxirgi foydalanuvchilar:\n\n"
    for u in users:
        text += (
            f"👤 {u.name}\n"
            f"💰 Balans: {u.balance:,} so'm\n\n"
        )

    update.callback_query.message.reply_text(text)