# Description du projet
Ce projet vise à mettre en place un service de transcription de fichiers audio ou vidéo. L'utilisateur a ainsi la possiblité de récupérer l'audio de l'input en brut (txt ou srt) ou directement inclus dans la vidéo transmise (embedded ou metadata). 

# Configuration minimun requise
Le projet doit être lancé avec les composants suivants (modèle tiny) :
* 6 GB de RAM
* 6 CPUs

# Init et lancement du projet
Il faut au préalable avoir installé docker et docker compose

```
docker compose up --build
```

# Accès aux services 

## Interface Web
La page principale est disponible à l'adresse suivante : **http://localhost:8000**

## Monitoring
Une page Grafana est disponible à cette adresse **http://localhost:3000**.
Identifiants Grafana : (**user : admin** & **mdp : admin**) 

Les metrics Prometheus sont disponibles ici **http://localhost:8000/metrics/**

# Arrêt des services
```
docker compose stop
```

# Arrêt des services et suppression des containers
```
docker compose down -v
```

# Notes pour les utilisateurs
* Le projet utilise une image Faster Whisper basé sur un usage entièrement CPU. Le changement du modèle doit être indiqué dans les fichiers **docker-compose** (image faster whisper) & **_model.py**