from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8679213655:AAFzstGI4tymiFMDKWtUYVTT1sU_WkWIo8A"
GROUP_ID = -1003859852646


async def relay_anything(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    # Only handle private chat (DM)
    if update.effective_chat.type != "private":
        return

    try:
        # Copy the exact message (works for text, photo+caption, video+caption, documents, etc.)
        sent = await context.bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id,
        )

        # Pin the copied message in the group
        await context.bot.pin_chat_message(
            chat_id=GROUP_ID,
            message_id=sent.message_id,
            disable_notification=True,  # set False if you want pin notification
        )

        # Confirm to you (Korean)
        await update.message.reply_text("✅ 그룹 채팅에 메시지가 전송되었습니다.")

    except Exception:
        await update.message.reply_text(
            "❌ 전송/고정에 실패했습니다.\n"
            "봇이 그룹에 추가되어 있는지, 관리자 권한(특히 '메시지 고정')이 있는지 확인해주세요."
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Relay almost everything sent in DM (text/media)
    app.add_handler(MessageHandler(filters.ALL, relay_anything))

    app.run_polling()


if __name__ == "__main__":
    main()