# 🤖 Kiro AI Telegram Bot

Telegram bot yang terhubung dengan Kiro AI untuk membantu berbagai tugas seperti coding, debugging, dan konsultasi teknis.

## 🚀 Fitur

- **Chat dengan Kiro AI**: Interaksi langsung dengan AI untuk berbagai kebutuhan
- **Multi-language Support**: Mendukung berbagai bahasa pemrograman
- **Error Handling**: Robust error handling dan logging
- **Webhook & Polling**: Support kedua mode (webhook untuk production, polling untuk development)
- **Admin Controls**: Perintah khusus untuk admin
- **Health Monitoring**: Endpoint health check untuk monitoring
- **Deployment Ready**: Siap deploy ke Railway dengan Docker

## 📋 Prasyarat

- Python 3.11+
- Telegram Bot Token dari [@BotFather](https://t.me/botfather)
- Kiro API Key dari [Kiro AI](https://kiro.ai)
- Docker (untuk deployment)

## 🏗️ Struktur Proyek

```
telegram-ai-bot/
├── main.py              # Entry point aplikasi
├── config.py            # Konfigurasi aplikasi
├── kiro_api.py          # Client Kiro API
├── bot_handlers.py      # Handler bot Telegram
├── requirements.txt     # Dependensi Python
├── Dockerfile          # Konfigurasi Docker
├── railway.toml        # Konfigurasi Railway
├── .env.example        # Contoh environment variables
├── .dockerignore       # Ignore file untuk Docker
└── README.md           # Dokumentasi ini
```

## ⚙️ Setup Lokal

### 1. Clone Repository

```bash
git clone https://github.com/catesnew1-svg/telegram-ai-bot.git
cd telegram-ai-bot
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment Variables

Buat file `.env` dari template:

```bash
cp .env.example .env
```

Edit file `.env` dengan konfigurasi Anda:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_URL=  # Kosongkan untuk mode polling

# Kiro API Configuration
KIRO_API_URL=https://api.kiro.ai/v1
KIRO_API_KEY=your_kiro_api_key_here

# Bot Settings
ADMIN_USER_IDS=123456789,987654321  # User ID admin dipisah koma
DEBUG_MODE=false
LOG_LEVEL=INFO

# Server Settings
PORT=8000
HOST=0.0.0.0
```

### 5. Jalankan Bot (Mode Polling)

```bash
python main.py
```

Bot akan berjalan dalam mode polling (cocok untuk development).

## 🌐 Deployment ke Railway

### 1. Push ke GitHub

Pastikan kode sudah ada di repository GitHub.

### 2. Setup Railway

1. Login ke [Railway](https://railway.app)
2. Create New Project → Deploy from GitHub
3. Pilih repository `telegram-ai-bot`
4. Railway akan otomatis mendeteksi Dockerfile dan deploy

### 3. Konfigurasi Environment Variables di Railway

Setelah deployment, tambahkan environment variables di Railway Dashboard:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-app-name.up.railway.app
KIRO_API_KEY=your_kiro_api_key_here
ADMIN_USER_IDS=your_admin_user_ids
```

### 4. Set Webhook (Otomatis)

Bot akan otomatis mengatur webhook saat dijalankan dengan `TELEGRAM_WEBHOOK_URL` yang valid.

## 📡 Webhook vs Polling

- **Webhook** (Production): Bot menerima update via HTTPS endpoint
  - Lebih cepat
  - Hemat resource
  - Membutuhkan domain publik
- **Polling** (Development): Bot secara aktif mengecek update
  - Cocok untuk development lokal
  - Tidak butuh domain publik
  - Lebih lambat

## 🤖 Perintah Bot

| Perintah | Deskripsi | Hak Akses |
|----------|-----------|-----------|
| `/start` | Mulai bot dan tampilkan menu | Semua user |
| `/help` | Tampilkan panduan penggunaan | Semua user |
| `/status` | Cek status bot dan koneksi | Semua user |
| `/usage` | Lihat penggunaan API Kiro | Admin only |
| `/clear` | Hapus percakapan (reset context) | Semua user |

## 💬 Penggunaan

1. Mulai bot dengan `/start`
2. Kirim pesan apa saja untuk chat dengan Kiro AI
3. Gunakan tombol inline untuk navigasi cepat
4. Untuk reset percakapan, gunakan `/clear`

## 🧪 Testing

### Manual Testing

1. Cari bot Anda di Telegram
2. Kirim perintah dan verifikasi respons
3. Test berbagai skenario error

### Health Check

```bash
curl https://your-app-name.up.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "telegram_bot": {
    "username": "your_bot_username",
    "id": 1234567890,
    "is_bot": true
  },
  "kiro_api": "connected",
  "debug_mode": false
}
```

## 🐛 Troubleshooting

### Bot Tidak Merespons

1. Cek logs di Railway Dashboard
2. Verifikasi `TELEGRAM_BOT_TOKEN` valid
3. Pastikan bot tidak di-block

### Error Kiro API

1. Cek `KIRO_API_KEY` valid
2. Verifikasi koneksi internet
3. Cek quota API di dashboard Kiro

### Webhook Error

1. Pastikan `TELEGRAM_WEBHOOK_URL` valid HTTPS
2. Cek port forwarding (jika lokal)
3. Verifikasi SSL certificate

## 📝 Logging

Log tersedia di:
- Console output (development)
- Railway logs (production)
- File log (jika dikonfigurasi)

Level log dikontrol oleh `LOG_LEVEL`:
- `DEBUG`: Semua log termasuk debug
- `INFO`: Informasi normal
- `WARNING`: Peringatan
- `ERROR`: Error saja

## 🔧 Customization

### Tambah Handler Baru

Edit `bot_handlers.py`:

```python
def new_command(update: Update, context: CallbackContext):
    update.message.reply_text("Hello from new command!")

application.add_handler(CommandHandler("new", new_command))
```

### Modifikasi Kiro API Integration

Edit `kiro_api.py` untuk menyesuaikan:
- Format respons
- Error handling
- Timeout settings

## 📄 License

MIT License

## 🤝 Kontribusi

1. Fork repository
2. Buat feature branch
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

## 📧 Support

Untuk bantuan:
1. Cek [issues](https://github.com/catesnew1-svg/telegram-ai-bot/issues)
2. Hubungi admin via Telegram
3. Baca dokumentasi Kiro API di [docs.kiro.ai](https://docs.kiro.ai)