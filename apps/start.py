from telegram import (Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import CallbackContext
from database.config import CHANNEL_ID, CHANNEL_LINK

def is_subscribed(bot, user_id):
    """Foydalanuvchi kanalga a'zo ekanligini tekshirish"""
    try:
        # Bot kanalda ADMIN bo'lishi shart!
        member = bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Status 'left' yoki 'kicked' bo'lmasa, demak u kanalda bor
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Xatolik: {e}") # Konsolda xatoni ko'rish uchun
        return False

def start(update: Update, context: CallbackContext):
    
    user = update.effective_user
    
    # Obunani tekshiramiz
    if is_subscribed(context.bot, user.id):
        # Agar obuna bo'lgan bo'lsa
        update.message.reply_text(
            text = "✋Assalomu Alaykum!\n\n"
            "⭐️ Starts sotib olish uchun, bir martalik ro'yhatdan o'ting!🧾",
            parse_mode = "markdown",
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton("Shaxsingizni tasdiqlang! 🪪"), KeyboardButton("Ro'yhatdan o'tganman!✅")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
    else:
        # Agar obuna bo'lmagan bo'lsa
        keyboard = [
            [InlineKeyboardButton("Kanalga obuna bo'lish 📢", url=CHANNEL_LINK)],
            [InlineKeyboardButton("Tekshirish ✅", callback_data="check_subscription")]
        ]
        update.message.reply_text(
            text="❌ **Botdan foydalanish uchun kanalimizga obuna bo'lishingiz kerak!**\n\n"
                 "Iltimos, avval kanalga a'zo bo'lib, keyin 'Tekshirish' tugmasini bosing.",
            parse_mode="markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def check_callback(update: Update, context: CallbackContext):
    """Tekshirish tugmasi bosilganda ishlaydi"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if is_subscribed(context.bot, user_id):
        query.answer("Rahmat! Obuna tasdiqlandi. ✅", show_alert=True)
        query.message.delete() # Eski xabarni o'chirish
        
        # Foydalanuvchiga menyuni ko'rsatish (start funksiyasini qo'lda chaqiramiz)
        # CallbackUpdate'da message yo'qligi sababli start'ni biroz o'zgartirib chaqiramiz:
        context.bot.send_message(
            chat_id=user_id,
            text="✅ Obuna tasdiqlandi! Endi botdan foydalanishingiz mumkin.\n"
                 "Botni boshlash uchun /start buyrug'ini bosing yoki pastdagi tugmalardan foydalaning.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton("Shaxsingizni tasdiqlang! 🪪"), KeyboardButton("Ro'yhatdan o'tganman!✅")]
                ],
                resize_keyboard=True
            )
        )
    else:
        query.answer("Siz hali ham kanalga a'zo emassiz! ⚠️\nIltimos, obuna bo'ling.", show_alert=True)