import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
from kiro_api import kiro_client
from config import settings

logger = logging.getLogger(__name__)

def is_authenticated(context) -> bool:
    return context.user_data.get("authenticated", False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_authenticated(context):
        skill_active = "✅ Ada" if context.user_data.get("system_prompt") else "⚙️ Default"
        await update.message.reply_text(
            f"👋 Kamu sudah login!\n\n"
            f"📄 Skill aktif: {skill_active}\n\n"
            f"Kirim pesan untuk chat dengan AI.\n"
            f"Kirim file .md untuk ganti skill bot.\n\n"
            f"/skill - Lihat skill aktif\n"
            f"/clear - Reset chat\n"
            f"/logout - Keluar"
        )
    else:
        await update.message.reply_text(
            "🔐 *Bot ini private.*\n\nMasukkan kode akses:",
            parse_mode="Markdown"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authenticated(context):
        await update.message.reply_text("🔐 Masukkan kode akses dulu.")
        return
    await update.message.reply_text(
        "🤖 *Bantuan*\n\n"
        "/start - Menu utama\n"
        "/skill - Lihat skill aktif\n"
        "/clear - Reset riwayat chat\n"
        "/logout - Keluar\n\n"
        "📄 *Kirim file .md* untuk update skill bot!",
        parse_mode="Markdown"
    )

async def show_skill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authenticated(context):
        await update.message.reply_text("🔐 Masukkan kode akses dulu.")
        return
    skill = context.user_data.get("system_prompt")
    if skill:
        preview = skill[:800] + "..." if len(skill) > 800 else skill
        await update.message.reply_text(
            f"📄 *Skill aktif (custom):*\n\n{preview}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "⚙️ Menggunakan skill default.\n\nKirim file .md untuk load skill custom!"
        )

async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authenticated(context):
        await update.message.reply_text("🔐 Masukkan kode akses dulu.")
        return
    context.user_data["history"] = []
    await update.message.reply_text("🗑️ Riwayat chat dihapus!")

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text("👋 Logout berhasil.\n\nKetik /start untuk login lagi.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authenticated(context):
        await update.message.reply_text("🔐 Masukkan kode akses dulu.")
        return

    doc = update.message.document
    file_name = doc.file_name or ""

    if not file_name.endswith(".md"):
        await update.message.reply_text("⚠️ Harus file .md ya! Contoh: SKILL.md")
        return

    try:
        await update.message.reply_text("⏳ Membaca skill...")

        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()
        skill_content = file_bytes.decode("utf-8")

        context.user_data["system_prompt"] = skill_content
        context.user_data["history"] = []

        await update.message.reply_text(
            f"✅ *Skill berhasil dimuat!*\n\n"
            f"📄 File: `{file_name}`\n"
            f"📝 {len(skill_content)} karakter\n\n"
            f"Chat history direset. Silakan mulai chat!",
            parse_mode="Markdown"
        )
        logger.info(f"Skill dimuat: {file_name} ({len(skill_content)} chars)")

    except UnicodeDecodeError:
        await update.message.reply_text("❌ File tidak bisa dibaca. Pastikan format UTF-8.")
    except Exception as e:
        logger.error(f"Error membaca file: {e}")
        await update.message.reply_text("❌ Gagal membaca file.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text

    if not is_authenticated(context):
        if settings.ACCESS_CODE and message == settings.ACCESS_CODE:
            context.user_data["authenticated"] = True
            await update.message.reply_text(
                "✅ *Kode benar! Selamat datang.*\n\n"
                "Kirim pesan untuk mulai chat.\n"
                "Kirim file .md untuk load skill agent.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Kode salah. Coba lagi:")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    history = context.user_data.get("history", [])
    system_prompt = context.user_data.get("system_prompt", None)

    response = kiro_client.send_message(message, history=history, system_prompt=system_prompt)
    reply_text = kiro_client.format_response(response)

    if "error" not in response:
        history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply_text}
        ])
        context.user_data["history"] = history[-20:]

    try:
        await update.message.reply_text(reply_text)
    except Exception as e:
        logger.error(f"Error kirim pesan: {e}")
        await update.message.reply_text("❌ Gagal mengirim respons.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error: {context.error}")

def register_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("skill", show_skill))
    application.add_handler(CommandHandler("clear", clear_context))
    application.add_handler(CommandHandler("logout", logout))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    logger.info("Semua handlers diregistrasi")
