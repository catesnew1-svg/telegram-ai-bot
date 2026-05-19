import logging
import json
import os
from typing import Dict, Any, Optional
import requests
from config import settings

logger = logging.getLogger(__name__)

def load_default_skill() -> str:
    skill_path = os.path.join(os.path.dirname(__file__), "SKILL.md")
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Kamu adalah asisten AI yang membantu dan ramah. Jawab dalam Bahasa Indonesia kecuali diminta sebaliknya."

class KiroAPI:
    def __init__(self):
        self.api_url = settings.KIRO_API_URL
        self.api_key = settings.KIRO_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.system_prompt = load_default_skill()
        logger.info("KiroAPI siap")

    def send_message(self, message: str, history: list = None, system_prompt: str = None) -> Dict[str, Any]:
        try:
            active_prompt = system_prompt if system_prompt else self.system_prompt

            messages = [{"role": "system", "content": active_prompt}]
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": message})

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }

            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
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
