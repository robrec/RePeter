# Ed25519 Public Key Pattern Searcher

Ein Python-Script für **MeshCore**, das mit allen verfügbaren CPU-Kernen nach ed25519 Public Keys mit speziellen Patterns am Anfang sucht. Ziel ist es, eindeutige und leicht erkennbare Keys für Repeater zu generieren, um Verwechslungen zu vermeiden.

## Features

- Multi-Core Processing für maximale Performance
- Sucht nach benutzerdefinierten Patterns am Anfang des Public Keys (Base58)
- Automatisches Speichern von gefundenen Key-Paaren
- Intelligente Duplikat-Vermeidung: Patterns bis 6 Zeichen werden nur 1x gespeichert
- Live-Statistiken während der Suche
- Sicheres Speichern von Private und Public Keys
- Epoch-Timestamp für chronologische Sortierung

## Installation

### Voraussetzungen

- Python 3.7 oder höher
- pip (Python Package Manager)

### Dependencies installieren

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

```bash
python key_searcher.py
```

Das Script nutzt automatisch alle verfügbaren CPU-Kerne.

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

Das Script erkennt automatisch bereits gefundene Patterns (bis 6 Zeichen) im `found_keys/` Ordner:

- Beim Start werden alle vorhandenen Dateien gescannt
- Bereits gefundene Patterns werden übersprungen
- Nur neue Patterns werden gesucht und gespeichert

**Beispiel-Output beim Start:**

```
Bereits gefunden (werden übersprungen): 9
  -> 1337, ACAB, BABE, BEEF, CAFE, DEAD, DEED, FADE, FEED
```

## Performance

Die Geschwindigkeit hängt von deiner CPU ab. Typische Werte:

- 4 Cores: ~40.000 - 60.000 Keys/Sekunde
- 8 Cores: ~80.000 - 120.000 Keys/Sekunde
- 16 Cores: ~160.000 - 240.000 Keys/Sekunde

**Hinweis:** Je länger das Pattern, desto seltener wird ein Match gefunden!

## Wahrscheinlichkeiten

Die Wahrscheinlichkeit, ein Pattern zu finden (Base58-Alphabet hat 58 Zeichen):

- 4 Zeichen (z.B. DEAD): ~1 zu 11,3 Millionen
- 6 Zeichen (z.B. AAAAAA): ~1 zu 38 Milliarden
- 8 Zeichen (z.B. DEADBEEF): ~1 zu 128 Billionen

**Tipp:** Kürzere Patterns (4-6 Zeichen) sind realistisch zu finden!

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
