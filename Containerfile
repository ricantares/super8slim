# Usa l'immagine slim di Python 3.15
FROM python:3.15-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il file requirements.txt nel container
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Il codice sorgente NON viene copiato:
# verrà montato da Windows tramite bind mount
