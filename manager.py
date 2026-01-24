from telegram.ext import ( Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler)

from database.database import Base, engine
from database.config import config

from apps.start import start
from apps.register import check_register
from apps.profile import profile
from apps.menu import send_menu
from apps.send_idea import send_idea
from apps.buy_stars import buy_stars_callback, buy_stars, confirm_buy, admin_buy_decision, cancel_buy

from apps.price_stars import seed_star_packages

from admin.admin_panel import admin_panel, admin_menu_callback, admin_stars, admin_admins, admin_cards
from admin.payments import payment_response

from apps.conversation import Register, Topup, Star_Price, Admin, Payment, Card

#Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)

#print("✅ Database tozalandi va qayta yaratildi")

def main() -> None:
    
    
    updater = Updater(config.BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    #seed_star_packages()
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('admin', admin_panel))

    dispatcher.add_handler(MessageHandler(Filters.text("Shaxsingizni tasdiqlang! 🪪"), check_register))
    dispatcher.add_handler(MessageHandler(Filters.text("Ro'yhatdan o'tganman!✅"), check_register))

    dispatcher.add_handler(Register.register_conversation_handler)
    
    dispatcher.add_handler(Payment.payment_conv)
    
    dispatcher.add_handler(Topup.topup_handler)
    
    dispatcher.add_handler(Star_Price.star_price_conv)
    
    dispatcher.add_handler(Admin.admin_conv)
    
    dispatcher.add_handler(Card.card_conv)
    
    dispatcher.add_handler(MessageHandler(Filters.text("Profilim 👤"), profile))
    
    dispatcher.add_handler(MessageHandler(Filters.text("Menularga qaytish! ↩️"), send_menu))
    
    dispatcher.add_handler(MessageHandler(Filters.text("Taklif-Mulohazalar-Yordam💡"), send_idea))
    
    dispatcher.add_handler(MessageHandler(Filters.text("⭐️ Stars olish"), buy_stars))
    
    dispatcher.add_handler(CallbackQueryHandler(buy_stars_callback,pattern="^buy_stars:"))
    
    dispatcher.add_handler(CallbackQueryHandler(send_menu, pattern="^menu$"))
    
    dispatcher.add_handler(CallbackQueryHandler(confirm_buy, pattern="^confirm_buy:"))
    
    dispatcher.add_handler(CallbackQueryHandler(cancel_buy, pattern="^cancel_buy$"))

    dispatcher.add_handler(CallbackQueryHandler(admin_buy_decision, pattern="^admin_buy_"))
    
    dispatcher.add_handler(CallbackQueryHandler(admin_stars, pattern="^admin:stars$"))
    
    dispatcher.add_handler(CallbackQueryHandler(admin_admins, pattern="^admin:admins$"))
    
    dispatcher.add_handler(CallbackQueryHandler(payment_response, pattern="^pay:(ok|no):"))
    
    dispatcher.add_handler(CallbackQueryHandler(admin_menu_callback, pattern=r"^admin:"))

    dispatcher.add_handler(CallbackQueryHandler(admin_cards, pattern="^admin:cards$"))

    updater.start_polling()
    updater.idle()
    
if __name__ == "__main__":
    main()