# BreMesh Repeater "RePeter" V1.2

MeshCore Narrow Repeater fürs [BreMesh.de](https://bremesh.de/)

EasyEDA BreMesh-Team: https://u.easyeda.com/bremesh

RePeter Firmware von [Nagios](https://github.com/timniklas/MeshCore-Bremen)

![image](images/RePeter_Front.png)
![image](images/RePeterV1_2_Box.PNG)

- 2026-01-04 - 10 Boards dieser Version 1.2 sind bestellt - tests ausbleibend


## Features
- MCU:            [nRF52840 on a ProMicro Board](https://github.com/joric/nrfmicro/wiki/Alternatives/dd5782fb56855cc7e24e884f1e423d664da34db1)
- RF:	            2 Optionen: HT-RS62, Ra-01SH-P oder (Ra-01SCH-P - no experience with). 
- Akku:			      1-3x 18650 OR 1-2x 3000mAh (expandable via QuickCharge Port)
- BMS: 			      XB8789D0 1S 3.2V-4,2V
- ChargeIC:       LTH7R - 4.5V - 5.5V to 4.3V, 300/500mAh via USB-C Port.
- DC-DC:          TPS62840DLCR 3.3V/1A with deep sleep function (optional)
- Display:        SSD1513 0,96" 128x64 OLED via i2c (optional)
- RTC:			      TinyRTC via i2c (optional)
- Temp. Sensor    ATH10 via i2c (optional)
- Weather Sensor: BMP280 via i2c (optional)
- Fuse:			      2A - replacable (optional - else: 0Ohm Resistor)

- Additional Ports
  - 2xI2C (6x total)
	- GPS
	- Externer PowerSwitch
- QuickCharge Port:
  - This Port is also Active while the Power is OFF. Its made to make use of external quickcharger. Also this can be used to connect more 1S Batteries if needed.


# Komponents
## Antenna
- Alfa 868MHz
  - https://quantumlink.shop/products/alfa-aoa-868-5acm-5dbi-868mhz-outdoor-lora-antenne
  - 16€ mit Versand
## Gehäuse
~ 7€
## Solarpanel 5V
2W ~ 4€
3W ~ 12€
## Akkus
### 18650
- https://www.nkon.nl/de/rechargeable/li-ion/18650-size.html?brand=Samsung&protected=Ohne
- 1x 5€ ~ 10Wh ~ 7-10Tage Akkulaufzeit
- 2x 10€ ~ 20Wh ~ 14-20Tage Akkulaufzeit
- 3x 15€ ~30Wh ~ 3-4 Wochen Akkulaufzeit
### LiPo
- https://www.amazon.de/Meshnology-USB-Ladekabel-103665-Schutzplatine-ESP32-Modulplatine-Schwarz/dp/B0F1FHHH5X/
- 1x 7,50€ ~ 11Wh ~ 8-10 Tage Akkulaufzeit
- 2x 15€ ~ 22Wh ~ 16-21 Tage Akkulaufzeit
### LiFePo4
- Nicht vom Board supportet ABER nicht unmöglich.
- Betrieb mit LiFePo4 Möglich wenn folgendes selber erstellt wird:
  - LiFePo4 Akku -> entsprechendes BMS -> LiFePo4 Charger <- Solarpanel
    - In dieser Konfiguration kann der Charger an den QuickCharge Port angeschlossen werden.
    - Wenn dieser Weg gewählt wird, muss das BMS, die Fuse und die Batteriehalter nicht mehr bestückt werden.
    - Über diesen Weg mit einem LiFePo4 PCB mit den entsprechenden Komponenten z.B. im Deckel, kann der RePeter auch hierfür benutzt werden.
## PCB RePeterV1.2
- 2,50€ - 10x bestellt, 25€ mit Versand + Zoll

### MCU
- nRF52840 in Form eines ProMicro Board - dieses ist mit abstand die stromsparenste Alternative. Produkte wie SenseCap, HelTec T114 usw. benutzen ebenfalls diesen MCU. Verbraucht ca. 1Wh/Tag.
  - https://a.aliexpress.com/_EHdhbaG
  - ~3€ - 10 Stück 27€ mit Versand.

### LoRa-Funkchip
- Ra-01SH IC:SX1264 +22dBm (Diesen Chip verwende ich zur Zeit)
  - günstigste Variante, soll evtl. bei niedrigen Temperaturn Probleme machen - noch nicht Feststellen können.
  - https://a.aliexpress.com/_EJohH6k
  - ~3,50€ - 34,50€ für 10 mit Versand
- HT-RA62 IC:SX1264 +22dBm
  - Solidester 22dBm Chip laut Internet - teurer - noch keinen Unterschied gemerkt.
  - ~4€ - 37,18€ für 10 mit Versand


# Kosten eines RePetersV1.2

## Minimal Konfiguration
- Antenne 16€
- Gehäuse 7€
- Solarpanel 2W 4€
- 1x 18650 Akku - 5€
- PCB - 2,50€
  - MCU 3€
  - RF 3,5€
...

## Maximale Konfiguration
- Antenne 16€
- Gehäuse 7€
- Solarpanel 3W 12€
- 3x 18650 Akku - 15€
- PCB - 2,50€
  - MCU 3€
  - RF 4€
...


(rechne ich irgendwann mal aus...)