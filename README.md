# MeshCore Narrow Repeater RePeterV1.2

MeshCore Narrow Repeater for [BreMesh.de](https://bremesh.de/)

EasyEDA BreMesh-Team: https://u.easyeda.com/bremesh

RePeter Firmware by [Nagios](https://github.com/timniklas/MeshCore-Bremen)

---

**Note:** This is a learning project for me. These are my first attempts and I make no claims that any of this actually works.

---

- 2026-01-04 - V1.2 Completed. 10 boards ordered - tests pending

![image](images/RePeter_Front.png)
![image](images/RePeterV1_2_Box.PNG)




## Features
- MCU:            [nRF52840 on a ProMicro Board](https://github.com/joric/nrfmicro/wiki/Alternatives/dd5782fb56855cc7e24e884f1e423d664da34db1)
- RF:	            2 Options: HT-RA62, Ra-01SH-P or (Ra-01SCH-P - no experience with). 
- Battery:		      1-3x 18650 OR 1-2x 3000mAh (expandable via QuickCharge Port)
- BMS: 			      XB8789D0 1S 3.2V-4.2V
- ChargeIC:       LTH7R - 4.5V - 5.5V to 4.3V, 300/500mAh via USB-C Port.
- DC-DC:          TPS62840DLCR 3.3V/1A with deep sleep function (optional)
- Display:        SSD1306 0.96" 128x64 OLED via i2c (optional)
- RTC:			      TinyRTC via i2c (optional)
- Temp. Sensor    AHT10 via i2c (optional)
- Weather Sensor: BMP280 via i2c (optional)
- Fuse:			      2A - replaceable (optional - else: 0Ohm Resistor)

- Additional Ports
  - 2xI2C (6x total)
	- GPS
	- External PowerSwitch
- QuickCharge Port:
  - This port is also active while the power is OFF. It's made to make use of external quickcharger. Also this can be used to connect more 1S batteries if needed.


# Components
## Antenna
- Alfa 868MHz
  - https://quantumlink.shop/products/alfa-aoa-868-5acm-5dbi-868mhz-outdoor-lora-antenne
  - 16€ with shipping
## Case
~ 7€
## Solar Panel 5V
2W ~ 4€
3W ~ 12€
## Batteries
### 18650
- https://www.nkon.nl/de/rechargeable/li-ion/18650-size.html?brand=Samsung&protected=Ohne
- 1x 5€ ~ 10Wh ~ 7-10 days battery life
- 2x 10€ ~ 20Wh ~ 14-20 days battery life
- 3x 15€ ~30Wh ~ 3-4 weeks battery life
### LiPo
- https://www.amazon.de/Meshnology-USB-Ladekabel-103665-Schutzplatine-ESP32-Modulplatine-Schwarz/dp/B0F1FHHH5X/
- 1x 7.50€ ~ 11Wh ~ 8-10 days battery life
- 2x 15€ ~ 22Wh ~ 16-21 days battery life
### LiFePo4
- Not supported by the board BUT not impossible.
- Operation with LiFePo4 possible if the following is self-made:
  - LiFePo4 Battery -> appropriate BMS -> LiFePo4 Charger <- Solar Panel
    - In this configuration, the charger can be connected to the QuickCharge port.
    - If this route is chosen, the BMS, fuse, and battery holders no longer need to be populated.
    - Through this route with a LiFePo4 PCB with the corresponding components e.g. in the lid, the RePeter can also be used for this purpose.
## PCB RePeterV1.2
- 2.50€ - 10x ordered, 25€ with shipping + customs

### MCU
- nRF52840 in the form of a ProMicro Board - this is by far the most power-efficient alternative. Products like SenseCap, HelTec T114 etc. also use this MCU. Consumes approx. 1Wh/day.
  - https://a.aliexpress.com/_EHdhbaG
  - ~3€ - 10 pieces 27€ with shipping.

### LoRa Radio Chip
- Ra-01SH IC:SX1264 +22dBm (This is the chip I currently use)
  - Cheapest option, supposedly has problems at low temperatures - haven't been able to confirm yet.
  - https://a.aliexpress.com/_EJohH6k
  - ~3.50€ - 34.50€ for 10 with shipping
- HT-RA62 IC:SX1264 +22dBm
  - Most solid 22dBm chip according to the internet - more expensive - haven't noticed any difference yet.
  - ~4€ - 37.18€ for 10 with shipping


# Cost of a RePeterV1.2

## Minimal Configuration
- Antenna 16€
- Case 7€
- Solar Panel 2W 4€
- 1x 18650 Battery - 5€
- PCB - 2.50€
  - MCU 3€
  - RF 3.5€
...

## Maximum Configuration
- Antenna 16€
- Case 7€
- Solar Panel 3W 12€
- 3x 18650 Battery - 15€
- PCB - 2.50€
  - MCU 3€
  - RF 4€
...


(I'll calculate this sometime...)