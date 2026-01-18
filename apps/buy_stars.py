from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from database.database import LocalSession
from database.models import User, Admin
from database.models import StarPackage
from database.config import admin

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
        # 👤 User
        db_user = session.query(User).filter_by(
            telegram_id=user.id
        ).first()

        balance = db_user.balance if db_user and db_user.balance else 0

        # ⭐ Stars paketi
        package = session.query(StarPackage).filter_by(
            stars=stars
        ).first()

        if not package:
            query.edit_message_text("❌ Bu stars paketi topilmadi")
            return

        price = package.price

        # 👥 Oddiy adminlar
        admins = session.query(Admin).all()

    # 👤 Userga javob
    query.edit_message_text(
        "✅ Buyurtma adminga yuborildi.\n\n"
        "⏳ Admin tasdiqlashini kuting..."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Tasdiqlash",
                callback_data=f"admin_buy_ok:{user.id}:{stars}:{price}"
            ),
            InlineKeyboardButton(
                "❌ Rad etish",
                callback_data=f"admin_buy_no:{user.id}"
            )
        ]
    ])

    text = (
        "🛒 Yangi Stars buyurtma\n\n"
        f"👤 User: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"💰 Balansi: {balance:,} so'm\n"
        f"⭐ Stars: {stars}\n"
        f"💵 Narx: {price:,} so'm"
    )

    # 👑 SUPER ADMIN
    context.bot.send_message(
        chat_id=admin.SUPERADMIN_ID,
        text=text,
        reply_markup=keyboard
    )

    # 👮 ODDIY ADMINLAR
    for a in admins:
        # super admin qayta yuborilmasin
        if a.telegram_id == admin.SUPERADMIN_ID:
            continue

        context.bot.send_message(
            chat_id=a.telegram_id,
            text=text,
            reply_markup=keyboard
        )


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

    # 🔥 ESKI XABARNI ALMASHTIRAMIZ
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
    query.answer()

    data = query.data.split(":")
    action = data[0]          # admin_buy_ok / admin_buy_no
    user_id = int(data[1])

    with LocalSession() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if not user:
            query.edit_message_text("❌ User topilmadi")
            return

        if action == "admin_buy_ok":
            stars = int(data[2])
            price = int(data[3])

            if user.balance is None:
                user.balance = 0

            if user.balance < price:
                query.edit_message_text("❌ User balansida mablag' yetarli emas")
                return

            # 💰 balansdan yechamiz
            user.balance -= price
            user.stars += stars
            session.commit()

            context.bot.send_message(
                chat_id=user_id,
                text=f"✅ {stars} ⭐ Stars balansingizga qo'shildi!"
            )

            query.edit_message_text("✅ Buyurtma tasdiqlandi")

        else:
            context.bot.send_message(
                chat_id=user_id,
                text="❌ Stars sotib olish rad etildi"
            )
            query.edit_message_text("❌ Buyurtma rad etildi")

def cancel_buy(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # user_data ni tozalaymiz
    context.user_data.pop("stars", None)
    context.user_data.pop("price", None)

    query.edit_message_text(
        "❌ Buyurtma bekor qilindi."
    )