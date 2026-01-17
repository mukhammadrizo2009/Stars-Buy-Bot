from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from database.config import admin
from admin.payments import admin_payments
from admin.users import admin_users
from admin.stats import admin_stats


def is_admin(user_id: int) -> bool:
    return user_id in [6293681152]


def admin_panel(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        update.message.reply_text("⛔ Siz admin emassiz")
        return

    keyboard = [
        [InlineKeyboardButton("💰 To'lovlar", callback_data="admin:payments")],
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin:users")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin:stats")]
    ]

    update.message.reply_text(
        "🛡 ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def admin_menu_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "admin:payments":
        admin_payments(update, context)

    elif query.data == "admin:users":
        admin_users(update, context)

    elif query.data == "admin:stats":
        admin_stats(update, context)
