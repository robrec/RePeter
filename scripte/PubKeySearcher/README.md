# BreMesh MeshCore PubKey Searcher

Ein hochperformantes Python-Script zur Generierung von Ed25519-Schlüsselpaaren mit benutzerdefinierten Public-Key-Präfixen.

Perfekt für einprägsame Keys für **MeshCore** Repeater!

![Interface](interface.png)

## Features

### Performance

- **Multi-Core Processing** - Nutzt alle verfügbaren CPU-Kerne für maximale Geschwindigkeit
- **Optimierte Schlüsselgenerierung** - Ed25519 Elliptic Curve Kryptographie
- **HEX Format** - MeshCore-kompatibles Format (64-Zeichen HEX Public Key)

### Benutzeroberfläche

- **Rich Live Display** - Flackerfreie Terminal-UI mit dem `rich` Framework
- **Alternate Screen Buffer** - Professionelle Vollbild-Anzeige wie bei `htop`
- **Drei-Panel-Layout** - Hauptstatistiken, ETA-Progressbar, gefundene Keys
- **Farbcodierte Anzeige** - Übersichtliche Darstellung aller Statistiken
- **CPU-Auslastungsanzeige** - Grafische Fortschrittsanzeige mit Farbcodierung
- **Seltenheits-Indikatoren** - Farbige Markierung je nach Pattern-Länge
- **Fortschrittsanzeige** - Zeigt gefundene/gesuchte Patterns pro Längen-Kategorie

### Steuerung

- **Pause/Resume** - Mit `P` pausieren, mit `R` fortsetzen
- **Graceful Shutdown** - Sauberes Beenden mit `Ctrl+C` und Zusammenfassung
- **Tastatur-Listener** - Reagiert auf Eingaben während der Suche
- **Single Pattern Mode** - Suche nach einzelnem Pattern mit Auto-Exit bei Fund

### Statistiken

- **Live-Statistiken** - Echtzeit-Anzeige von Fortschritt und Geschwindigkeit
- **Session-Stats** - Aktuelle Sitzung: Geprüfte Keys, gefundene Matches, Laufzeit
- **All-Time-Stats** - Gesamtzahl geprüfter Keys über alle Sessions (persistent)
- **Zeitschätzungen** - Berechnete Wahrscheinlichkeiten mit Fortschritt (gefunden/gesucht)
- **Remaining Counter** - Zeigt verbleibende Patterns insgesamt und pro Kategorie
- **Next Key ETA** - Mathematische Schätzung bis zum nächsten Fund mit dynamischem Progressbar
- **Verbose Mode** - Zeigt die ETA-Berechnungsformel mit `-v` Flag

### Verwaltung

- **Pattern-Datei** - Externe Musterliste für einfache Anpassung
- **Duplikat-Erkennung** - Verhindert doppelte Funde für kurze Patterns (≤7 Zeichen)
- **Mehrfach-Funde** - Patterns >7 Zeichen können beliebig oft gefunden werden
- **Persistente Speicherung** - Gefundene Keys werden sofort gespeichert
- **JSON-Export** - MeshCore-kompatibles Import-Format

## Installation

### Voraussetzungen

- Python 3.7+
- pip

### Abhängigkeiten installieren

```bash
pip install cryptography rich psutil
```

## Verwendung

### Schnellstart

```bash
python key_searcher.py
```

### Einzelnes Pattern suchen (mit Auto-Exit)

```bash
python key_searcher.py --pattern CAFE
# oder kurz:
python key_searcher.py -p BREMESH
```

Das Script beendet sich automatisch sobald das Pattern gefunden wurde.

### Mit eigener Pattern-Datei

```bash
python key_searcher.py -f meine_patterns.txt
# oder:
python key_searcher.py --patterns-file meine_patterns.txt
```

### Mit ETA-Formel (Verbose Mode)

```bash
python key_searcher.py -v
```

### Alle Optionen

```bash
python key_searcher.py -f searchFor.txt --max-pattern-length 7 --output-dir found_keys -v
```

## Konfiguration

### Command Line Argumente

| Argument                 | Beschreibung                             | Standard          |
| ------------------------ | ---------------------------------------- | ----------------- |
| `--pattern`, `-p`        | Einzelnes Pattern suchen (mit Auto-Exit) | -                 |
| `--patterns-file`, `-f`  | Pfad zur Pattern-Datei                   | `searchFor.txt`   |
| `--max-pattern-length`   | Max. Länge für Duplikat-Erkennung        | `7`               |
| `--output-dir`           | Ausgabeverzeichnis für gefundene Keys    | `found_keys`      |
| `--verbose`, `-v`        | Zeigt ETA-Berechnungsformel an           | -                 |

### Umgebungsvariablen

Alternativ per Umgebungsvariablen konfigurierbar:

