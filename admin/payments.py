from sqlalchemy import select
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from database.config import admin, PAYMENT
from database.database import LocalSession
from database.models import User, Admin, Payment


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def send_payment_to_admin(update: Update, context: CallbackContext, *, bot, user, amount, file_id, is_photo=True):
    
    bot = context.bot
    user = update.effective_user
    
    with LocalSession() as session:
        # 1. Avval bazada to'lov so'rovini yaratamiz
        new_payment = Payment(
            user_id=user.id,
            amount=amount,
            status="pending",
            admin_messages={} # Hozircha bo'sh
        )
        session.add(new_payment)
        session.flush() # ID olish uchun flush qilamiz
        payment_id = new_payment.id

        # 2. Adminlar ro'yxatini olish
        admins = session.query(Admin).all()
        admin_ids = [a.telegram_id for a in admins]
        if admin.SUPERADMIN_ID not in admin_ids:
            admin_ids.append(admin.SUPERADMIN_ID)

        # 3. Tugmalar (Callback data ichida payment_id ketadi)
        keyboard = [
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"pay:ok:{payment_id}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"pay:no:{payment_id}")
            ],
            [
                InlineKeyboardButton("✏️ Boshqa summa", callback_data=f"pay:custom:{payment_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        caption = (
            "💰 Balans to'ldirish so'rovi\n\n"
            f"👤 Foydalanuvchi: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"💵 Summa: {amount:,} so'm"
        )

        # 4. Xabarlarni yuborish va ID-larni saqlash
        sent_messages = {} # {admin_id: message_id}
        
        for admin_id in admin_ids:
            try:
                if is_photo:
                    msg = bot.send_photo(chat_id=admin_id, photo=file_id, caption=caption, reply_markup=reply_markup)
                else:
                    msg = bot.send_document(chat_id=admin_id, document=file_id, caption=caption, reply_markup=reply_markup)
                
                sent_messages[str(admin_id)] = msg.message_id
            except Exception as e:
                print(f"Admin {admin_id} ga yuborishda xato: {e}")

        # 5. Xabar ID-larini bazaga saqlaym3
        new_payment.admin_messages = sent_messages
        session.commit()

def payment_response(update: Update, context: CallbackContext):
    query = update.callback_query
    admin_user = update.effective_user
    
    # Data format: "pay:action:payment_id"
    data = query.data.split(":")
    action = data[1]
    payment_id = int(data[2])

    with LocalSession() as session:
        payment = session.query(Payment).filter_by(id=payment_id).first()

        if not payment:
            query.answer("❌ To'lov ma'lumotlari topilmadi!", show_alert=True)
            return

        # 1. Tekshirilganlik holatini ko'rish
        if payment.status != "pending":
            query.answer("⚠️ Bu so'rov allaqachon ko'rib chiqilgan!", show_alert=True)
            # Admin ekranini tozalash (agar yangilanmagan bo'lsa)
            try:
                query.edit_message_reply_markup(reply_markup=None)
            except: pass
            return

        user_in_db = session.query(User).filter_by(telegram_id=payment.user_id).first()

        # 2. Amallar
        status_text = ""
        if action == "ok":
            payment.status = "approved"
            user_in_db.balance += payment.amount
            session.commit()
            
            context.bot.send_message(
                chat_id=payment.user_id,
                text=f"✅ To‘lovingiz tasdiqlandi. Balansingizga {payment.amount:,} so'm qo'shildi."
            )
            status_text = f"✅ Tasdiqlandi (Admin: {admin_user.full_name})"
            query.answer("Muvaffaqiyatli tasdiqlandi")

        elif action == "no":
            payment.status = "rejected"
            session.commit()
            
            context.bot.send_message(
                chat_id=payment.user_id,
                text="❌ To‘lovingiz rad etildi."
            )
            status_text = f"❌ Rad etildi (Admin: {admin_user.full_name})"
            query.answer("To'lov rad etildi")

        elif action == "custom":
            context.user_data["pending_payment_id"] = payment_id
            query.message.reply_text(f"✏️ {payment.user_id} uchun tushgan aniq summani yozing:")
            query.answer()
            return PAYMENT.CUSTOM_AMOUNT

        # 3. BARCHA ADMINLARDAGI XABARLARNI YANGILASH
        if status_text:
            messages_data = payment.admin_messages or {}
            for admin_id, msg_id in messages_data.items():
                try:
                    context.bot.edit_message_caption(
                        chat_id=int(admin_id),
                        message_id=int(msg_id),
                        caption=query.message.caption + f"\n\n=== {status_text} ===",
                        reply_markup=None # Tugmalarni o'chirish
                    )
                except Exception as e:
                    print(f"Update error for admin {admin_id}: {e}")
            

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
