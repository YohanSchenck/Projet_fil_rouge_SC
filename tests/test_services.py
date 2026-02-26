import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from app.schemas.enums import ResponseType
from app.services._transcription import transcription_service


@pytest.mark.asyncio
async def test_transcription_to_srt_flow():
    fake_whisper_json = {
        "text": "Ceci est un test.",
        "segments": [{"start": 0.0, "end": 2.0, "text": "Ceci est un test."}]
    }

    # On mock l'extraction audio et l'insertion dans la queue
    with patch("app.services._transcription.run_in_threadpool") as mock_threadpool, \
         patch("app.services._transcription.transcription_queue.put") as mock_put:
        
        mock_threadpool.return_value = (b"fake_wav_data", 2.0)

        # ASTUCE : Quand le service appelle queue.put, on intercepte le Future
        # et on lui donne immédiatement le résultat fake_whisper_json
        async def side_effect(item):
            audio, future, timestamp = item
            future.set_result(fake_whisper_json) # On débloque le 'await future'
        
        mock_put.side_effect = side_effect

        # Appel du service
        content, mime, filename = await transcription_service(
            file_bytes=b"anything",
            file_name="test_video",
            response_type=ResponseType.SRT
        )

        # Vérifications
        assert mime == "application/x-subrip"
        assert "00:00:00,000 --> 00:00:02,000" in content.decode()
        assert "Ceci est un test" in content.decode()
