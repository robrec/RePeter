# USB-C Adapter für RePeter

Dieses kleine PCB ist ein USB-C Adapter für das BreMesh RePeter Projekt.

## Übersicht

Das Board ermöglicht es, den RePeter über einen handelsüblichen USB-C Anschluss mit Strom zu versorgen. Dies ist besonders praktisch für:

- **Tests und Entwicklung**: Schneller Aufbau ohne Solarpanel und Akku
- **Indoor-Betrieb**: Permanente Stromversorgung über USB-C Netzteil
- **Notstrom**: Alternative Stromversorgung bei defektem Solar-Setup
- **Winterbetrieb**: Wenn die Solarleistung nicht ausreicht

## Features

- ✅ Standard USB-C Anschluss
- ✅ Kompaktes Design
- ✅ Einfache Integration in das RePeter-System
- ✅ Kompatibel mit handelsüblichen USB-C Netzteilen (5V)

## 3D-Ansichten

### Vorderseite
![USB-C Adapter Vorderseite](3D_USB-C_RePeter_V1_front.png)

### Rückseite
![USB-C Adapter Rückseite](3DUSB-C_RePeter_V1_back.png)

## Technische Daten

- **Eingangsspannung**: 5V DC über USB-C
- **Board-Version**: V1
- **Kompatibilität**: RePeter Boards

## Dateien in diesem Ordner

### Fertigungsdaten
- **[Gerber_USB-C_RePeter_V1.zip](Gerber_USB-C_RePeter_V1.zip)**: Gerber-Dateien für die PCB-Fertigung
- **[BOM_USB-C_Adapter_USB-C_RePeter_V1.xlsx](BOM_USB-C_Adapter_USB-C_RePeter_V1.xlsx)**: Stückliste (Bill of Materials) mit allen benötigten Bauteilen
- **[PickAndPlace_USB-C_RePeter_V1.xlsx](PickAndPlace_USB-C_RePeter_V1.xlsx)**: Pick-and-Place Datei für die automatische Bestückung

### Dokumentation
- **[SCH_USB-C_RePeter_V1.pdf](SCH_USB-C_RePeter_V1.pdf)**: Schaltplan des Adapters

### 3D-Visualisierung
- **[3D_USB-C_RePeter_V1_front.png](3D_USB-C_RePeter_V1_front.png)**: 3D-Ansicht der Vorderseite
- **[3DUSB-C_RePeter_V1_back.png](3DUSB-C_RePeter_V1_back.png)**: 3D-Ansicht der Rückseite
- **[3D_USB-C_RePeter_V1.zip](3D_USB-C_RePeter_V1.zip)**: 3D-Modell des Boards

## Fertigung

### PCB bestellen

1. Die [Gerber_USB-C_RePeter_V1.zip](Gerber_USB-C_RePeter_V1.zip) Datei bei einem PCB-Hersteller hochladen (z.B. JLCPCB, PCBWay, Aisler)
2. Standard-Einstellungen sind in der Regel ausreichend:
   - Material: FR4
   - Dicke: 1,6 mm
   - Kupferdicke: 1 oz
   - Oberflächenfinish: HASL oder ENIG

### Bauteile

Die benötigten Bauteile sind in der [BOM_USB-C_Adapter_USB-C_RePeter_V1.xlsx](BOM_USB-C_Adapter_USB-C_RePeter_V1.xlsx) aufgelistet.

### Bestückung

Bei automatischer Bestückung kann die [PickAndPlace_USB-C_RePeter_V1.xlsx](PickAndPlace_USB-C_RePeter_V1.xlsx) verwendet werden.

Alternativ kann das Board auch manuell bestückt werden - die Bauteile sind in der Regel einfach zu verlöten.

## Installation

1. USB-C Adapter mit dem RePeter Board verbinden
2. USB-C Kabel an ein 5V Netzteil anschließen
3. RePeter sollte nun mit Strom versorgt werden

## Hinweise

⚠️ **Wichtig**: 
- Verwende nur qualitativ hochwertige USB-C Netzteile mit ausreichender Stromstärke
- Beachte die maximale Stromaufnahme deines RePeter-Setups
- Das Board ist nicht für den dauerhaften Outdoor-Einsatz ohne Schutz gedacht

## Support

Weitere Informationen zum RePeter Projekt findest du im [Haupt-README](../README.md).

BreMesh Projekt: https://bremesh.de/

EasyEDA BreMesh-Team: https://u.easyeda.com/bremesh

## Lizenz

Dieses Design ist Teil des BreMesh RePeter Projekts und steht für die Community zur Verfügung.

---

*Entwickelt für das BreMesh.de Projekt - Ein Mesh-Netzwerk für Bremen*
