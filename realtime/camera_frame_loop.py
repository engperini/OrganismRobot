import cv2
import time
import asyncio
import json
import base64
import os
from openai import OpenAI

class CameraFrameProvider:
    def __init__(self, camera_index: int = 0):
        # Inicializa a captura da câmera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print("[Camera] Nenhuma câmera encontrada. Verifique a conexão USB.")
            self.cap = None
        
        # Inicializa o cliente OpenAI usando a variável de ambiente OPENAI_API_KEY
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_latest_frame(self):
        if self.cap is None:
            return None
        ret, frame = self.cap.read()
        return frame if ret else None

    def release(self):
        if self.cap:
            self.cap.release()

    def frame_to_base64(self, frame):
        """Converte frame OpenCV em string base64 para a API."""
        # Redimensiona para evitar lentidão e economizar tokens
        frame_resized = cv2.resize(frame, (640, 480))
        _, buffer = cv2.imencode(".jpg", frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode("utf-8")

    def describe_frame(self, frame) -> dict:
        """Usa GPT-4o-mini para descrever a imagem e retorna JSON estruturado."""
        if frame is None:
            return {
                "description": "Visão indisponível.",
                "external_message": "Não consigo ver nada agora.",
                "confidence": 0.0,
            }

        frame_b64 = self.frame_to_base64(frame)

        try:
            # Chamada correta para a API OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é o módulo de visão de um robô. "
                            "Descreva o que vê de forma curta e objetiva. "
                            "Retorne APENAS um JSON válido. "
                            "O campo 'confidence' deve ser obrigatoriamente um NÚMERO entre 0.0 e 1.0."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Descreva o que está diante de você."},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}
                            }
                        ],
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=150
            )

            # --- CORREÇÃO DO ERRO DE LISTA ---
            # Acessamos o primeiro item da lista de escolhas
            content = response.choices[0].message.content
            data = json.loads(content)

            # --- TRATAMENTO SEGURO DA CONFIANÇA ---
            raw_conf = data.get("confidence", 0.5)
            try:
                # Se for número ou string numérica, converte para float
                confidence = float(raw_conf)
            except (ValueError, TypeError):
                # Se for "high", "medium", etc., mapeia para valores
                conf_map = {"high": 0.9, "medium": 0.5, "low": 0.2}
                confidence = conf_map.get(str(raw_conf).lower(), 0.5)

            return {
                "description": data.get("description", "Sem descrição."),
                "external_message": data.get("external_message", "Visão processada."),
                "confidence": confidence,
            }

        except Exception as exc:
            print(f"[ERRO VISÃO] Falha ao descrever frame: {exc}")
            return {
                "description": f"Erro na LLM: {exc}",
                "external_message": "Minha visão falhou.",
                "confidence": 0.0,
            }

# Instância global do provedor
_provider = CameraFrameProvider()

async def capture_frame_summary():
    """Captura o frame e gera o resumo com descrição da IA."""
    frame = _provider.get_latest_frame()
    
    if frame is not None:
        h, w = frame.shape[:2]
        summary = {
            "width": w,
            "height": h,
            "timestamp": time.time(),
        }
        
        # Chama a OpenAI para descrever a imagem
        summary["llm_description"] = _provider.describe_frame(frame)
        
        # Log para monitoramento
        desc = summary["llm_description"]["description"]
        conf = summary["llm_description"]["confidence"]
        print(f"[CameraFrameLoop] Descrição: {desc} (Confiança: {conf:.2f})")
    else:
        summary = {
            "status": "no camera",
            "llm_description": {
                "description": "Câmera offline.",
                "external_message": "Não estou vendo nada.",
                "confidence": 0.0
            }
        }
    
    # Pausa de 10 segundos para não estourar o limite da API
    await asyncio.sleep(60.0)
    return summary
