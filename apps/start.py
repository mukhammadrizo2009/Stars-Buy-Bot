from telegram import (Update, ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext):
    bot = context.bot
    user = update.effective_user
    
    bot.send_message(
        chat_id = user.id,
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