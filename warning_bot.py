from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8679213655:AAFzstGI4tymiFMDKWtUYVTT1sU_WkWIo8A"

# Warning thresholds
WARN_AT = 5
STRONG_WARN_AT = 10  # optional; keep or remove

# chat_id -> {"last_user_id": int, "streak": int}
CHAT_STREAK = {}

async def anti_spam_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or not update.effective_chat:
        return

    chat = update.effective_chat
    user = update.effective_user

    # Only in group/supergroup
    if chat.type not in ("group", "supergroup"):
        return

    # Ignore bots
    if user.is_bot:
        return

    state = CHAT_STREAK.get(chat.id, {"last_user_id": None, "streak": 0})

    # "in a row" = same user sends consecutive messages without others speaking
    if state["last_user_id"] == user.id:
        state["streak"] += 1
    else:
        state["last_user_id"] = user.id
        state["streak"] = 1

    CHAT_STREAK[chat.id] = state
    streak = state["streak"]

    if streak == WARN_AT:
        await update.message.reply_text(
            "⚠️ 도배 주의\n"
            "연속으로 메시지를 보내고 있습니다.\n"
            "그룹 채팅 스팸으로 오해될 수 있으니 전송 간격을 조절해 주세요.\n"
            f"(연속 {WARN_AT}회)"
        )

    if STRONG_WARN_AT and streak == STRONG_WARN_AT:
        await update.message.reply_text(
            "🚫 도배 경고\n"
            "연속 메시지가 계속 감지되었습니다.\n"
            "추가 도배가 발생할 경우 다른 봇/관리 시스템에 의해 채팅 제한(뮤트)이 적용될 수 있습니다.\n"
            f"(연속 {STRONG_WARN_AT}회)"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Watch normal text messages (not commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam_warning))

    app.run_polling()

if __name__ == "__main__":
    main()