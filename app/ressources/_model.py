import logging

import httpx


class ModelClient:
    # 1. MISE À JOUR : Le endpoint pointe vers le Load Balancer défini dans docker-compose
    def __init__(self, endpoint: str = "http://inference-lb:80/v1/audio/transcriptions"):
        self.endpoint = endpoint

    async def get_script_transcription_remote(self, audio_bytes: bytes):
        """
        Envoie l'audio au Load Balancer qui distribue vers les workers Faster-Whisper.
        """
        # On garde le timeout à None pour le 'read' car la transcription CPU est longue
        timeout = httpx.Timeout(connect=10.0, read=None, write=60.0, pool=None)

        async with httpx.AsyncClient(timeout=timeout) as client:
            files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
            
            # 2. MISE À JOUR : 'model' doit correspondre à ce que Faster-Whisper attend
            # Souvent, faster-whisper-server accepte n'importe quelle chaîne ou 'distil-small'
            data = {
                'model': 'small', 
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
