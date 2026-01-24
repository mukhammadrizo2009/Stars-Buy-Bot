from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from database.config import admin, PAYMENT
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
    ],
    [
        InlineKeyboardButton(
            "✏️ Boshqa summa kiritish",
            callback_data=f"pay:custom:{user.id}"
        )
    ]
]

    caption = (
        "💰 Balans to'ldirish\n\n"
        f"👤 {user.name}\n"
        f"🆔 {user.id}\n"
        f"💵 {amount:,} so'm"
    )



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


    for a in admins:
        if a.telegram_id == admin.SUPERADMIN_ID:
            continue  
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


def payment_response(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data.split(":")
    _, action, user_id, *rest = data
    user_id = int(user_id)

    with LocalSession() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if action == "ok":
            amount = int(rest[0])
            user.balance += amount
            session.commit()

            context.bot.send_message(
                chat_id=user_id,
                text=f"✅ Balansingiz {amount:,} so'mga to‘ldirildi"
            )
            safe_edit(query, "✅ To‘lov tasdiqlandi")


        elif action == "custom":
            # 🔑 user_id ni saqlab qo‘yamiz
            context.user_data["custom_user"] = user_id

            safe_edit(
            query,
                "✏️ <b>Real tushgan summani kiriting:</b>"
            )
            return PAYMENT.CUSTOM_AMOUNT

        elif action == "no":
            context.bot.send_message(
                chat_id=user_id,
                text="❌ To‘lov rad etildi"
            )
            query.edit_message_caption("❌ To‘lov rad etildi")
            

def save_custom_amount(update: Update, context: CallbackContext):
    print("🔥 save_custom_amount ishladi")
    if "custom_user" not in context.user_data:
        update.message.reply_text("❌ Xatolik. Qaytadan urinib ko'ring.")
        return ConversationHandler.END

    try:
        amount = int(update.message.text)
    except ValueError:
        update.message.reply_text("❌ Iltimos, faqat raqam kiriting.")
        return PAYMENT.CUSTOM_AMOUNT

    user_id = context.user_data["custom_user"]

    # tasdiqlash tugmasi bilan qayta chiqaramiz
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Tasdiqlash",
                callback_data=f"pay:ok:{user_id}:{amount}"
            ),
            InlineKeyboardButton(
                "❌ Rad etish",
                callback_data=f"pay:no:{user_id}"
            )
        ]
    ]

    update.message.reply_text(
        f"💰 <b>Kiritilgan summa:</b> {amount:,} so'm\n\n"
        "Tasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data.clear()
    return ConversationHandler.END


def safe_edit(query, text, reply_markup=None):
    
    if query.message.text:
        query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        
    else:
        query.edit_message_caption(
            caption=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
