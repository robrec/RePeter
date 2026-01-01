# 🔍 BreMesh MeshCore PubKey Searcher

Ein hochperformantes Python-Script zur Generierung von Ed25519-Schlüsselpaaren mit benutzerdefinierten Public-Key-Präfixen.

Perfekt für einprägsame Keys für **MeshCore** Repeater!

![Interface](interface.png)

## ✨ Features

### Performance

- **Multi-Core Processing** - Nutzt alle verfügbaren CPU-Kerne für maximale Geschwindigkeit
- **Optimierte Schlüsselgenerierung** - Ed25519 Elliptic Curve Kryptographie
- **HEX Format** - MeshCore-kompatibles Format (64-Zeichen HEX Public Key)

### Benutzeroberfläche

- **Rich Live Display** - Flackerfreie Terminal-UI mit dem `rich` Framework
- **Alternate Screen Buffer** - Professionelle Vollbild-Anzeige wie bei `htop`
- **Farbcodierte Anzeige** - Übersichtliche Darstellung aller Statistiken
- **CPU-Auslastungsanzeige** - Grafische Fortschrittsanzeige mit Farbcodierung
- **WoW-Style Seltenheits-Indikatoren** - Farben je nach Pattern-Länge:
  - `•` Grau (#9D9D9D) - ≤5 Zeichen (Poor)
  - `•` Weiß (#FFFFFF) - 6 Zeichen (Common)
  - `•` Grün (#1EFF00) - 7 Zeichen (Uncommon)
  - `✨` Blau (#0070DD) - 8 Zeichen (Rare)
  - `⭐` Lila (#A335EE) - 9 Zeichen (Epic)
  - `⭐💎` Orange (#FF8000) - 10+ Zeichen (Artifact)
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

### Verwaltung

- **Pattern-Datei** - Externe Musterliste für einfache Anpassung
- **Duplikat-Erkennung** - Verhindert doppelte Funde (konfigurierbare Länge)
- **Persistente Speicherung** - Gefundene Keys werden sofort gespeichert
- **JSON-Export** - MeshCore-kompatibles Import-Format

## 📦 Installation

### Voraussetzungen

- Python 3.7+
- pip

### Abhängigkeiten installieren

```bash
pip install cryptography rich psutil
```

## 🚀 Verwendung

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
python key_searcher.py --patterns-file meine_patterns.txt
```

### Alle Optionen

```bash
python key_searcher.py --patterns-file searchFor.txt --max-pattern-length 7 --output-dir found_keys
```

## ⚙️ Konfiguration

### Command Line Argumente

| Argument                 | Beschreibung                             | Standard          |
| ------------------------ | ---------------------------------------- | ----------------- |
| `--pattern`, `-p`    | Einzelnes Pattern suchen (mit Auto-Exit) | -                 |
| `--patterns-file`      | Pfad zur Pattern-Datei                   | `searchFor.txt` |
| `--max-pattern-length` | Max. Länge für Duplikat-Erkennung      | `7`             |
| `--output-dir`         | Ausgabeverzeichnis für gefundene Keys   | `found_keys`    |

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

## 🎮 Bedienung

### Während der Suche

| Taste      | Aktion           |
| ---------- | ---------------- |
| `P`      | Suche pausieren  |
| `R`      | Suche fortsetzen |
| `Ctrl+C` | Suche beenden    |

### Anzeige-Elemente

```
╭──────────────────────── 🔍 BreMesh MeshCore PubKey Searcher ─────────────────────────╮
│                                                                                       │
│   Patterns:  148                              Workers:  16                            │
│   Already Found:  48                                                                  │
│   ────────────────────────────────────────                                            │
│   Status:  ▶ RUNNING                                                                  │
│   Session:  12.5M keys                       All-Time:  151.7M keys                   │
│   Found:  3 matches                          Speed:  42.1k keys/s                     │
│   Duration:  4m 56s                          CPU:  ████████████████████ 100%          │
│                                                                                       │
│   ────────────────────────────────────────                                            │
│   Time Estimates:                            Remaining:  97 patterns                  │
│   5 chars:  26s  (5/7)                       6 chars:  7m  (12/43)                    │
│   7 chars:  1.9h  (28/38)                    8 chars:  1.3d  (2/32)                   │
│   9 chars:  20.3d  (1/19)                    10+ chars:  324.1d  (0/9)                │
│                                                                                       │
│   ────────────────────────────────────────                                            │
│   Found Keys:                                                                         │
│   • B9001            B9001A567890ABCDEF...                                            │
│   • B666666          B666666567890ABCDE...                                            │
│   ✨ B6000000        B6000000567890ABCD...                                            │
│   ⭐ B60000000       B60000000567890ABC...                                            │
│                                                                                       │
╰────────────────────── Ctrl+C to stop • P to pause • R to resume ─────────────────────╯
```

**Legende Time Estimates:** `Zeitschätzung (gefunden/gesucht)`

## 📁 Ausgabe-Format

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

## 📊 Zeitschätzungen

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

## 🔧 Technische Details

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

## 📝 Lizenz

MIT License

## 🤝 Beitragen

Pull Requests sind willkommen! Für größere Änderungen bitte erst ein Issue erstellen.

---

**Viel Erfolg bei der Suche nach dem perfekten Key! 🔑**
