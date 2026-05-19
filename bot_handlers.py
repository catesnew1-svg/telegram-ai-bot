import logging
from telegram import Update
from telegram.ext import (
    ContextTypes, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from kiro_api import kiro_client
from config import settings

logger = logging.getLogger(__name__)

def is_authenticated(context) -> bool:
    return context.user_data.get("authenticated", False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_authenticated(context):
        await update.message.reply_text(
            "👋 Kamu sudah login!\n\nKirim pesan apa saja untuk chat dengan AI.\n/clear - Reset percakapan\n/logout - Keluar"
        )
    else:
        await update.message.reply_text(
            "🔐 *Bot ini private.*\n\nMasukkan kode akses untuk melanjutkan:",
            parse_mode="Markdown"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authenticated(context):
        await update.message.reply_text("🔐 Masukkan kode akses dulu.")
        return
    await update.message.reply_text(
        "🤖 *Bantuan*\n\n/start - Mulai\n/clear - Reset chat\n/logout - Keluar",
        parse_mode="Markdown"
    )

async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authenticated(context):
        await update.message.reply_text("🔐 Masukkan kode akses dulu.")
        return
    context.user_data["history"] = []
    await update.message.reply_text("🗑️ Riwayat chat dihapus!")

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text("👋 Kamu sudah logout. Ketik /start untuk login lagi.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text

    # Belum auth → cek kode akses
    if not is_authenticated(context):
        if message == settings.ACCESS_CODE:
            context.user_data["authenticated"] = True
            await update.message.reply_text("✅ Kode benar! Selamat datang.\n\nKirim pesan apa saja untuk mulai chat.")
        else:
            await update.message.reply_text("❌ Kode salah. Coba lagi:")
        return

    # Sudah auth → proses ke AI
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    history = context.user_data.get("history", [])
    response = kiro_client.send_message(message, history=history)
    reply_text = kiro_client.format_response(response)

    if "error" not in response:
        history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply_text}
        ])
        context.user_data["history"] = history[-20:]

    await update.message.reply_text(reply_text)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error: {context.error}")

def register_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_context))
    application.add_handler(CommandHandler("logout", logout))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
