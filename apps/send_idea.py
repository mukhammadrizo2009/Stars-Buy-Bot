from telegram import (Update, ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import CallbackContext

def send_idea(update: Update, context: CallbackContext):
    bot = context.bot
    user = update.effective_user
    
    bot.send_message(
        chat_id = user.id,
        text = "🧾Taklif va Mulohazalaringizni bu yerga yozib qoldirishingiz mumkin!😇\n\n"
        "Username: @mirzayeoff",
        parse_mode = "markdown",
        reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton("Menularga qaytish! ↩️")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            ))