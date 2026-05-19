import logging
import json
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from config import settings

logger = logging.getLogger(__name__)


class KiroAPI:
    """Client untuk berinteraksi dengan Kiro API."""
    
    def __init__(self):
        self.api_url = settings.KIRO_API_URL
        self.api_key = settings.KIRO_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def send_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Mengirim pesan ke Kiro API dan mendapatkan respons.
        
        Args:
            message: Pesan yang akan dikirim ke Kiro
            context: Konteks tambahan (opsional)
            
        Returns:
            Respons dari Kiro API
        """
        try:
            payload = {
                "message": message,
                "context": context or {}
            }
            
            logger.info(f"Mengirim pesan ke Kiro API: {message[:50]}...")
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("Berhasil mendapatkan respons dari Kiro API")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Timeout saat menghubungi Kiro API")
            return {
                "error": "Timeout",
                "message": "Kiro API tidak merespons dalam waktu yang ditentukan"
            }
        except requests.exceptions.ConnectionError:
            logger.error("Koneksi error dengan Kiro API")
            return {
                "error": "ConnectionError",
                "message": "Tidak dapat terhubung ke Kiro API"
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error dari Kiro API: {e}")
            return {
                "error": f"HTTPError: {response.status_code}",
                "message": f"Error dari Kiro API: {response.text}"
            }
        except Exception as e:
            logger.error(f"Error tidak terduga: {e}")
            return {
                "error": "UnknownError",
                "message": f"Terjadi kesalahan: {str(e)}"
            }
    
    def format_response(self, kiro_response: Dict[str, Any]) -> str:
        """
        Format respons dari Kiro API untuk ditampilkan di Telegram.
        
        Args:
            kiro_response: Respons dari Kiro API
            
        Returns:
            String yang sudah diformat
        """
        if "error" in kiro_response:
            error_msg = kiro_response.get("message", "Error tidak diketahui")
            return f"❌ *Error*:\n{error_msg}"
        
        # Contoh format untuk respons yang diharapkan
        if "choices" in kiro_response and len(kiro_response["choices"]) > 0:
            content = kiro_response["choices"][0].get("message", {}).get("content", "")
            return content
        
        # Fallback untuk format lain
        if "response" in kiro_response:
            return kiro_response["response"]
        
        if "message" in kiro_response:
            return kiro_response["message"]
        
        # Jika tidak ada format yang cocok, kembalikan string JSON
        return json.dumps(kiro_response, indent=2, ensure_ascii=False)
    
    def get_usage_info(self) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan informasi penggunaan API.
        
        Returns:
            Informasi penggunaan API atau None jika error
        """
        try:
            response = requests.get(
                f"{self.api_url}/usage",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error mendapatkan info penggunaan: {e}")
            return None


# Singleton instance
kiro_client = KiroAPI()