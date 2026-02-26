import asyncio

import pytest
from app.services._batcher import transcription_queue


@pytest.mark.asyncio
async def test_queue_insertion():
    """Vérifie que la queue accepte bien les objets et les stocke"""
    # Nettoyage de la queue
    while not transcription_queue.empty():
        transcription_queue.get_nowait()
        
    future = asyncio.get_running_loop().create_future()
    test_data = (b"fake_audio", future, 123456789)
    
    await transcription_queue.put(test_data)
    assert transcription_queue.qsize() == 1
    
    # On récupère pour vérifier le contenu
    item = await transcription_queue.get()
    assert item[0] == b"fake_audio"
