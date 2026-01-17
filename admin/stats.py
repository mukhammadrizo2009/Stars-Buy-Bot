from telegram import Update
from telegram.ext import CallbackContext

from database.database import LocalSession
from database.models import User

def admin_stats(update: Update, context: CallbackContext):
    with LocalSession() as session:
        users_count = session.query(User).count()
        total_balance = sum(u.balance for u in session.query(User).all())

    update.callback_query.message.reply_text(
        "📊 Statistika\n\n"
        f"👥 Foydalanuvchilar: {users_count}\n"
        f"💰 Umumiy balans: {total_balance:,} so‘m"
    )