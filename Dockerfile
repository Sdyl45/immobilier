# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système requises
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Commande par défaut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]