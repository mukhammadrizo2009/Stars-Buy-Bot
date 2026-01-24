from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from database.database import LocalSession
from database.models import PaymentCard
from database.config import CARD

def start_add_card(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        "💳 <b>Karta raqamini kiriting:</b>",
        parse_mode="HTML"
    )
    return CARD.NUMBER

def save_card_number(update: Update, context: CallbackContext):
    context.user_data["card_number"] = update.message.text
    update.message.reply_text("💳 Karta turi? (Visa / MasterCard / Uzcard)")
    return CARD.TYPE

def save_card_type(update: Update, context: CallbackContext):
    card_type = update.message.text
    card_number = context.user_data["card_number"]

    with LocalSession() as session:
        session.add(PaymentCard(
            card_number=card_number,
            card_type=card_type
        ))
        session.commit()

    update.message.reply_text("✅ Karta muvaffaqiyatli qo'shildi")
    context.user_data.clear()
    return ConversationHandler.END
