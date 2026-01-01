# BreMesh MeshCore Ed25519 PubKey Prefix Searcher

Ein hochperformantes Python-Script zur Generierung von Ed25519-Schlüsselpaaren mit benutzerdefinierten Public-Key-Präfixen.

Perfekt für einprägsame Keys für **MeshCore** Repeater!

## Empfehlung für einfache Keys

**Für einfache, einzelne Keys empfehle ich:** [https://gessaman.com/mc-keygen/](https://gessaman.com/mc-keygen/)

Diese Website ist perfekt für schnelle, unkomplizierte Key-Generierung und ich lege sie jedem ans Herz. Tatsächlich war diese Seite meine Inspiration für dieses Tool - ich wollte eine Möglichkeit schaffen, **mehrere komplexere Keys gleichzeitig zu suchen**, um Ressourcen zu schonen und Zeit zu sparen, wenn man mehrere Repeater mit benutzerdefinierten Patterns konfigurieren möchte.

**GitHub:** [https://github.com/agessaman/meshcore-web-keygen](https://github.com/agessaman/meshcore-web-keygen)

**Verwenden Sie dieses Tool, wenn:**

- Sie mehrere Keys mit unterschiedlichen Patterns gleichzeitig suchen möchten
- Sie komplexere/längere Patterns (7+ Zeichen) benötigen
- Sie eine Pattern-Liste haben und alle Keys in einem Durchgang generieren möchten
- Sie die volle CPU-Power Ihres Systems nutzen möchten

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
- **CPU-Limitierung** - Mit `L` CPU auf ~75% limitieren (pausiert 25% der Worker)
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
- **Per-Length ETAs** - Einzelne ETA-Timer pro Pattern-Länge (5-10, 11+ in Rot)
- **Session Progress** - Zeigt gefundene vs. erwartete Keys (z.B. `1 / 1.4`)
- **Verbose Mode** - Zeigt die ETA-Berechnungsformel mit `-v` Flag

### Verwaltung

- **Pattern-Datei** - Externe Musterliste für einfache Anpassung
- **Hot-Reload** - Pattern-Datei wird alle 30 Sekunden neu geladen (neue Patterns werden automatisch hinzugefügt)
- **Duplikat-Erkennung** - Verhindert doppelte Funde für kurze Patterns (konfigurierbar via `--max-pattern-length`)
- **No Dup Cap** - Patterns oberhalb der max-pattern-length können beliebig oft gefunden werden
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

| Argument                    | Beschreibung                             | Standard          |
| --------------------------- | ---------------------------------------- | ----------------- |
| `--pattern`, `-p`       | Einzelnes Pattern suchen (mit Auto-Exit) | -                 |
| `--patterns-file`, `-f` | Pfad zur Pattern-Datei                   | `searchFor.txt` |
| `--max-pattern-length`    | Max. Länge für Duplikat-Erkennung      | `7`             |
| `--output-dir`            | Ausgabeverzeichnis für gefundene Keys   | `found_keys`    |
| `--verbose`, `-v`       | Zeigt ETA-Berechnungsformel an           | -                 |

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

| Taste      | Aktion                                         |
| ---------- | ---------------------------------------------- |
| `P`      | Suche pausieren                                |
| `R`      | Suche fortsetzen                               |
| `L`      | CPU limitieren (~75%, pausiert 25% der Worker) |
| `Ctrl+C` | Suche beenden                                  |

### Anzeige-Elemente

Das Interface besteht aus drei separaten Panels:

1. **Hauptstatistiken (blauer Rahmen)** - Config, Patterns, No Dup Cap, Status, Session/All-Time Stats, Time Estimates
2. **ETA Progressbar (magenta Rahmen)** - Expected/Elapsed Zeit, Session Progress, Per-Length ETAs, Fortschrittsbalken
3. **Found Keys (gruener Rahmen)** - Gefundene Keys mit vollstaendigem 64-Zeichen Public Key

![Interface](interface.png)

**Legende:**

- **No Dup Cap:** Zeigt ab welcher Pattern-Laenge Mehrfach-Funde erlaubt sind
- **Workers:** Zeigt Anzahl der aktiven Worker, bei CPU-Limit: `4 (Limit: 3)`
- **Status:** Zeigt RUNNING/PAUSED, bei CPU-Limit zusaetzlich: `(CPU ~75%)`
- **Time Estimates:** `Zeitschaetzung (gefunden/gesucht)` pro Laengen-Kategorie
- **Session:** Zeigt `gefunden / erwartet` Keys in der aktuellen Session
- **Per-Length ETAs:** Einzelne ETA-Timer fuer jede Pattern-Laenge in Rarity-Farben:
  - Grau: 5 Zeichen oder weniger
  - Weiss: 6 Zeichen
  - Gruen: 7 Zeichen
  - Blau: 8 Zeichen
  - Lila: 9 Zeichen
  - Orange: 10 Zeichen
  - Rot: 11+ Zeichen
- **Next Key ETA:** Mathematisch erwartete Zeit bis zum naechsten Fund basierend auf kombinierter Wahrscheinlichkeit:
  ```
  ETA = 1 / ((n1/16^L1 + n2/16^L2 + ...) x keys_per_sec)
  ```
- **Progressbar:** Zeigt verstrichene Zeit im Verhaeltnis zur erwarteten Zeit
  - Cyan (<50%): unterwegs
  - Gelb (50-100%): bald erwartet
  - Gruen (>100%): ueberfaellig - Fund sollte bald kommen

## Ausgabe-Format

Gefundene Keys werden im Verzeichnis `found_keys/` gespeichert:

### Dateiname

```
{pattern}_1.txt
{pattern}_2.txt  (bei Duplikaten für Patterns >7 Zeichen)
```

Beispiel: `CAFE_1.txt`, `BREMESH_1.txt`, `BREMESH_2.txt`

### Dateiinhalt

```
Pattern Match: CAFE
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

Die generierten Key-Dateien enthalten zusätzlich detaillierte Konfigurationsanweisungen für Ihren Repeater.

## Keys auf dem Repeater konfigurieren

Nach der erfolgreichen Generierung eines Keys mit Ihrem gewünschten Pattern müssen Sie diesen auf Ihrem MeshCore Repeater konfigurieren.

### Methode: USB Serial Console (Empfohlen)

Dies ist die schnellste Methode, wenn Sie Ihren Repeater direkt mit einem Computer verbinden können:

#### Schritt 1: USB-Verbindung herstellen

Verbinden Sie Ihren Repeater über USB mit Ihrem Computer.

#### Schritt 2: Console öffnen

Öffnen Sie die MeshCore Web Console oder verwenden Sie eine beliebige Terminal-Anwendung:

- **Web Console**: Besuchen Sie [flasher.meshcore.co.uk](https://flasher.meshcore.co.uk)
- **Terminal**: Verwenden Sie PuTTY, screen, oder ein anderes Serial-Terminal-Programm

#### Schritt 3: Private Key setzen

Führen Sie folgenden Befehl in der Console aus:

```
set prv.key <IHR_128_ZEICHEN_PRIVATE_KEY>
```

Ersetzen Sie `<IHR_128_ZEICHEN_PRIVATE_KEY>` mit dem vollständigen 128-Zeichen Private Key aus Ihrer generierten Key-Datei.

**Wichtig:** Verwenden Sie den kompletten 128-Zeichen Private Key. Der Befehl ändert den Private Key des Geräts sofort.

#### Schritt 4: Änderung verifizieren

Überprüfen Sie die Änderung, indem Sie den Public Key in den Geräteeinstellungen kontrollieren:

- Die ersten Zeichen sollten Ihrem gewünschten Pattern entsprechen
- Der vollständige Public Key sollte mit dem generierten Key übereinstimmen

### Vorteile der Serial Console Methode

- Keine Companion-Firmware erforderlich
- Änderung erfolgt sofort ohne Firmware-Wechsel
- Schnell und unkompliziert bei Console-Erfahrung
- Funktioniert mit MeshCore Web Console oder jedem Terminal-Programm

### Troubleshooting

**Häufige Probleme:**

- **Key wird nicht angezeigt**: Stellen Sie sicher, dass Sie die Änderung gespeichert haben
- **Falsches Key-Format**: Verwenden Sie den kompletten 128-Zeichen Private Key
- **App erkennt Gerät nicht**: USB-Kabel ab- und wieder anstecken
- **Firmware-Flash schlägt fehl**: Anderes USB-Kabel oder USB-Port versuchen
- **Key-Import schlägt fehl**: Key-Generierung überprüfen und erneut versuchen

**Verifizierungsschritte:**

1. Prüfen Sie, dass der angezeigte Public Key mit Ihrem generierten Key übereinstimmt
2. Verifizieren Sie, dass die ersten Zeichen Ihrem gewünschten Pattern entsprechen
3. Testen Sie die Verbindung, um sicherzustellen, dass das Gerät funktioniert
4. Überprüfen Sie im MeshCore-Netzwerk, ob Ihr Gerät mit der neuen Kennung sichtbar ist

**Pro-Tipp:** Bewahren Sie eine Sicherungskopie Ihres Private Keys an einem sicheren Ort auf. Sie benötigen ihn, falls Sie Ihre Gerätekonfiguration wiederherstellen müssen.

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
- **Worker-Management** - CPU-Limitierung durch selektives Pausieren von Workern
- **Shared Memory** - Gemeinsame Zähler für alle Worker
- **Queue-basierte Kommunikation** - Worker zu Display-Prozess
- **Event-basierte Steuerung** - Synchronisierte Pause und CPU-Limitierung über alle Worker

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

Viel Erfolg bei der Suche nach dem perfekten Key!
