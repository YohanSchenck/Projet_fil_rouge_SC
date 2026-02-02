# Utilisation d'une image Python légère
FROM python:3.12-slim

# Installation de FFmpeg et des dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Définition du dossier de travail
WORKDIR /app

# Copie du fichier des dépendances
COPY requirements.txt .

# Installation des librairies Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le code de l'application
COPY . .

# Exposition du port utilisé par FastAPI
EXPOSE 8000

# Commande de lancement (Uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]