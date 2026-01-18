from telegram import Update , ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from database.database import LocalSession
from database.models import User
from .menu import send_menu
from .menu import user_already_register
from database.config import register_states

def check_register(update: Update , context: CallbackContext):
    user = update.effective_user
    
    with LocalSession() as session:
        user = session.query(User).filter(User.telegram_id == user.id).first()
        
        if user:
            user_already_register(update , context)
            
        else:
            register_message(update , context)
            
            
def register_message(update: Update, context: CallbackContext):
    bot = context.bot
    user = update.effective_user

    bot.send_message(
        chat_id=user.id,
        text="Ro'yhatdan o'tishga xush kelibsiz! 🎯",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton("📝 Ro'yhatdan o'tishni boshlash..!")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )



def get_name(update: Update, context: CallbackContext):
    bot = context.bot
    user = update.effective_user

    bot.send_message(
        chat_id=user.id,
        text=(
            "Ism va Familiyangizni kiriting 🖊\n\n"
            "Misol: *Abdulla Abdullayev*"
        ),
        parse_mode="markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return register_states.NAME


def set_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text.strip().title()

    update.message.reply_text(
        "Telefon raqamingizni yuboring 📞\n\n"
        "Iltimos!...Quyidagi tugmani bosgan qolda yuboring!🕹",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return register_states.PHONE_NUMBER



def set_phone(update: Update, context: CallbackContext):
    contact = update.message.contact


    if contact.user_id != update.effective_user.id:
        update.message.reply_text(
            "❌ Iltimos, faqat O'Z telefon raqamingizni yuboring.\n\
            Quyidagi tugmani bosgan qolda yuboring!"
        )
        return register_states.PHONE_NUMBER

    context.user_data["phone_number"] = contact.phone_number

    name = context.user_data["name"]
    phone = contact.phone_number

    update.message.reply_text(
        f"🔍 Ma'lumotlarni tekshiring:\n\n"
        f"👤 Ism: *{name}*\n"
        f"📞 Telefon: *{phone}*\n\n"
        "Agar hammasi to'g'ri bo'lsa — Tasdiqlang ✅\n"
        "Agar xato bo'lsa — Tahrirlang ♻️",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Tasdiqlash! ✅"],
                ["Tahrirlash! ♻️"]
            ],
            resize_keyboard=True
        )
    )

    return register_states.CONFIRM





def save_user(update: Update, context: CallbackContext):
    user_tg = update.effective_user
    data = context.user_data

    with LocalSession() as session:
        user = User(
            telegram_id=user_tg.id,
            name=data["name"],
            phone_number=data["phone_number"]
        )
        session.add(user)
        session.commit()

    context.user_data.clear()

    update.message.reply_text(
        "✅ Siz muvaffaqiyatli ro'yhatdan o'tdingiz!",
        reply_markup=ReplyKeyboardRemove()
    )

    send_menu(update, context)