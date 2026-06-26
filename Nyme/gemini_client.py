import os
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """Cliente compartido de Gemini AI. La API Key se guarda en la DB (settings)
    o como variable de entorno GEMINI_API_KEY como fallback."""

    def _get_api_key(self):
        try:
            from database import db
            key = db.get_setting("gemini_api_key")
            if key:
                return key
        except Exception:
            pass
        return os.getenv("GEMINI_API_KEY", "")

    def _get_model(self):
        try:
            import google.generativeai as genai
            api_key = self._get_api_key()
            if not api_key:
                return None
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-2.5-flash")
        except Exception as e:
            print(f"[Gemini] Error inicializando modelo: {e}")
            return None

    @property
    def is_configured(self):
        return bool(self._get_api_key())

    def translate(self, text, target_lang="español"):
        """Traduce el texto al idioma destino."""
        model = self._get_model()
        if not model:
            return None
        try:
            prompt = (
                f"Traduce al {target_lang}. Responde ÚNICAMENTE con la traducción, "
                f"sin explicaciones.\nTexto: {text}"
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini] Error traduciendo: {e}")
            return None

    def analyze_sentiment(self, messages):
        """Analiza el sentimiento de una conversación completa.
        Retorna dict: {sentiment, urgent, reason} o None si falla."""
        model = self._get_model()
        if not model:
            return None
        try:
            history_text = "\n".join([
                f"{'Cliente' if t == 'INBOUND' else 'Agente'}: {body}"
                for t, body, *_ in messages[-20:]
            ])
            prompt = (
                "Analiza el sentimiento general de esta conversación de atención al cliente de WhatsApp. "
                "Responde ÚNICAMENTE con un JSON válido con estas claves:\n"
                "- 'sentiment': 'positivo', 'neutral' o 'negativo'\n"
                "- 'urgent': true si el cliente está muy molesto, tiene una queja grave o amenaza con cancelar\n"
                "- 'reason': una frase corta (máx 15 palabras) explicando el motivo del sentimiento\n\n"
                f"Conversación:\n{history_text}\n\nJSON:"
            )
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Limpiar markdown si lo hay
            text = text.replace("```json", "").replace("```", "").strip()
            import json
            return json.loads(text)
        except Exception as e:
            print(f"[Gemini] Error analizando sentimiento: {e}")
            return None

    def generate_agent_feedback(self, agent_username, messages, sentiments_summary):
        """Genera feedback narrativo sobre el desempeño de un agente."""
        model = self._get_model()
        if not model:
            return None
        try:
            sla_green  = sentiments_summary.get("sla_green", 0)
            sla_yellow = sentiments_summary.get("sla_yellow", 0)
            sla_red    = sentiments_summary.get("sla_red", 0)
            sla_total  = sentiments_summary.get("sla_total", 0)
            avg_rt     = sentiments_summary.get("avg_rt", "N/A")

            sla_info = (
                f"  • Respuestas en < 5 min (🟢 excelente): {sla_green}/{sla_total}\n"
                f"  • Respuestas entre 5-30 min (🟡 aceptable): {sla_yellow}/{sla_total}\n"
                f"  • Respuestas en > 30 min (🔴 falla SLA): {sla_red}/{sla_total}\n"
                f"  • Tiempo promedio de respuesta: {avg_rt} minutos"
            ) if sla_total else "  • Sin datos de tiempos de respuesta"

            prompt = (
                f"Eres un supervisor de atención al cliente. Analiza el desempeño del agente '@{agent_username}' "
                f"basándote en estos datos del período:\n\n"
                f"- Mensajes enviados: {sentiments_summary.get('sent', 0)}\n"
                f"- Conversaciones atendidas: {sentiments_summary.get('chats', 0)}\n"
                f"- Cumplimiento de SLA (tiempo de respuesta):\n{sla_info}\n"
                f"- Sentimientos detectados: {sentiments_summary.get('positive', 0)} positivos, "
                f"{sentiments_summary.get('neutral', 0)} neutrales, "
                f"{sentiments_summary.get('negative', 0)} negativos\n\n"
                "Genera un feedback profesional y constructivo con:\n"
                "1. Fortalezas detectadas (1-2 puntos)\n"
                "2. Áreas de mejora (especialmente en tiempos de respuesta si hay fallas SLA)\n"
                "3. Una sugerencia concreta y accionable\n\n"
                "Sé breve, directo y en español."
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini] Error generando feedback: {e}")
            return None

    def detect_language(self, text):
        """Detecta el idioma del texto."""
        model = self._get_model()
        if not model:
            return "desconocido"
        try:
            prompt = (
                "Detecta el idioma del siguiente texto. Responde SOLO con el nombre "
                "del idioma en español (ej: 'inglés', 'francés', 'portugués').\n"
                f"Texto: {text}"
            )
            response = model.generate_content(prompt)
            return response.text.strip().lower()
        except Exception:
            return "desconocido"

    def suggest_reply(self, history):
        """Genera una sugerencia de respuesta basada en el historial del chat."""
        model = self._get_model()
        if not model:
            return None
        try:
            history_text = "\n".join([
                f"{'Cliente' if t == 'INBOUND' else 'Agente'}: {body}"
                for t, body, *_ in history[-10:]
            ])
            prompt = (
                "Eres un asistente de atención al cliente profesional y amable. "
                "Basándote en este historial de WhatsApp, escribe UNA respuesta breve y apropiada "
                "para el agente. Solo el texto de la respuesta, sin comillas ni explicaciones.\n\n"
                f"Historial:\n{history_text}\n\nRespuesta sugerida:"
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini] Error sugiriendo respuesta: {e}")
            return None

    def improve_text(self, text):
        """Mejora ortografía y tono del texto del agente."""
        model = self._get_model()
        if not model:
            return None
        try:
            prompt = (
                "Mejora este mensaje de atención al cliente: corrige ortografía, "
                "hazlo más profesional pero amigable, mantenlo breve. "
                "Conserva el mismo idioma e intención. "
                "Responde SOLO con el texto mejorado.\n\n"
                f"Original: {text}"
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini] Error mejorando texto: {e}")
            return None

    def transcribe_audio(self, audio_data: bytes) -> str:
        """Usa Gemini para transcribir audio (multimodal)."""
        model = self._get_model()
        if not model or not audio_data:
            return "IA no configurada o audio vacío."
        try:
            # Creamos el contenido para Gemini con los bytes del audio
            # Gemini soporta varios formatos, WhatsApp usa .ogg (opus)
            import base64
            response = model.generate_content([
                "Transcribe exactamente lo que dice este audio de WhatsApp. "
                "Si el audio está en otro idioma, tradúcelo al español.",
                {"mime_type": "audio/ogg", "data": audio_data}
            ])
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini] Error transcribiendo audio: {e}")
            return "Error al procesar el audio con la IA."


gemini = GeminiClient()
