from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler

from database.models import StarPackage, Admin, PaymentCard
from database.database import LocalSession
from database.config import admin, ADMIN_ADD, STAR
from admin.users import admin_users



def is_admin(user_id: int) -> bool:

    if user_id == admin.SUPERADMIN_ID:
        return True


    with LocalSession() as session:
        return session.query(Admin).filter_by(
            telegram_id=user_id
        ).first() is not None




def is_superadmin(user_id: int) -> bool:
    return user_id == admin.SUPERADMIN_ID


def admin_panel(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        update.message.reply_text("⛔ Siz admin emassiz")
        return
       
    update.message.reply_text("👑 Admin panelga xush kelibsiz") 

    keyboard = [
        [InlineKeyboardButton("👥 Adminlar", callback_data="admin:admins")],
        
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin:users")],
        
        [InlineKeyboardButton("⭐ Stars narxlari", callback_data="admin:stars")],
        
        [InlineKeyboardButton("💳 To'lov kartalari", callback_data="admin:cards")],
    ]

    update.message.reply_text(
        "🛡 ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



def admin_menu_callback(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    query = update.callback_query
    query.answer()
    
    if not is_admin(user_id):
        update.message.reply_text("⛔ Siz admin emassiz")
        return
    
    elif query.data == "admin:admins":
        admin_admins(update, context)

    elif query.data == "admin:users":
        admin_users(update, context)
        
    elif query.data == "admin:stars":
        admin_stars(update, context)
        
    elif query.data == "admin:cards":
        admin_cards(update, context)
         
def admin_stars(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        update.message.reply_text("⛔ Siz admin emassiz")
        return

    query = update.callback_query
    query.answer()

    with LocalSession() as session:
        packages = session.query(StarPackage).all()

    text = "⭐ Stars paketlar:\n\n"
    keyboard = []

    for pkg in packages:
        text += f"⭐ {pkg.stars} → 💵 {pkg.price:,} so'm\n"


        if is_superadmin(user_id):
            keyboard.append([
                InlineKeyboardButton(
                    f"✏️ {pkg.stars} Stars",
                    callback_data=f"edit_star:{pkg.stars}"
                )
            ])

    query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )


def edit_star_price(update: Update, context: CallbackContext):
    
    user_id = update.effective_user.id
    
    query = update.callback_query
    query.answer()

    if not is_superadmin(user_id):
        query.message.reply_text(
            "⛔ Stars narxini faqat SUPER ADMIN o‘zgartira oladi"
        )
        return ConversationHandler.END

    stars = int(query.data.split(":")[1])
    context.user_data["edit_star"] = stars
    

    query.edit_message_text(
        f"💵 <b>{stars} Stars</b> uchun yangi narxni kiriting:",
        parse_mode="HTML"
    )

    return STAR.STAR_EDIT



def save_star_price(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not is_superadmin(user_id):
        update.message.reply_text(
            "⛔ Stars narxini faqat SUPER ADMIN o'zgartira oladi"
        )
        return ConversationHandler.END

    if "edit_star" not in context.user_data:
        update.message.reply_text("❌ Xatolik. Qaytadan urinib ko'ring.")
        return ConversationHandler.END

    price = int(update.message.text)
    stars = context.user_data["edit_star"]

    with LocalSession() as session:
        pkg = session.query(StarPackage).filter_by(stars=stars).first()
        pkg.price = price
        session.commit()

    update.message.reply_text(
        f"✅ {stars} Stars narxi yangilandi: {price:,} so'm"
    )

    context.user_data.clear()
    return ConversationHandler.END



def admin_admins(update: Update, context: CallbackContext):
    
    user_id = update.effective_user.id

    if not is_admin(user_id):
        update.message.reply_text("⛔ Siz admin emassiz")
        return

    query = update.callback_query
    query.answer()

    with LocalSession() as session:
        admins = session.query(Admin).all()

    text = "👥 Adminlar ro'yxati:\n\n"
    for a in admins:
        text += f"🆔 {a.telegram_id}\n"

    keyboard = []
    if is_superadmin(user_id):
        keyboard = [
            [InlineKeyboardButton("➕ Admin qo'shish", callback_data="admin:add")],
            [InlineKeyboardButton("➖ Admin o'chirish", callback_data="admin:remove")]
        ]

    query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )


def start_add_admin(update: Update, context: CallbackContext):
    
    user_id = update.effective_user.id

    if not is_superadmin(user_id):
        update.callback_query.answer(
            "⛔ Faqat Super Admin admin qo'sha oladi",
            show_alert=True
        )
        return ConversationHandler.END

    query = update.callback_query
    query.answer()


    query.edit_message_text(
        "🆔 <b>Admin qilinadigan foydalanuvchi ID sini yuboring:</b>",
        parse_mode="HTML"
    )

    return ADMIN_ADD.ADD


def save_admin(update: Update, context: CallbackContext):
    
    user_id = update.effective_user.id

    if not is_admin(user_id):
        update.message.reply_text("⛔ Siz admin emassiz")
        return
    
    admin_id = int(update.message.text)

    with LocalSession() as session:
        if session.query(Admin).filter_by(telegram_id=admin_id).first():
            update.message.reply_text("⚠️ Bu foydalanuvchi allaqachon admin")
            return ConversationHandler.END

        session.add(Admin(telegram_id=admin_id))
        session.commit()

    update.message.reply_text("✅ Admin muvaffaqiyatli qo'shildi")
    return ConversationHandler.END

def start_remove_admin(update: Update, context: CallbackContext):
    
    user_id = update.effective_user.id

    if not is_superadmin(user_id):
        update.callback_query.answer(
            "⛔ Faqat Super Admin admin o'chira oladi",
            show_alert=True
        )
        return ConversationHandler.END

    query = update.callback_query
    query.answer()


    query.edit_message_text(
        "🆔 <b>O‘chiriladigan admin ID sini yuboring:</b>",
        parse_mode="HTML"
    )

    return ADMIN_ADD.REMOVE



def delete_admin(update: Update, context: CallbackContext):
    
    user_id = update.effective_user.id

    if not is_admin(user_id):
        update.message.reply_text("⛔ Siz admin emassiz")
        return
    
    admin_id = int(update.message.text)

    with LocalSession() as session:
        admin = session.query(Admin).filter_by(
            telegram_id=admin_id
        ).first()

        if not admin:
            update.message.reply_text("❌ Bunday admin yo'q")
            return ConversationHandler.END

        session.delete(admin)
        session.commit()

    update.message.reply_text("✅ Admin o'chirildi")
    return ConversationHandler.END


def admin_cards(update: Update, context: CallbackContext):
    
    user_id = update.effective_user.id
    query = update.callback_query
    
    # Foydalanuvchi superadminmi yoki yo'qligini tekshiramiz
    is_super = is_superadmin(user_id)
    
    # Agar foydalanuvchi umuman admin bo'lmasa (ixtiyoriy tekshiruv)
    # if not is_admin(user_id): 
    #     query.answer("Ruxsat berilmagan", show_alert=True)
    #     return

    if query:
        query.answer()

    with LocalSession() as session:
        cards = session.query(PaymentCard).all()

    text = "💳 <b>To‘lov kartalari</b>\n\n"
    keyboard = []

    if not cards:
        text += "Hozircha kartalar qo'shilmagan."
    else:
        for i, c in enumerate(cards, start=1):
            text += f"{i}. <code>{c.card_number}</code> ({c.card_type})\n"
            
            # FAQAT Super Admin uchun o'chirish tugmasini chiqaramiz
            if is_super:
                keyboard.append([
                    InlineKeyboardButton(f"❌ {i}-kartani o'chirish", callback_data=f"card:del:{c.id}")
                ])

    # FAQAT Super Admin uchun karta qo'shish tugmasini chiqaramiz
    if is_super:
        keyboard.append([
            InlineKeyboardButton("➕ Karta qo'shish", callback_data="card:add")
        ])

    if query:
        query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    else:
        update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )