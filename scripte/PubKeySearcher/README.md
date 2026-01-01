# Ed25519 Public Key Pattern Searcher

Ein Python-Script für **MeshCore**, das mit allen verfügbaren CPU-Kernen nach ed25519 Public Keys mit speziellen Patterns am Anfang sucht. Ziel ist es, eindeutige und leicht erkennbare Keys für Repeater zu generieren, um Verwechslungen zu vermeiden.

## Features

- Multi-Core Processing für maximale Performance
- Sucht nach benutzerdefinierten Patterns am Anfang des Public Keys (Base58)
- Automatisches Speichern von gefundenen Key-Paaren
- Duplikat-Vermeidung: Patterns bis 7 Zeichen werden nur 1x gespeichert (konfigurierbar)
- Live-Statistiken während der Suche mit Session-Tracking
- Anzeige gefundener Patterns in der aktuellen Session
- **Docker-Support**: Einfache Containerisierung für portables Deployment

## Installation

### Option 1: Docker (empfohlen)

**Vorteile:**

- ✅ Keine lokale Python-Installation nötig
- ✅ Isolierte Umgebung
- ✅ Portabel auf jedem System (Windows, Linux, macOS)
- ✅ Einfaches Deployment auf Servern
- ✅ Automatische Dependency-Verwaltung

**Voraussetzungen:**

- Docker & Docker Compose installiert

**Quick Start:**

```bash
docker-compose up
```

📖 **Vollständige Docker-Dokumentation:** [DOCKER.md](DOCKER.md)

### Option 2: Python (lokal)

**Voraussetzungen:**

- Python 3.7 oder höher
- pip (Python Package Manager)

**Dependencies installieren:**

```bash
pip install cryptography base58
```

## Verwendung

### 1. Patterns definieren

Bearbeite die Datei `searchFor.txt` und füge die gewünschten Patterns hinzu (ein Pattern pro Zeile).

Beispiel:

```
AAAAAA
DEADBEEF
123456
CAFE
D0000000
```

Die mitgelieferte Liste enthält bereits viele interessante Patterns!

### 2. Script starten

**Python (direkt):**

```bash
python key_searcher.py
```

**Mit Optionen:**

```bash
# Duplikat-Grenze auf 10 Zeichen setzen
python key_searcher.py --max-pattern-length 10

# Andere Pattern-Datei verwenden
python key_searcher.py --patterns-file custom_patterns.txt

# Hilfe anzeigen
python key_searcher.py --help
```

**Docker:**

```bash
# Container starten
docker-compose up

# Im Hintergrund
docker-compose up -d

# Logs ansehen
docker-compose logs -f
```

👉 **Mehr Docker-Optionen:** Siehe [DOCKER.md](DOCKER.md) für erweiterte Konfiguration, CPU/Memory-Limits, Multi-Container-Setup, etc.

Das Script nutzt automatisch alle verfügbaren CPU-Kerne.

#### Konfiguration

**Environment Variable (Docker):**

In `docker-compose.yml`:

```yaml
environment:
  - MAX_PATTERN_LENGTH=10  # Patterns bis 10 Zeichen nur 1x speichern
```

**Command-Line Arguments (Python):**

- `--max-pattern-length N` - Maximale Pattern-Länge für Duplikat-Vermeidung (Standard: 7)
- `--patterns-file FILE` - Pfad zur Pattern-Datei (Standard: searchFor.txt)
- `--output-dir DIR` - Ausgabe-Verzeichnis (Standard: found_keys)

### 3. Script beenden

Drücke `Strg+C` um die Suche zu beenden. Alle bereits gefundenen Keys bleiben gespeichert.

## Ausgabe

Gefundene Keys werden im Ordner `found_keys/` gespeichert mit folgendem Format:

- **Dateiname**: `{EPOCH}_{PATTERN}.txt` (z.B. `1735700000_CAFE.txt`)
- **Inhalt**: Private Key (PEM), Public Key (PEM), Public Key (Base58)

**Public Key Format**: Der Base58-encodierte Public Key ist der Schlüssel, den Sie verteilen!

```
Beispiel: CAFEM37BEuiceCLzuduYBHiYTsjfWSTaCtYdnas5JGkV
```

**⚠️ WICHTIG:** Die Private Keys sind NICHT verschlüsselt! Halte diese Dateien sicher und teile sie nicht!

## Duplikat-Vermeidung

Das Script erkennt automatisch bereits gefundene Patterns (bis 7 Zeichen, konfigurierbar) im `found_keys/` Ordner:

- Beim Start werden alle vorhandenen Dateien gescannt
- Bereits gefundene Patterns werden übersprungen
- Nur neue Patterns werden gesucht und gespeichert

**Beispiel-Output beim Start:**

```
Bereits gefunden (werden übersprungen): 9
  -> 1337, ACAB, BABE, BEEF, CAFE, DEAD, DEED, FADE, FEED
```

## Live-Statistiken

Während der Suche zeigt das Script detaillierte Fortschritts-Updates:

```
Worker 0: 300,000 Keys geprüft | Total: 1,200,000 | Gefunden: 3 | Session: [ABC123, C0DED, FACE]
```

**Anzeige-Elemente:**
- **Worker N**: Welcher CPU-Kern arbeitet
- **Keys geprüft**: Anzahl der von diesem Worker geprüften Keys
- **Total**: Gesamtanzahl aller geprüften Keys (alle Worker)
- **Gefunden**: Anzahl gefundener Matches in dieser Session
- **Session**: Liste der in dieser Session gefundenen Patterns (alphabetisch sortiert)

**Bei Session-Ende:**
```
======================================================================
Suche beendet!
Geprüfte Keys: 5,234,567
Gefundene Matches: 5
Gefundene Patterns in dieser Session: BABE, C0DE, DEAD, FACE, FEED
======================================================================
```

## Performance

Die Geschwindigkeit hängt von deiner CPU ab. Typische Werte:

- 4 Cores: ~100.000 - 150.000 Keys/Sekunde
- 8 Cores: ~200.000 - 300.000 Keys/Sekunde
- 16 Cores: ~400.000 - 600.000 Keys/Sekunde

**Hinweis:** Je länger das Pattern, desto seltener wird ein Match gefunden!

**Beispiel-Suche:**
- 1 Million Keys in ~10 Sekunden (4 Cores)
- Patterns mit 4 Zeichen: Durchschnittlich 1 Match pro ~10-20 Millionen Keys
- Patterns mit 6 Zeichen: Sehr selten, kann Stunden bis Tage dauern

## Wahrscheinlichkeiten

Die Wahrscheinlichkeit, ein Pattern zu finden (Base58-Alphabet hat 58 Zeichen):

- 4 Zeichen (z.B. DEAD): ~1 zu 11,3 Millionen
- 6 Zeichen (z.B. AAAAAA): ~1 zu 38 Milliarden
- 8 Zeichen (z.B. DEADBEEF): ~1 zu 128 Billionen

**Tipp:** Kürzere Patterns (4-7 Zeichen) sind realistisch zu finden!

## MeshCore Integration

Diese Keys werden für **MeshCore Repeater** verwendet, um:

- Eindeutige Identifikation zu gewährleisten
- Verwechslungen zu vermeiden
- Leicht erkennbare und einprägsame Adressen zu haben

Der Base58-Public-Key kann direkt als Repeater-Identifikator verwendet werden.

### Private Key in MeshCore Repeater einrichten

Um einen gefundenen Private Key in einem MeshCore Repeater zu verwenden:

1. **Repeater via USB verbinden**
2. **CLI Console öffnen** (z.B. über Serial Monitor, PuTTY, oder die MeshCore Console)
3. **Private Key setzen** mit dem Befehl:

   ```
   set prv.key <PRIVATE_KEY>
   ```

   Dabei ist `<PRIVATE_KEY>` der Private Key aus der generierten Datei (ohne PEM-Header/Footer, nur der Base64-Teil oder je nach MeshCore-Format).
4. **Repeater neustarten**, damit die Änderungen wirksam werden

**Beispiel:**

```bash
set prv.key MC4CAQAwBQYDK2VwBCIEINO1JWgy+o2iLVy+mZZaVqewr/YKZZbVxOBaHP44t0cX
```

**Hinweis:** Der Public Key wird automatisch aus dem Private Key abgeleitet und sollte dann mit dem gewünschten Pattern beginnen (z.B. `CAFE...`).

## Sicherheitshinweise

⚠️ **Private Keys sicher aufbewahren!**

- Niemals Private Keys in öffentliche Repositories hochladen
- Die `.gitignore` ist bereits so konfiguriert, dass `found_keys/` ausgeschlossen wird
- Private Keys mit starkem Passwort verschlüsseln, wenn sie langfristig gespeichert werden
- Backup der Keys an sicherem Ort aufbewahren

## Technische Details

- **Algorithmus**: Ed25519 (Elliptic Curve Digital Signature Algorithm)
- **Key-Länge**: 256 Bit (32 Bytes)
- **Public Key Format**: Base58-Encoding (wie Bitcoin/Solana)
- **Public Key Länge**: ~44 Zeichen in Base58
- **Multiprocessing**: Nutzt Python's `multiprocessing` Modul
- **Dateiformat**: Epoch-Timestamp für chronologische Sortierung

## Dateistruktur

```
PubKeySearcher/
├── key_searcher.py      # Haupt-Script
├── searchFor.txt        # Pattern-Liste
├── .gitignore          # Git-Schutz für Keys
├── README.md           # Diese Dokumentation
└── found_keys/         # Gefundene Keys (nicht in Git)
    ├── 1735700000_CAFE.txt
    ├── 1735700123_DEAD.txt
    └── ...
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'cryptography'" oder "'base58'"

Installiere die benötigten Libraries:

```bash
pip install cryptography base58
```

### Script ist langsam

- Überprüfe, ob alle CPU-Kerne genutzt werden (Task Manager / htop)
- Kürzere Patterns haben höhere Erfolgsraten
- Moderne CPUs mit mehr Kernen sind schneller

### Keine Matches gefunden

Das ist normal! Abhängig vom Pattern kann es Stunden oder Tage dauern, bis ein Match gefunden wird.

**Empfehlung:** Starte mit 4-6 Zeichen langen Patterns für realistische Erfolgschancen.

### PEM-Key beginnt nicht mit Pattern

Das ist korrekt! Der **Base58-Public-Key** (nicht das PEM-Format) beginnt mit dem Pattern. Das PEM-Format enthält zusätzliche Metadaten und ist für andere Zwecke gedacht.

## Lizenz

Dieses Script ist für persönliche und Bildungszwecke sowie für MeshCore gedacht.
