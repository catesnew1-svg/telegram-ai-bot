import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    Filters,
    CallbackContext
)
from kiro_api import kiro_client
from config import settings

logger = logging.getLogger(__name__)

# Conversation states
CHOOSING, TYPING_REPLY = range(2)

def start(update: Update, context: CallbackContext) -> None:
    """Handler untuk command /start."""
    user = update.effective_user
    welcome_message = f"""
👋 Halo {user.mention_html()}!

🤖 Saya adalah bot Telegram yang terhubung dengan Kiro AI.

✨ *Fitur yang tersedia:*
• Chat dengan AI menggunakan Kiro
• Dapatkan bantuan pemrograman
• Bantuan debugging code
• Dan banyak lagi!

📝 *Perintah yang tersedia:*
/start - Mulai bot
/help - Tampilkan bantuan
/status - Cek status bot
/usage - Lihat penggunaan API
/clear - Hapus percakapan

💡 *Cara penggunaan:*
Cukup kirim pesan apa saja, dan saya akan membalas dengan bantuan Kiro AI!

⚙️ *Informasi Bot:*
• Admin: {'✅' if user.id in settings.ADMIN_USER_IDS else '❌'}
• Mode Debug: {'✅' if settings.DEBUG_MODE else '❌'}
    """
    
    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton("💬 Chat dengan Kiro", callback_data="chat")],
        [InlineKeyboardButton("📊 Cek Status", callback_data="status")],
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_html(welcome_message, reply_markup=reply_markup)
    logger.info(f"User {user.id} ({user.username}) memulai bot")


def help_command(update: Update, context: CallbackContext) -> None:
    """Handler untuk command /help."""
    help_text = """
🤖 *Bantuan Bot Kiro AI*

📚 *Perintah:*
/start - Mulai bot
/help - Tampilkan pesan bantuan ini
/status - Cek status bot dan koneksi API
/usage - Lihat penggunaan API Kiro
/clear - Hapus percakapan (reset context)

💬 *Cara Penggunaan:*
1. Kirim pesan teks biasa untuk chat dengan Kiro AI
2. Gunakan perintah di atas untuk kontrol bot
3. Bot akan merespons dengan bantuan AI

🔧 *Fitur:*
• Chat dengan Kiro AI
• Support untuk berbagai bahasa
• Context-aware responses
• Error handling

⚠️ *Catatan:*
• Bot tidak menyimpan data percakapan secara permanen
• Respons mungkin memerlukan waktu beberapa detik
• Pastikan koneksi internet stabil

📞 *Support:*
Jika mengalami masalah, hubungi admin.
    """
    
    update.message.reply_markdown(help_text)
    logger.info(f"User {update.effective_user.id} meminta bantuan")


def status(update: Update, context: CallbackContext) -> None:
    """Handler untuk command /status."""
    user = update.effective_user
    
    # Check Kiro API connection
    try:
        usage_info = kiro_client.get_usage_info()
        kiro_status = "✅ Terhubung"
        if usage_info:
            kiro_status += f"\n• Credits tersisa: {usage_info.get('remaining_credits', 'N/A')}"
    except Exception as e:
        kiro_status = f"❌ Error: {str(e)}"
    
    status_message = f"""
📊 *Status Bot Kiro AI*

👤 *User:*
• ID: `{user.id}`
• Username: @{user.username or 'N/A'}
• Admin: {'✅' if user.id in settings.ADMIN_USER_IDS else '❌'}

🤖 *Bot Status:*
• API Kiro: {kiro_status}
• Mode Debug: {'✅' if settings.DEBUG_MODE else '❌'}
• Log Level: {settings.LOG_LEVEL}

🌐 *Server:*
• Port: {settings.PORT}
• Host: {settings.HOST}
• Webhook: {'✅' if settings.TELEGRAM_WEBHOOK_URL else '❌'}

🔧 *Versi:*
• Python Telegram Bot: 20.7
• Kiro API: v1
    """
    
    update.message.reply_markdown(status_message)
    logger.info(f"User {user.id} memeriksa status bot")


