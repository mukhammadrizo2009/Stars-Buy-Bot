from database.config import config, register_states, topup_states, ADMIN_ADD, STAR
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
    )
from database.database import Base, engine
from apps.start import start
from apps.register import check_register, get_name, set_name, set_phone, save_user
from apps.profile import profile
from apps.menu import send_menu
from apps.send_idea import send_idea
from apps.buy_stars import buy_stars_callback, buy_stars, confirm_buy, admin_buy_decision, cancel_buy
from apps.balance import increase_balance, get_amount, get_check, cancel_topup
from apps.price_stars import seed_star_packages
from admin.admin_panel import admin_panel, admin_menu_callback, save_star_price, admin_stars, edit_star_price, start_remove_admin, admin_admins, start_add_admin, delete_admin, save_admin
from admin.payments import payment_decision

#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

#print("✅ Database tozalandi va qayta yaratildi")

def main() -> None:
    updater = Updater(config.BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    #seed_star_packages()
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('admin', admin_panel))
    
    #Message Handler
    dispatcher.add_handler(MessageHandler(Filters.text("Shaxsingizni tasdiqlang! 🪪"), check_register))
    dispatcher.add_handler(MessageHandler(Filters.text("Ro'yhatdan o'tganman!✅"), check_register))
    
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
    dispatcher.add_handler(register_conversation_handler)
    
    dispatcher.add_handler(MessageHandler(Filters.text("Profilim 👤"), profile))
    dispatcher.add_handler(MessageHandler(Filters.text("Menularga qaytish! ↩️"), send_menu))
    dispatcher.add_handler(MessageHandler(Filters.text("Taklif-Mulohazalar-Yordam💡"), send_idea))
    dispatcher.add_handler(MessageHandler(Filters.text("⭐️ Stars olish"), buy_stars))
    dispatcher.add_handler(CallbackQueryHandler(buy_stars_callback,pattern="^buy_stars:"))

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

    dispatcher.add_handler(topup_handler)
    
    
    dispatcher.add_handler(CallbackQueryHandler(payment_decision,pattern=r"^pay:"))

    dispatcher.add_handler(MessageHandler(Filters.text("Ha ✅"), confirm_buy))
    dispatcher.add_handler(MessageHandler(Filters.text("Yo'q ❌"), confirm_buy))
    
    dispatcher.add_handler(CallbackQueryHandler(send_menu, pattern="^menu$"))
    
    dispatcher.add_handler(CallbackQueryHandler(confirm_buy, pattern="^confirm_buy:"))
    dispatcher.add_handler(CallbackQueryHandler(cancel_buy, pattern="^cancel_buy$"))

    dispatcher.add_handler(CallbackQueryHandler(admin_buy_decision, pattern="^admin_buy_"))
    
    dispatcher.add_handler(CallbackQueryHandler(admin_stars, pattern="^admin:stars$"))
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

    dispatcher.add_handler(star_price_conv)

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
    dispatcher.add_handler(admin_conv)
    dispatcher.add_handler(
    CallbackQueryHandler(admin_admins, pattern="^admin:admins$")
    )
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin:"))



    updater.start_polling()
    updater.idle()
    
if __name__ == "__main__":
    main()