import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from kiro_api import kiro_client
from config import settings

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome_message = (
        f"👋 Halo {user.first_name}!\n\n"
        f"🤖 Saya adalah AI Assistant yang siap membantu kamu.\n\n"
        f"✨ *Fitur yang tersedia:*\n"
        f"• Chat bebas dengan AI\n• Bantuan pemrograman & debugging\n• Tanya apa saja!\n\n"
        f"📝 *Perintah:*\n/start - Mulai bot\n/help - Bantuan\n/clear - Reset percakapan\n\n"
        f"💡 Kirim pesan apa saja untuk mulai!"
    )
    keyboard = [
        [InlineKeyboardButton("💬 Mulai Chat", callback_data="chat")],
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")]
    ]
    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = "🤖 *Panduan Bot*\n\nKirim pesan teks biasa dan AI akan membalas!\n\n*Perintah:*\n/start /help /clear"
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text("🗑️ Riwayat percakapan telah dihapus!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    history = context.user_data.get("history", [])
    response = kiro_client.send_message(message, history=history)
    reply_text = kiro_client.format_response(response)
    if "error" not in response:
        history.extend([{"role": "user", "content": message}, {"role": "assistant", "content": reply_text}])
        context.user_data["history"] = history[-20:]
    await update.message.reply_text(reply_text)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "chat":
        await query.message.reply_text("💬 Silakan kirim pesan kamu!")
    elif query.data == "help":
        await help_command(update, context)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error: {context.error}")

def register_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_context))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
