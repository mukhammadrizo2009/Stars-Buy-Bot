from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from database.database import LocalSession
from database.models import User, Admin, StarsOrder
from database.models import StarPackage
from database.config import admin, PAYMENT

def buy_stars(update: Update, context: CallbackContext):
    keyboard = []

    with LocalSession() as session:
        packages = session.query(StarPackage).order_by(StarPackage.stars).all()

    for pkg in packages:
        keyboard.append(
            [
            InlineKeyboardButton(
                text=f"⭐ {pkg.stars} Stars | 💵 {pkg.price:,} so'm",
                callback_data=f"buy_stars:{pkg.stars}"
            )
            ]
            )
    update.message.reply_text(
        "⭐ Stars paketni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def confirm_buy(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user = query.from_user
    stars = int(query.data.split(":")[1])

    with LocalSession() as session:
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        package = session.query(StarPackage).filter_by(stars=stars).first()
        
        if not package:
            query.edit_message_text("❌ Paket topilmadi")
            return

        # 1. Bazada yangi buyurtma yaratamiz
        new_order = StarsOrder(
            user_id=user.id,
            stars=stars,
            price=package.price,
            status="pending",
            admin_messages={}
        )
        session.add(new_order)
        session.flush() # ID olish uchun
        order_id = new_order.id

        # 2. Adminlar ro'yxati
        admins = session.query(Admin).all()
        admin_ids = [a.telegram_id for a in admins]
        if admin.SUPERADMIN_ID not in admin_ids:
            admin_ids.append(admin.SUPERADMIN_ID)

        # 3. Tugmalar (Callback data ichiga order_id qo'shamiz)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"admin_buy_ok:{order_id}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"admin_buy_no:{order_id}")
            ]
        ])

        text = (
            "🛒 Yangi Stars buyurtma\n\n"
            f"👤 User: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"💰 Balansi: {db_user.balance:,} so'm\n"
            f"⭐ Stars: {stars}\n"
            f"💵 Narx: {package.price:,} so'm"
        )

        # 4. Xabarlarni yuborish va ID-larni yig'ish
        sent_messages = {}
        for admin_id in admin_ids:
            try:
                msg = context.bot.send_message(chat_id=admin_id, text=text, reply_markup=keyboard)
                sent_messages[str(admin_id)] = msg.message_id
            except: continue

        # 5. ID-larni saqlaymiz
        new_order.admin_messages = sent_messages
        session.commit()

    query.edit_message_text("✅ Buyurtma adminga yuborildi. Kuting...")


def buy_stars_callback(update: Update, context: CallbackContext):
    
    query = update.callback_query
    query.answer()

    user = query.from_user
    stars = int(query.data.split(":")[1])

    with LocalSession() as session:
        package = session.query(StarPackage).filter_by(stars=stars).first()
        if not package:
            query.edit_message_text("❌ Bu stars paketi mavjud emas")
            return

        price = package.price

        db_user = session.query(User).filter_by(
            telegram_id=user.id
        ).first()
        balance = db_user.balance if db_user else 0

    
    query.edit_message_text(
        text=(
            "🧾 Buyurtma:\n"
            f"⭐ Stars: {stars}\n"
            f"💵 Narxi: {price:,} so'm\n"
            f"💰 Balansingiz: {balance:,} so'm\n\n"
            "Tasdiqlaysizmi?"
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Ha ✅",
                    callback_data=f"confirm_buy:{stars}"
                ),
                InlineKeyboardButton(
                    "Yo'q ❌",
                    callback_data="cancel_buy"
                )
            ]
        ])
    )


def admin_buy_decision(update: Update, context: CallbackContext):
    query = update.callback_query
    admin_user = update.effective_user
    
    data = query.data.split(":")
    action = data[0]          
    order_id = int(data[1])

    with LocalSession() as session:
        # 1. Buyurtmani olish
        order = session.query(StarsOrder).filter_by(id=order_id).first()

        if not order:
            query.answer("❌ Buyurtma topilmadi!", show_alert=True)
            return

        # 2. ENG ASOSIYSI: Statusni tekshirish
        if order.status != "pending":
            query.answer("⚠️ Bu buyurtma allaqachon ko'rib chiqilgan!", show_alert=True)
            try: query.edit_message_reply_markup(reply_markup=None)
            except: pass
            return

        user = session.query(User).filter_by(telegram_id=order.user_id).first()
        status_text = ""

        if action == "admin_buy_ok":
            if user.balance < order.price:
                query.answer("❌ User balansida mablag' yetarli emas", show_alert=True)
                return

            # Hisob-kitob
            user.balance -= order.price
            user.stars += order.stars
            order.status = "approved"
            session.commit()

            context.bot.send_message(
                chat_id=user.telegram_id,
                text=f"✅ {order.stars} ⭐ Stars balansingizga qo'shildi!"
            )
            status_text = f"✅ Tasdiqlandi (Admin: {admin_user.full_name})"
            query.answer("Tasdiqlandi")

        elif action == "admin_buy_no":
            order.status = "rejected"
            session.commit()


            context.bot.send_message(
                chat_id=user.telegram_id,
                text="❌ Stars sotib olish rad etildi"
            )
            status_text = f"❌ Rad etildi (Admin: {admin_user.full_name})"
            query.answer("Rad etildi")

        # 3. Barcha adminlarda xabarni yangilash
        if status_text:
            admin_msgs = order.admin_messages or {}
            for admin_id, msg_id in admin_msgs.items():
                try:
                    context.bot.edit_message_text(
                        chat_id=int(admin_id),
                        message_id=int(msg_id),
                        text=query.message.text + f"\n\n=== {status_text} ===",
                        reply_markup=None
                    )
                except: continue

def cancel_buy(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

 
    context.user_data.pop("stars", None)
    context.user_data.pop("price", None)

    query.edit_message_text(
        "❌ Buyurtma bekor qilindi."
    )