import logging

import httpx


class ModelClient:
    def __init__(self, endpoint: str = "http://inference-worker:8000/v1/audio/transcriptions"):
        self.endpoint = endpoint

    async def get_script_transcription_remote(self, audio_bytes: bytes):
        """
        Envoie l'audio au Load Balancer qui distribue vers les workers Faster-Whisper.
        """
        timeout = httpx.Timeout(connect=10.0, read=300.0, write=60.0, pool=None)

        async with httpx.AsyncClient(timeout=timeout) as client:
            files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
            
            data = {
                'model': 'tiny', 
                'response_format': 'verbose_json',
                'temperature': '0.0'
            }
            
            try:
                response = await client.post(
                    self.endpoint, 
                    files=files, 
                    data=data
                )
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                logging.error(f"Erreur serveur d'inférence ({e.response.status_code}): {e.response.text}")
                raise
            except httpx.RequestError as e:
                logging.error(f"Erreur de communication avec le Load Balancer: {e}")
                raise
