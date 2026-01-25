# handlers/broadcast.py
import time
from telegram import Update
from telegram.ext import CallbackContext
from database.config import ADMIN_IDS
from database.dependencies import get_all_users

ADMIN_ID = ADMIN_IDS.SUPERADMIN_ID

def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Siz admin emassiz")
        return

    users = get_all_users()

    msg = update.message

    sent = 0
    failed = 0

    for user in users:
        try:
            if msg.text:
                context.bot.send_message(user.chat_id, msg.text)
            elif msg.photo:
                context.bot.send_photo(
                    user.chat_id,
                    msg.photo[-1].file_id,
                    caption=msg.caption
                )
            elif msg.video:
                context.bot.send_video(
                    user.chat_id,
                    msg.video.file_id,
                    caption=msg.caption
                )

            sent += 1
            time.sleep(0.05)

        except:
            failed += 1
            continue

    update.message.reply_text(
        f"📢 Yakunlandi\n"
        f"Yuborildi: {sent}\n"
        f"Xato: {failed}"
    )