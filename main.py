#!/usr/bin/env python3
"""
Telegram Bot dengan Kiro AI
Deploy ke Railway dengan webhook support
"""

import logging
import logging.config
from http import HTTPStatus
from typing import Dict, Any
import signal
import sys

from flask import Flask, request, jsonify
from telegram.ext import Application, ApplicationBuilder
import requests

from config import settings, LOGGING_CONFIG
from bot_handlers import register_handlers

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Flask app for webhook
app = Flask(__name__)
telegram_app: Application = None


def setup_telegram_bot() -> Application:
    """Setup dan konfigurasi Telegram bot."""
    logger.info("Menyiapkan Telegram bot...")
    
    # Build application
    app_builder = ApplicationBuilder()
    app_builder.token(settings.TELEGRAM_BOT_TOKEN)
    
    # Add optional configuration
    if settings.DEBUG_MODE:
        app_builder.read_timeout(30)
        app_builder.write_timeout(30)
        app_builder.connect_timeout(30)
        app_builder.pool_timeout(30)
    
    application = app_builder.build()
    
    # Register handlers
    register_handlers(application)
    
    logger.info("Telegram bot berhasil disiapkan")
    return application


def setup_webhook(application: Application) -> bool:
    """Setup webhook untuk Telegram bot."""
    if not settings.TELEGRAM_WEBHOOK_URL:
        logger.warning("TELEGRAM_WEBHOOK_URL tidak diset, menggunakan polling")
        return False
    
    try:
        webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/webhook"
        logger.info(f"Mengatur webhook ke: {webhook_url}")
        
        # Set webhook
        application.bot.set_webhook(
            url=webhook_url,
            max_connections=40,
            allowed_updates=["message", "callback_query"]
        )
        
        logger.info("Webhook berhasil diatur")
        return True
        
    except Exception as e:
        logger.error(f"Gagal mengatur webhook: {e}")
        return False


def health_check() -> Dict[str, Any]:
    """Health check untuk aplikasi."""
    try:
        # Check Telegram bot
        bot_info = telegram_app.bot.get_me() if telegram_app else None
        
        # Check Kiro API (optional)
        kiro_status = "unknown"
        try:
            import kiro_api
            usage_info = kiro_api.kiro_client.get_usage_info()
            kiro_status = "connected" if usage_info else "error"
        except:
            kiro_status = "not_checked"
        
        return {
            "status": "healthy",
            "telegram_bot": {
                "username": bot_info.username if bot_info else None,
                "id": bot_info.id if bot_info else None,
                "is_bot": bot_info.is_bot if bot_info else None
            },
            "kiro_api": kiro_status,
            "debug_mode": settings.DEBUG_MODE
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.route('/health', methods=['GET'])
def health():
    """Endpoint untuk health check."""
    return jsonify(health_check()), HTTPStatus.OK


@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint untuk webhook Telegram."""
    if telegram_app is None:
        return jsonify({"error": "Bot not initialized"}), HTTPStatus.SERVICE_UNAVAILABLE
    
    try:
        # Process update
        update = telegram_app.update_queue.get_nowait()
        telegram_app.process_update(update)
        return jsonify({"status": "ok"}), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/')
def index():
    """Halaman utama."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kiro AI Telegram Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 10px;
            }
            .status {
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .healthy {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .unhealthy {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .endpoints {
                margin-top: 30px;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #4CAF50;
                border-radius: 4px;
            }
            code {
                background: #e9ecef;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Kiro AI Telegram Bot</h1>
            
            <p>Telegram bot yang terhubung dengan Kiro AI untuk membantu berbagai tugas.</p>
            
            <div class="status healthy">
                <strong>✅ Status:</strong> Bot berjalan dengan baik
            </div>
            
            <div class="endpoints">
                <h3>📊 Endpoints</h3>
                
                <div class="endpoint">
                    <strong>GET <code>/health</code></strong>
                    <p>Health check endpoint untuk monitoring.</p>
                </div>
                
                <div class="endpoint">
                    <strong>POST <code>/webhook</code></strong>
                    <p>Webhook endpoint untuk Telegram bot.</p>
                </div>
            </div>
            
            <div class="info">
                <h3>ℹ️ Informasi</h3>
                <ul>
                    <li><strong>Framework:</strong> Python + Flask</li>
                    <li><strong>Telegram Library:</strong> python-telegram-bot v20.7</li>
                    <li><strong>Deployment:</strong> Railway</li>
                    <li><strong>API:</strong> Kiro AI</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """


def signal_handler(signum, frame):
    """Handler untuk signal shutdown."""
    logger.info(f"Menerima signal {signum}, melakukan shutdown...")
    if telegram_app:
        telegram_app.stop()
        telegram_app.shutdown()
    sys.exit(0)


def main():
    """Fungsi utama untuk menjalankan bot."""
    global telegram_app
    
    try:
        logger.info("=== Memulai Kiro AI Telegram Bot ===")
        logger.info(f"Debug Mode: {settings.DEBUG_MODE}")
        logger.info(f"Log Level: {settings.LOG_LEVEL}")
        logger.info(f"Host: {settings.HOST}")
        logger.info(f"Port: {settings.PORT}")
        
        # Setup Telegram bot
        telegram_app = setup_telegram_bot()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Setup webhook or polling
        use_webhook = setup_webhook(telegram_app)
        
        if use_webhook:
            logger.info("Mode: Webhook")
            # Run Flask app
            logger.info(f"Menjalankan Flask server di {settings.HOST}:{settings.PORT}")
            app.run(
                host=settings.HOST,
                port=settings.PORT,
                debug=settings.DEBUG_MODE
            )
        else:
            logger.info("Mode: Polling")
            # Run bot with polling
            telegram_app.run_polling(
                poll_interval=1,
                timeout=30,
                drop_pending_updates=True
            )
            
    except Exception as e:
        logger.error(f"Error utama: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()