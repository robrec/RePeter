# Docker Setup für PubKeySearcher

Dieses Dokument beschreibt, wie du den Ed25519 PubKeySearcher mit Docker verwendest.

## Voraussetzungen

- Docker installiert ([Docker Desktop](https://www.docker.com/products/docker-desktop) für Windows/Mac oder Docker Engine für Linux)
- Docker Compose (normalerweise mit Docker Desktop enthalten)

## Quick Start

### 1. Docker Image bauen

```bash
docker-compose build
```

### 2. Container starten

```bash
docker-compose up
```

oder im Hintergrund:

```bash
docker-compose up -d
```

### 3. Logs ansehen (bei Hintergrund-Ausführung)

```bash
docker-compose logs -f
```

### 4. Container stoppen

```bash
docker-compose down
```

oder mit `Strg+C` wenn im Vordergrund.

## Manuelle Docker Befehle (ohne docker-compose)

### Image bauen

```bash
docker build -t pubkey-searcher .
```

### Container ausführen

```bash
docker run -it --rm \
  -v "$(pwd)/found_keys:/app/found_keys" \
  -v "$(pwd)/searchFor.txt:/app/searchFor.txt:ro" \
  pubkey-searcher
```

**Windows PowerShell:**
```powershell
docker run -it --rm `
  -v "${PWD}/found_keys:/app/found_keys" `
  -v "${PWD}/searchFor.txt:/app/searchFor.txt:ro" `
  pubkey-searcher
```

## Konfiguration anpassen

### Patterns ändern

Bearbeite `searchFor.txt` im Host-System. Die Änderungen werden automatisch übernommen (bei aktivem Volume-Mount).

### CPU-Limitierung

Bearbeite `docker-compose.yml` und passe den `cpus` Wert an:

```yaml
cpus: "4.0"  # Begrenzt auf 4 CPU-Kerne
```

### Memory-Limitierung

Füge in `docker-compose.yml` hinzu:

```yaml
mem_limit: 2g  # Begrenzt auf 2GB RAM
```

## Volumes

Das Docker Setup nutzt zwei Volumes:

1. **`./found_keys`** - Persistente Speicherung der gefundenen Keys
2. **`./searchFor.txt`** - Pattern-Liste (read-only)

Alle gefundenen Keys werden direkt auf dem Host-System gespeichert.

## Performance

Der Docker Container nutzt standardmäßig alle verfügbaren CPU-Kerne. Performance sollte vergleichbar mit nativer Ausführung sein.

**Tipp für maximale Performance:**
- Stelle sicher, dass Docker Desktop genügend CPU-Kerne und RAM zugewiesen hat (Einstellungen → Resources)
- Empfohlen: Alle CPU-Kerne und mindestens 2GB RAM

## Troubleshooting

### Container startet nicht

```bash
# Logs prüfen
docker-compose logs

# Container-Status prüfen
docker-compose ps
```

### Keine Keys werden gefunden

Das ist normal und hängt von den Patterns ab. Prüfe die Logs für Progress-Updates.

### Volume-Probleme unter Windows

Stelle sicher, dass:
- Docker Desktop die Berechtigung hat, auf das Verzeichnis zuzugreifen
- Der Pfad korrekt in den Docker-Einstellungen freigegeben ist (File Sharing)

### Permission Errors

Unter Linux kann es zu Permission-Problemen kommen:

```bash
# Berechtigungen anpassen
chmod -R 777 found_keys/
```

## Best Practices

1. **Regelmäßige Backups**: Sichere den `found_keys/` Ordner regelmäßig
2. **Pattern-Optimierung**: Nutze realistische Pattern-Längen (4-6 Zeichen)
3. **Monitoring**: Prüfe regelmäßig die Logs für gefundene Keys
4. **Ressourcen**: Lasse den Container auf einem dedizierten System laufen für beste Performance

## Container im Hintergrund laufen lassen

Für Langzeit-Suche:

```bash
# Starten mit automatischem Neustart
docker-compose up -d --restart unless-stopped

# Status prüfen
docker-compose ps

# Logs live ansehen
docker-compose logs -f

# Stoppen
docker-compose stop
```

## Multi-Container Setup (Optional)

Für parallele Suche mit unterschiedlichen Pattern-Listen:

```yaml
version: '3.8'

services:
  searcher-1:
    build: .
    volumes:
      - ./found_keys:/app/found_keys
      - ./searchFor.txt:/app/searchFor.txt:ro
    cpus: "2.0"
    
  searcher-2:
    build: .
    volumes:
      - ./found_keys:/app/found_keys
      - ./searchFor_long.txt:/app/searchFor.txt:ro
    cpus: "2.0"
```

## Sicherheit

- ⚠️ **Private Keys**: Der `found_keys/` Ordner enthält Private Keys! Sichere Aufbewahrung!
- 🔒 **Backups verschlüsseln**: Nutze verschlüsselte Backups für gefundene Keys
- 🚫 **Nicht exposen**: Exponiere den Container nicht unnötig im Netzwerk

## Support

Bei Problemen prüfe:
1. Docker-Version: `docker --version`
2. Docker Compose-Version: `docker-compose --version`
3. Logs: `docker-compose logs`
4. System-Ressourcen in Docker Desktop Einstellungen
