import asyncio
import logging
import time

from app.ressources import ModelClient

# UNE SEULE INSTANCE ICI
transcription_queue = asyncio.Queue()

async def batch_processor():
    logging.info("🚀 Batch Processor : Démarrage du worker...")
    client = ModelClient()
    BATCH_WINDOW = 5  
    MAX_BATCH_SIZE = 2  

    while True:
        # 1. On attend la première tâche
        item = await transcription_queue.get()
        audio_bytes, future, start_time = item
        batch = [item]
        
        logging.info(f"📥 Première tâche reçue. Attente de {BATCH_WINDOW}s pour grouper...")

        # 2. Accumulation
        deadline = asyncio.get_event_loop().time() + BATCH_WINDOW
        try:
            while len(batch) < MAX_BATCH_SIZE:
                timeout = deadline - asyncio.get_event_loop().time()
                if timeout <= 0:
                    break
                # On essaie de prendre les suivantes
                extra_item = await asyncio.wait_for(transcription_queue.get(), timeout=timeout)
                batch.append(extra_item)
        except asyncio.TimeoutError:
            pass # C'est normal, la fenêtre de temps est finie

        logging.info(f"📦 Batch formé : {len(batch)} fichiers. Envoi à Whisper...")

        # 3. Exécution parallèle
        tasks = [client.get_script_transcription_remote(b[0]) for b in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 4. Libération des "Futures"
        for i, result in enumerate(results):
            _, fut, _ = batch[i]
            if not fut.done():
                if isinstance(result, Exception):
                    fut.set_exception(result)
                else:
                    fut.set_result(result)
            # Indiquer à la queue que l'item est traité
            transcription_queue.task_done()
