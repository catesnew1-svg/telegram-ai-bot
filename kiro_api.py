import logging
import json
from typing import Dict, Any, Optional
import requests
from config import settings

logger = logging.getLogger(__name__)

class KiroAPI:
    def __init__(self):
        self.api_url = settings.KIRO_API_URL
        self.api_key = settings.KIRO_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_message(self, message: str, history: list = None) -> Dict[str, Any]:
        try:
            messages = [{"role": "system", "content": "Kamu adalah asisten AI yang membantu dan ramah. Jawab dalam Bahasa Indonesia kecuali user minta bahasa lain."}]
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": message})

            payload = {
                "model": "llama3-8b-8192",
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }

            response = requests.post(f"{self.api_url}/chat/completions", headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            return {"error": "Timeout", "message": "⏱️ AI tidak merespons, coba lagi."}
        except requests.exceptions.ConnectionError:
            return {"error": "ConnectionError", "message": "❌ Tidak dapat terhubung ke AI."}
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTPError: {response.status_code}", "message": f"❌ Error: {response.text}"}
        except Exception as e:
            return {"error": "UnknownError", "message": f"❌ Terjadi kesalahan: {str(e)}"}

    def format_response(self, api_response: Dict[str, Any]) -> str:
        if "error" in api_response:
            return api_response.get("message", "❌ Error tidak diketahui")
        if "choices" in api_response and len(api_response["choices"]) > 0:
            return api_response["choices"][0].get("message", {}).get("content", "❌ Respons kosong")
        return json.dumps(api_response, indent=2, ensure_ascii=False)

kiro_client = KiroAPI()
