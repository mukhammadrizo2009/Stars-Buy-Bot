from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from database.database import LocalSession
from database.models import User

STARS_PACKAGES = [
    (50, 10000),
    (75, 15000),
    (100, 20000),
    (150, 30000),
    (200, 40000),
    (250, 50000),
    (300, 60000),
    (400, 80000),
    (500, 100000),
    (600, 120000),
    (700, 140000),
    (800, 160000),
    (900, 180000),
    (1000, 200000),
]

def buy_stars(update: Update, context: CallbackContext):
    keyboard = []

    for stars, price in STARS_PACKAGES:
        keyboard.append([
            InlineKeyboardButton(
                text=f"⭐ {stars} Stars | 💵 {price:,} so'm",
                callback_data=f"buy_stars:{stars}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "⭐ Sotib olmoqchi bo'lgan stars miqdorini tanlang:",
        reply_markup=reply_markup
    )
    
def confirm_buy(update: Update, context: CallbackContext):
    text = update.message.text
    tg_user = update.effective_user

    if text == "Yo'q ❌":
        update.message.reply_text(
            "❌ Buyurtma bekor qilindi",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return

    stars = context.user_data.get("stars")
    price = context.user_data.get("price")

    with LocalSession() as session:
        user = session.query(User).filter_by(telegram_id=tg_user.id).first()

        if user.balance < price:
            update.message.reply_text(
                "❌ Balansingiz yetarli emas.\n💳 Balans to'ldiring.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=
                    [
                        KeyboardButton("Hisobni to'dirish💰"), KeyboardButton("Menularga qaytish! ↩️")
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True
                    ),
            )
            return

        user.balance -= price
        user.stars += stars
        session.commit()
        
    keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Menularga qaytish! ↩️", callback_data="menu")
    ]
])

    update.message.reply_text(
        f"✅ Xarid muvaffaqiyatli!\n\n Admin tasdiqidan so'ng ⭐ {stars} Stars qo'shiladi",
        reply_markup=keyboard
    )

    context.user_data.clear()

    
    
def buy_stars_callback(update: Update, context: CallbackContext):
    bot = context.bot
    user = update.effective_user

    query = update.callback_query
    query.answer()

    data = query.data  # buy_stars:100
    stars = int(data.split(":")[1])
    price = dict(STARS_PACKAGES)[stars]

    # 🔴 MUHIM: user_data ga saqlaymiz
    context.user_data["stars"] = stars
    context.user_data["price"] = price

    bot.send_message(
        chat_id=user.id,
        text=(
            f"🧾 Buyurtma:\n"
            f"⭐ Stars: {stars}\n"
            f"💵 Narxi: {price:,} so'm\n\n"
            "Tasdiqlaysizmi?"
        ),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("Ha ✅"), KeyboardButton("Yo'q ❌")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
