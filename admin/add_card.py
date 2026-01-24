from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from database.database import LocalSession
from database.models import PaymentCard
from database.config import CARD

from .admin_panel import is_superadmin, admin_cards

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

def delete_card_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id

    if not is_superadmin(user_id):
        query.answer("⛔ Bu amalga ruxsat yo'q!", show_alert=True)
        return

    # callback_data dan ID ni ajratib olamiz (card:del:5 -> 5)
    card_id = int(query.data.split(":")[2])

    with LocalSession() as session:
        card = session.query(PaymentCard).filter(PaymentCard.id == card_id).first()
        if card:
            session.delete(card)
            session.commit()
            query.answer("✅ Karta muvaffaqiyatli o'chirildi", show_alert=True)
        else:
            query.answer("❌ Karta topilmadi yoki allaqachon o'chirilgan", show_alert=True)

    # Kartalar ro'yxatini yangilash uchun yana asosiy funksiyani chaqiramiz
    return admin_cards(update, context)