def usage(update: Update, context: CallbackContext) -> None:
    """Handler untuk command /usage."""
    user = update.effective_user
    
    if user.id not in settings.ADMIN_USER_IDS:
        update.message.reply_text("❌ Hanya admin yang dapat melihat penggunaan API.")
        return
    
    usage_info = kiro_client.get_usage_info()
    
    if usage_info:
        usage_message = f"""
📈 *Penggunaan API Kiro*

🔑 *Informasi Akun:*
• Credits tersisa: {usage_info.get('remaining_credits', 'N/A')}
• Total requests: {usage_info.get('total_requests', 'N/A')}
• Requests bulan ini: {usage_info.get('monthly_requests', 'N/A')}

📊 *Statistik:*
• Success rate: {usage_info.get('success_rate', 'N/A')}%
• Avg response time: {usage_info.get('avg_response_time', 'N/A')}ms
        """
    else:
        usage_message = "❌ Tidak dapat mengambil informasi penggunaan API."
    
    update.message.reply_markdown(usage_message)
    logger.info(f"Admin {user.id} memeriksa penggunaan API")


def clear_context(update: Update, context: CallbackContext) -> None:
    """Handler untuk command /clear."""
    if 'conversation_context' in context.chat_data:
        del context.chat_data['conversation_context']
    
    update.message.reply_text("✅ Percakapan telah direset. Context telah dihapus.")
    logger.info(f"User {update.effective_user.id} menghapus context")


def handle_message(update: Update, context: CallbackContext) -> None:
    """Handler untuk pesan teks biasa."""
    user = update.effective_user
    message_text = update.message.text
    
    if not message_text.strip():
        update.message.reply_text("⚠️ Mohon kirim pesan yang valid.")
        return
    
    logger.info(f"User {user.id} mengirim pesan: {message_text[:50]}...")
    
    # Show typing indicator
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get previous context if exists
    conversation_context = context.chat_data.get('conversation_context', {})
    
    try:
        # Send message to Kiro API
        kiro_response = kiro_client.send_message(message_text, conversation_context)
        
        # Format and send response
        formatted_response = kiro_client.format_response(kiro_response)
        
        # Update conversation context
        if "conversation_id" in kiro_response:
            conversation_context["conversation_id"] = kiro_response["conversation_id"]
        context.chat_data['conversation_context'] = conversation_context
        
        # Send response (split if too long)
        if len(formatted_response) > 4096:
            for i in range(0, len(formatted_response), 4096):
                update.message.reply_text(
                    formatted_response[i:i+4096],
                    parse_mode="Markdown"
                )
        else:
            update.message.reply_text(formatted_response, parse_mode="Markdown")
        
        logger.info(f"Berhasil membalas pesan user {user.id}")
        
    except Exception as e:
        error_message = f"❌ Terjadi kesalahan: {str(e)}"
        update.message.reply_text(error_message)
        logger.error(f"Error handling message from user {user.id}: {e}")


def button_callback(update: Update, context: CallbackContext) -> None:
    """Handler untuk callback dari inline keyboard."""
    query = update.callback_query
    query.answer()
    
    user = query.from_user
    
    if query.data == "chat":
        query.edit_message_text(
            text="💬 *Mode Chat Aktif*\n\nKirim pesan apa saja untuk chat dengan Kiro AI!",
            parse_mode="Markdown"
        )
    elif query.data == "status":
        query.edit_message_text(
            text=f"📊 *Status Bot*\n\n👤 User: {user.username or user.id}\n🤖 Status: Online\n⚡ API: Connected",
            parse_mode="Markdown"
        )
    elif query.data == "help":
        query.edit_message_text(
            text="❓ *Bantuan*\n\nKirim /help untuk melihat panduan lengkap penggunaan bot.",
            parse_mode="Markdown"
        )
    
    logger.info(f"User {user.id} menekan tombol: {query.data}")


def error_handler(update: Update, context: CallbackContext) -> None:
    """Handler untuk error."""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            update.effective_message.reply_text(
                "❌ Maaf, terjadi kesalahan internal. Silakan coba lagi nanti."
            )
    except Exception as e:
        logger.error(f"Error sending error message: {e}")


# Register all handlers
def register_handlers(application):
    """Register semua handlers ke application."""
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("usage", usage))
    application.add_handler(CommandHandler("clear", clear_context))
    
    # Message handler
    application.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        handle_message
    ))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("Semua handlers telah diregistrasi")