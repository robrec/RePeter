# Ed25519 Public Key Pattern Searcher - Dockerfile
FROM python:3.11-slim

# Arbeitsverzeichnis erstellen
WORKDIR /app

# System-Dependencies installieren (falls benötigt für cryptography)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Python Dependencies installieren
RUN pip install --no-cache-dir cryptography base58

# Script und Konfigurationsdateien kopieren
COPY key_searcher.py .
COPY searchFor.txt .

# Erstelle Ordner für gefundene Keys
RUN mkdir -p /app/found_keys

# Volume für persistente Speicherung
VOLUME ["/app/found_keys"]

# Script ausführen
CMD ["python", "-u", "key_searcher.py"]
