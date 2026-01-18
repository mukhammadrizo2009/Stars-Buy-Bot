from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import CallbackContext
from database.models import StarPackage
from database.database import LocalSession


def seed_star_packages():
    
    packages = [
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

    with LocalSession() as session:
        for stars, price in packages:
            exists = session.query(StarPackage).filter_by(stars=stars).first()
            if not exists:
                session.add(StarPackage(stars=stars, price=price))
        session.commit()
        print("✅ Stars paketlar bazaga yozildi")


def buy_stars(update: Update, context: CallbackContext):
    keyboard = []

    with LocalSession() as session:
        packages = session.query(StarPackage).order_by(StarPackage.stars).all()

    for pkg in packages:
        keyboard.append([
            InlineKeyboardButton(
                text=f"⭐ {pkg.stars} Stars | 💵 {pkg.price:,} so'm",
                callback_data=f"buy_stars:{pkg.stars}"
            )
        ])

    update.message.reply_text(
        "⭐ Stars paketni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
