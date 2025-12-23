# ESP32 RTC Time Sync

Automatische Zeit-Synchronisation für TinyRTC (DS1307) Module via NTP über WLAN.

## Features

- 📡 Holt UTC Zeit via NTP vom Internet
- 🕐 Programmiert TinyRTC (DS1307) RTC-Modul via I2C
- 📺 Optionale OLED Display-Unterstützung (128x64, SSD1306)
- 💡 RGB LED Status-Anzeigen (ESP32-S3 onboard LED)
- 🔌 RTC Hotplug-Unterstützung (kann nach ESP32-Start angeschlossen werden)
- 🌍 Zeigt deutsche Zeit (CET/UTC+1) auf Display an

## Hardware

### Benötigt
- **ESP32-S3-DevKitC-1** (oder kompatibel)
- **TinyRTC DS1307** RTC-Modul
- WLAN-Zugang

### Optional
- **OLED Display** 0,96" I2C (128x64, SSD1306, Adresse 0x3C)

### Pinbelegung (ESP32-S3)

| Komponente | Pin | ESP32-S3 GPIO |
|------------|-----|---------------|
| I2C SDA | SDA | GPIO 8 |
| I2C SCL | SCL | GPIO 9 |
| RGB LED | DIN | GPIO 48 (onboard) |
| RTC VCC | 5V | 5V |
| OLED VCC | 3.3V | 3.3V |

> **Hinweis:** RTC und OLED nutzen den gleichen I2C-Bus

## Installation

### Voraussetzungen
- [PlatformIO](https://platformio.org/) (empfohlen) oder Arduino IDE
- Python 3.x (für PlatformIO)

### WLAN konfigurieren

Passe die WLAN-Zugangsdaten in `ESP32_RTC_TimeSync.ino` an:

```cpp
const char* ssid = "DEIN_WLAN_NAME";
const char* password = "DEIN_WLAN_PASSWORT";
```

### Build & Upload

#### Mit PlatformIO (empfohlen)
```powershell
# Kompilieren und hochladen
.\build_and_flash.ps1

# Nur kompilieren
.\build_and_flash.ps1 -CompileOnly

# Serial Monitor öffnen
.\build_and_flash.ps1 -Monitor
```

#### Manuell mit PlatformIO
```bash
# Build & Upload
pio run --target upload

# Serial Monitor
pio device monitor --baud 115200
```

## Betrieb

### LED Status-Anzeigen

| Farbe | Status |
|-------|--------|
| 🤍 Weiß pulsend | Wartet auf RTC-Modul |
| 🔴 Rot | RTC gefunden, verbinde mit WLAN |
| 🟡 Gelb | WLAN verbunden |
| 🟡 Gelb pulsend | NTP Zeit wird abgerufen |
| 🟢 Grün | ✅ Erfolgreich synchronisiert |

### Display-Anzeige

**Während Synchronisation:**
```
BreMesh RTC Setup
=================

RTC: OK
WLAN...
NTP Sync...
RTC Sync: OK
```

**Nach erfolgreicher Synchronisation:**
```
DE Zeit (CET):
23.12.2025
  18:45:32
Status: OK
```

**Bei Fehler:**
```
FEHLER:
WLAN Verbindung
fehlgeschlagen!

SSID:
WLAN Hotspot
```

oder

```
Fehler: WLAN fehlt
```

### RTC Zeitformat

- **Gespeichert auf RTC:** UTC Zeit (ohne Zeitzone)
- **Angezeigt auf Display:** Deutsche Zeit (CET = UTC+1)
- **Serial Monitor:** Zeigt beide Zeiten an

## Zeitzone & Sommerzeit

Die Firmware speichert **UTC Zeit** auf der RTC und rechnet bei der Anzeige automatisch in deutsche Zeit um:
- **Winterzeit (MEZ/CET):** UTC + 1 Stunde
- **Sommerzeit (MESZ/CEST):** UTC + 2 Stunden

⚠️ **Wichtig:** Für Sommerzeit muss der Code angepasst werden:
```cpp
// Im loop() ändern:
DateTime deTime = now + TimeSpan(0, 2, 0, 0); // +2 Stunden für Sommerzeit
```

## Fehlerbehebung

### WLAN-Verbindung schlägt fehl
- Prüfe SSID und Passwort
- Stelle sicher, dass 2.4 GHz WLAN verfügbar ist (ESP32 unterstützt kein 5 GHz)
- LED bleibt rot → WLAN-Problem

### RTC wird nicht erkannt
- Prüfe I2C-Verkabelung (SDA=GPIO8, SCL=GPIO9)
- LED pulsiert weiß → RTC fehlt oder falsch angeschlossen
- RTC Modul benötigt 5V Versorgung

### Display zeigt nichts
- Prüfe I2C-Adresse (Standard: 0x3C)
- Display benötigt 3.3V (nicht 5V!)
- Code läuft auch ohne Display weiter

### Zeit ist falsch
- Bei Sommerzeit: TimeSpan auf (0, 2, 0, 0) ändern
- Bei falscher Zeitzone: gmtOffset_sec anpassen
- RTC-Batterie prüfen (CR2032)

## Bibliotheken

Die folgenden Bibliotheken werden automatisch von PlatformIO installiert:
- [RTClib](https://github.com/adafruit/RTClib) (v2.1.4)
- [Adafruit GFX Library](https://github.com/adafruit/Adafruit-GFX-Library) (v1.12.4)
- [Adafruit SSD1306](https://github.com/adafruit/Adafruit_SSD1306) (v2.5.16)
- [Adafruit NeoPixel](https://github.com/adafruit/Adafruit_NeoPixel) (v1.15.2)
- WiFi (Arduino ESP32 Core)
- Wire (Arduino ESP32 Core)

## Projektstruktur

```
ESP32_RTC_TimeSync/
├── ESP32_RTC_TimeSync.ino    # Hauptskript
├── platformio.ini             # PlatformIO Konfiguration
├── build_and_flash.ps1        # Build & Flash Script (Windows)
├── README.md                  # Diese Datei
└── src/                       # (wird beim Build erstellt)
```

## Lizenz

Dieses Projekt ist Teil des BreMesh RePeter Projekts.

## Changelog

### v1.0.0 (2025-12-23)
- Initial Release
- UTC Zeit auf RTC speichern
- Deutsche Zeit (CET) auf Display anzeigen
- RTC Hotplug-Unterstützung
- Optionales OLED Display
- RGB LED Status-Anzeigen
- Fehlerbehandlung mit aussagekräftigen Meldungen
