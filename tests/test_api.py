import pytest


@pytest.mark.asyncio
async def test_read_main(client):
    """Vérifie que la page d'accueil s'affiche bien"""
    response = await client.get("/") # Ajuste selon ton préfixe
    assert response.status_code == 200
    assert "html" in response.headers["content-type"]

@pytest.mark.asyncio
async def test_transcribe_no_file(client):
    """Vérifie que l'envoi sans fichier retourne une erreur"""
    response = await client.post("/transcribe", data={"response_type": "text"})
    assert response.status_code == 422 # Erreur de validation FastAPI