**Windows PowerShell:**

```powershell
$env:PATTERNS_FILE = "custom_patterns.txt"
$env:MAX_PATTERN_LENGTH = 8
python key_searcher.py
```

**Linux/Mac:**

```bash
export PATTERNS_FILE=custom_patterns.txt
export MAX_PATTERN_LENGTH=8
python key_searcher.py
```

### Pattern-Datei erstellen

Erstelle eine Textdatei mit einem Pattern pro Zeile:

```
CAFE
DEAD
BEEF
1234
ABCD
BREMESH
```

**Hinweise:**

- Nur HEX-Zeichen erlaubt: `0-9` und `A-F`
- Groß-/Kleinschreibung wird ignoriert
- Zeilen mit `#` sind Kommentare
- Leere Zeilen werden ignoriert

## Bedienung

### Während der Suche

| Taste      | Aktion           |
| ---------- | ---------------- |
| `P`      | Suche pausieren  |
| `R`      | Suche fortsetzen |
| `Ctrl+C` | Suche beenden    |

### Anzeige-Elemente

Das Interface besteht aus drei separaten Panels:

1. **Hauptstatistiken (blauer Rahmen)** - Config, Patterns, Status, Session/All-Time Stats, Time Estimates
2. **ETA Progressbar (magenta Rahmen)** - Expected/Elapsed Zeit mit dynamischem Fortschrittsbalken
3. **Found Keys (grüner Rahmen)** - Gefundene Keys mit vollständigem 64-Zeichen Public Key

![Interface](interface.png)

**Legende:**
- **Time Estimates:** `Zeitschätzung (gefunden/gesucht)` pro Längen-Kategorie
- **Next Key ETA:** Mathematisch erwartete Zeit bis zum nächsten Fund basierend auf kombinierter Wahrscheinlichkeit:
  ```
  ETA = 1 / ((n1/16^L1 + n2/16^L2 + ...) × keys_per_sec)
  ```
- **Progressbar:** Zeigt verstrichene Zeit im Verhältnis zur erwarteten Zeit
  - Cyan (<50%): unterwegs
  - Gelb (50-100%): bald erwartet
  - Grün (>100% oder negativ): überfällig oder früher Fund
- **Credits System:** Bei jedem gefundenen Key wird der Fortschritt um 100% reduziert
  - Progress kann negativ werden (Key früher als erwartet gefunden)
  - Progress >100% bedeutet überfällig

## Ausgabe-Format

Gefundene Keys werden im Verzeichnis `found_keys/` gespeichert:

### Dateiname

```
{timestamp}_{pattern}.txt
```

Beispiel: `1735689600_CAFE.txt`

### Dateiinhalt

```
Pattern Match: CAFE
Timestamp: 2026-01-01T12:00:00
Public Key (HEX): CAFE1234567890ABCDEF...
Private Key (HEX): ABCDEF1234567890...

======================================================================
MeshCore Import Format:
======================================================================

{
  "public_key": "CAFE1234567890ABCDEF...",
  "private_key": "ABCDEF1234567890..."
}
```

## Zeitschätzungen

Die Wahrscheinlichkeit, ein bestimmtes Präfix zu finden:

| Präfix-Länge | Möglichkeiten    | Bei 30k keys/s |
| -------------- | ----------------- | -------------- |
| 4 Zeichen      | 65.536            | ~2 Sekunden    |
| 5 Zeichen      | 1.048.576         | ~35 Sekunden   |
| 6 Zeichen      | 16.777.216        | ~9 Minuten     |
| 7 Zeichen      | 268.435.456       | ~2,5 Stunden   |
| 8 Zeichen      | 4.294.967.296     | ~1,7 Tage      |
| 9 Zeichen      | 68.719.476.736    | ~26 Tage       |
| 10 Zeichen     | 1.099.511.627.776 | ~1,2 Jahre     |

## Technische Details

### Architektur

- **Multiprocessing** - Ein Worker-Prozess pro CPU-Kern
- **Shared Memory** - Gemeinsame Zähler für alle Worker
- **Queue-basierte Kommunikation** - Worker → Display-Prozess
- **Event-basierte Pause** - Synchronisierte Pause über alle Worker

### Dateien

- `key_searcher.py` - Hauptscript
- `searchFor.txt` - Standard Pattern-Datei
- `.total_stats.json` - Persistente All-Time-Statistiken
- `found_keys/` - Ausgabeverzeichnis

### Abhängigkeiten

- `cryptography` - Ed25519 Schlüsselgenerierung
- `rich` - Terminal-UI Framework
- `psutil` - CPU-Auslastung

## Lizenz

MIT License

## Beitragen

Pull Requests sind willkommen! Für größere Änderungen bitte erst ein Issue erstellen.

---

**Viel Erfolg bei der Suche nach dem perfekten Key!**
