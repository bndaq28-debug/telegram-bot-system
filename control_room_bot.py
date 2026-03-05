from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = "8679213655:AAFzstGI4tymiFMDKWtUYVTT1sU_WkWIo8A"
CHANNEL_ID = "@testrosebot0305"

# ---- (선택) /post /suspend 권한 제한 ----
ALLOWED_USERS = set([
    # 123456789,
])

def is_allowed(user_id: int) -> bool:
    return (len(ALLOWED_USERS) == 0) or (user_id in ALLOWED_USERS)

# ---- Anti-spam: "연속 메시지" 경고만 ----
WARN_AT = 8
STRONG_WARN_AT = 10

# chat_id -> {"last_user_id": int, "streak": int}
CHAT_STREAK = {}

async def anti_spam_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Warn if a user sends messages consecutively in a group."""
    if not update.message or not update.effective_user or not update.effective_chat:
        return

    chat = update.effective_chat
    user = update.effective_user

    # Only groups
    if chat.type not in ("group", "supergroup"):
        return

    # Ignore bots
    if user.is_bot:
        return

    state = CHAT_STREAK.get(chat.id, {"last_user_id": None, "streak": 0})

    if state["last_user_id"] == user.id:
        state["streak"] += 1
    else:
        state["last_user_id"] = user.id
        state["streak"] = 1

    CHAT_STREAK[chat.id] = state
    streak = state["streak"]

    if streak == WARN_AT:
        await update.message.reply_text(
            "⚠️ 주의: 메시지를 너무 연속으로 보내고 있어요.\n"
            "그룹 채팅 스팸으로 오해될 수 있으니 잠시 텀을 두고 작성해주세요.\n"
            f"(연속 {WARN_AT}회)"
        )

    if streak == STRONG_WARN_AT:
        await update.message.reply_text(
            "🚫 경고: 연속 도배가 감지되었습니다.\n"
            "계속 스팸이 반복되면 다른 봇/관리자 시스템에 의해 채팅이 제한(뮤트)될 수 있습니다.\n"
            f"(연속 {STRONG_WARN_AT}회)"
        )

# ---- Channel posting commands ----
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None or update.message is None:
        return

    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text("❌ 권한이 없습니다. 관리자에게 문의해주세요.")
        return

    msg = " ".join(context.args).strip()
    if not msg:
        await update.message.reply_text("사용법: /post <공지 내용>")
        return

    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    await update.message.reply_text("✅ 채널에 공지가 게시되었습니다.")

async def suspend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None or update.message is None:
        return

    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text("❌ 권한이 없습니다. 관리자에게 문의해주세요.")
        return

    raw = " ".join(context.args).strip()
    if not raw or "|" not in raw:
        await update.message.reply_text(
            "사용법:\n"
            "/suspend <날짜> | <시간> | <예상 소요> | <영향 서비스>\n"
            "예:\n"
            "/suspend 2026-04-02 | 10:00(KST) | 약 2시간 | 거래, 입출금"
        )
        return

    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 4:
        await update.message.reply_text(
            "입력 항목이 부족합니다.\n"
            "형식: <날짜> | <시간> | <예상 소요> | <영향 서비스>"
        )
        return

    date, time, duration, services = parts[0], parts[1], parts[2], parts[3]

    text = (
        "⏸ 서비스 일시 중단 안내\n\n"
        "시스템 점검/업그레이드로 인해 일부 서비스가 일시적으로 중단됩니다.\n\n"
        f"• 📅 날짜: {date}\n"
        f"• 🕒 시간: {time}\n"
        f"• ⏳ 예상 소요: {duration}\n\n"
        "영향 서비스:\n"
        f"• {services}\n\n"
        "서비스는 점검 완료 후 순차적으로 정상화됩니다.\n"
        "이용에 불편을 드려 죄송합니다.\n\n"
        "🔗 공식 공지:\n"
        "[공식 링크 삽입]\n\n"
        "업데이트 채널:\n"
        "• 📲 App Download: https://bitbnq.com/services/downloads\n"
        "• 🐦 Twitter/X: https://x.com/BitnasdaqGlobal\n"
        "• 💬 Telegram: [Telegram 링크 삽입]"
    )

    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    await update.message.reply_text("✅ 서비스 중단 공지가 채널에 게시되었습니다.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text(
        "📌 사용 가능한 명령어\n"
        "/post <공지 내용>  → 채널에 그대로 게시\n"
        "/suspend <날짜> | <시간> | <예상 소요> | <영향 서비스>  → 서비스 중단 템플릿 게시\n"
        "/help  → 도움말\n\n"
        "※ 그룹에서 같은 사람이 메시지를 연속으로 보내면 자동 경고가 표시됩니다."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("post", post))
    app.add_handler(CommandHandler("suspend", suspend))
    app.add_handler(CommandHandler("help", help_cmd))

    # Anti-spam warning for group messages (text only, not commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam_warning))

    app.run_polling()

if __name__ == "__main__":
    main()