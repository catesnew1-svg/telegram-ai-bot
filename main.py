#!/usr/bin/env python3
import logging
import logging.config
import sys
from telegram.ext import ApplicationBuilder
from config import settings, LOGGING_CONFIG
from bot_handlers import register_handlers

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("=== Memulai Telegram AI Bot ===")
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        register_handlers(application)
        logger.info("Bot berjalan dengan mode polling...")
        application.run_polling(poll_interval=1, timeout=30, drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot dihentikan")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
