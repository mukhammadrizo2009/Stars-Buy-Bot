from telegram import Update , ReplyKeyboardMarkup , KeyboardButton , InlineKeyboardButton , InlineKeyboardMarkup
from telegram.ext import CallbackContext

def send_menu(update: Update , context: CallbackContext): 
    bot = context.bot
    user = update.effective_user
    
    bot.send_message(
        chat_id = user.id,
        text = "Bosh Sahifa ro'yhati! 📝",
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton("⭐️ Stars olish"), KeyboardButton("Hisobni to'dirish💰")],
                [KeyboardButton("Profilim 👤") , KeyboardButton("Taklif-Mulohazalar-Yordam💡")]
            ],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    
def user_already_register(update: Update , context: CallbackContext):
    bot = context.bot
    user = update.effective_user
    
    bot.send_message(
        chat_id = user.id,
        text = "Siz ro'yhatdan o'tgan ekansiz! 💡\n\n"\
            "📃 Menulardan birini tanlashingiz mumkin! ",
        parse_mode = "markdown",
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton("⭐️ Stars olish"), KeyboardButton("Hisobni to'dirish💰")],
                [KeyboardButton("Profilim 👤") , KeyboardButton("Taklif-Mulohazalar-Yordam💡")]
            ],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )