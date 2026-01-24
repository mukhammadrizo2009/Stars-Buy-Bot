from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from database.config import register_states, topup_states, STAR, ADMIN_ADD, PAYMENT, CARD

from apps.register import get_name, set_name, set_phone, save_user
from apps.balance import increase_balance, get_amount, get_check, cancel_topup

from admin.admin_panel import save_star_price, edit_star_price, start_remove_admin, start_add_admin, delete_admin, save_admin
from admin.add_card import save_card_number, save_card_type, start_add_card
from admin.payments import payment_response, save_custom_amount

class Register():
    register_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text("📝 Ro'yhatdan o'tishni boshlash..!") , get_name)],
    states={
        register_states.NAME: [MessageHandler(Filters.text, set_name)],
        register_states.PHONE_NUMBER: [MessageHandler(Filters.contact, set_phone)],
        
        register_states.CONFIRM: [
            MessageHandler(Filters.regex("^Tasdiqlash! ✅$"), save_user),
            MessageHandler(Filters.regex("^Tahrirlash! ♻️$"), get_name),
        ]
    },
    fallbacks = []
    )
    
class Topup():
    topup_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex("^Hisobni to'dirish💰$"), increase_balance)
    ],
    states={
        topup_states.AMOUNT: [
            MessageHandler(Filters.text & ~Filters.command, get_amount)
        ],
        topup_states.CHECK: [
            MessageHandler(Filters.photo | Filters.document, get_check)
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_topup)
    ]
    )
    
class Star_Price():
    star_price_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(edit_star_price, pattern="^edit_star:")
    ],
    states={
        STAR.STAR_EDIT: [
            MessageHandler(Filters.text & Filters.regex("^[0-9]+$"), save_star_price)
        ]
    },
    fallbacks=[],
    per_message=False
)
    
class Admin():
    admin_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_add_admin, pattern="^admin:add$"),
        CallbackQueryHandler(start_remove_admin, pattern="^admin:remove$")
    ],
    states={
        ADMIN_ADD.ADD: [
            MessageHandler(Filters.text & ~Filters.command, save_admin)
        ],
        ADMIN_ADD.REMOVE: [
            MessageHandler(Filters.text & ~Filters.command, delete_admin)
        ],
    },
    fallbacks=[],
    per_message=False
    )

class Payment():
    payment_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(payment_response, pattern="^pay:custom:")
        ],
        states={
            PAYMENT.CUSTOM_AMOUNT: [
                MessageHandler(Filters.text & Filters.regex("^[0-9]+$"), save_custom_amount)
            ]
        },
        fallbacks=[],
        per_message=False
        )

class Card():
    card_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_card, pattern="^card:add$")],
        states={
            CARD.NUMBER: [MessageHandler(Filters.text, save_card_number)],
            CARD.TYPE: [MessageHandler(Filters.text, save_card_type)],
        },
        fallbacks=[]
    )