from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from database.config import admin
from database.database import LocalSession
from database.models import User, Admin


def send_payment_to_admin(
    update: Update,
    context: CallbackContext,
    *,
    bot,
    user,
    amount,
    file_id,
    is_photo=True
    ):
    with LocalSession() as session:
        # 👥 Oddiy adminlar
        admins = session.query(Admin).all()
    
    bot = context.bot
    user = update._effective_user
    
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Tasdiqlash",
                callback_data=f"pay:ok:{user.id}:{amount}"
            ),
            InlineKeyboardButton(
                "❌ Rad etish",
                callback_data=f"pay:no:{user.id}"
            )
        ]
    ]

    caption = (
        "💰 Balans to'ldirish\n\n"
        f"👤 {user.name}\n"
        f"🆔 {user.id}\n"
        f"💵 {amount:,} so'm"
    )


# Super adminga yuborish
    if is_photo:
        bot.send_photo(
            chat_id=admin.SUPERADMIN_ID,
            photo=file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        bot.send_document(
            chat_id=admin.SUPERADMIN_ID,
            document=file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Boshqa adminlarga yuborish
    for a in admins:
        if a.telegram_id == admin.SUPERADMIN_ID:
            continue  # Super adminni o'tkazib yuborish
        if is_photo:
            bot.send_photo(
                chat_id=a.telegram_id,
                photo=file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            bot.send_document(
                chat_id=a.telegram_id,
                document=file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


def payment_decision(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    _, action, user_id, *rest = query.data.split(":")
    user_id = int(user_id)

    with LocalSession() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if action == "ok":
            amount = int(rest[0])
            user.balance += amount
            session.commit()

            context.bot.send_message(
                chat_id=user_id,
                text=f"✅ Balansingiz {amount:,} so'mga to'ldirildi"
            )
            query.edit_message_caption("✅ To'lov tasdiqlandi")

        else:
            context.bot.send_message(
                chat_id=user_id,
                text="❌ To'lov rad etildi"
            )
            query.edit_message_caption("❌ To'lov rad etildi")
