from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database.config import topup_states, admin
from admin.payments import send_payment_to_admin
ADMIN_ID = admin.ADMIN


def increase_balance(update: Update, context: CallbackContext):
    update.message.reply_text(
        "💳 <b>To'lov uchun karta raqamlari</b>\n\n"
        "🔹 <code>4439 2000 2691 5271</code> (Visa)\n"
        "🔹 <code>4439 2000 2725 5040</code> (Visa)\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💵 <b>To'lov miqdorini kiriting</b>\n\n"
        "📌 Minimal summa: <b>10 000 so'm</b>\n"
        "✏️ Misol: <i>50000</i>",
        parse_mode="HTML"
    )
    return topup_states.AMOUNT


def get_amount(update: Update, context: CallbackContext):
    text_amount = update.message.text.replace(" ", "")

    if not text_amount.isdigit():
        update.message.reply_text("❌ Iltimos, faqat raqam kiriting!")
        return topup_states.AMOUNT

    amount = int(text_amount)

    if amount < 10000:
        update.message.reply_text("❌ Minimal summa 10 000 so'm")
        return topup_states.AMOUNT

    context.user_data["topup_amount"] = amount

    update.message.reply_text(
        "📸 Endi to'lov chekini yuboring (rasm yoki файл)"
    )
    return topup_states.CHECK


def get_check(update: Update, context: CallbackContext):
    user = update.effective_user
    amount = context.user_data.get("topup_amount")

    if not amount:
        update.message.reply_text("❌ Xatolik. Qayta urinib ko'ring.")
        return ConversationHandler.END

    # 📸 Rasm yoki файлni tekshiramiz
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        is_photo = True
    elif update.message.document:
        file_id = update.message.document.file_id
        is_photo = False
    else:
        update.message.reply_text(
            "❌ Iltimos chekni rasm yoki файл ko'rinishida yuboring"
        )
        return topup_states.CHECK

    # 👑 ADMINga yuboramiz
    send_payment_to_admin(
        update=update,
        context=context,
        bot=context.bot,
        user=user,
        amount=amount,
        file_id=file_id,
        is_photo=is_photo
    )

    # 👤 USERga javob
    keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📞 Admin bilan bog‘lanish", url="https://t.me/mirzayeoff")
    ]
    ])
    update.message.reply_text(
    "✅ <b>To'lov qabul qilindi.</b>\n\n"
    "⏳ Admin tekshiruvdan so'ng balansingiz to'ldiriladi.",
    reply_markup=keyboard,
    parse_mode="HTML"
)

    context.user_data.clear()
    return ConversationHandler.END
