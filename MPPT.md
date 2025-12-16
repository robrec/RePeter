Sachen die ich gerne vorher gewusst hätte...

# Heute :MPPT

[__TOC__]

### Warum MPPT grundsätzlich gut ist

Ein Solarpanel hat **keine feste Spannung**.
Für jede Beleuchtung gibt es **einen Punkt**, an dem

> **Leistung = Spannung × Strom maximal ist**
> → der **Maximum Power Point (MPP)**

#### Ohne MPPT

* Der Verbraucher (z. B. Akku + Lader) **zwingt** dem Panel eine Spannung auf
* Meist liegt diese **nicht** im MPP
* Ergebnis: Ein Teil der möglichen Leistung bleibt ungenutzt

#### Mit MPPT

* Ein Regler misst kontinuierlich:

  * Panelspannung
  * Panelstrom
* Er stellt seinen Arbeitspunkt so ein, dass das Panel **immer nahe Vmp** bleibt
* Ergebnis:
  ✔ mehr Energie pro Tag
  ✔ besonders bei wechselnder Einstrahlung

 **Bei „großen“ Panels (10 W, 50 W, 200 W)** ist das ein massiver Gewinn.

---

### der Knackpunkt: kleine Panels & kleine Spannungen

Bei **kleinen 5 V / 3 W Panels** kippt die Rechnung.
Nicht, weil MPPT „schlecht“ ist – sondern weil **die Verluste dominieren**.

---

#### A) MPPT braucht einen Schaltregler

MPPT ist **immer** ein DC/DC-Wandler (Buck, Boost oder Buck-Boost).

Das bringt **Fixkosten**:

* Gate-Treiber
* Schaltverluste
* Induktivität
* Messwiderstände
* Regel-IC Eigenverbrauch

Diese Verluste sind **nahezu konstant**, egal ob du
**3 W oder 300 mW** umsetzt.

---

#### B) Kleine Spannung = wenig „Regelspielraum“

Beispiel 5 V Panel:

| Zustand        | Spannung  |
| -------------- | --------- |
| Leerlauf (Voc) | ~6–6,5 V |
| MPP (Vmp)      | ~4,5–5 V |
| Unter Last     | <4,5 V    |

**Der nutzbare Spannungsbereich ist winzig**

MPPT lebt davon, dass es:

> „Spannung opfert, um Strom zu gewinnen“

Aber hier gilt:

* Wir haben nur **~1 V Spielraum**
* Jede Diode, jeder MOSFET frisst einen großen Prozentsatz davon

---

#### C) Wirkungsgrad vs. absolute Leistung

Annahmen:

* Panel liefert realistisch: **300 mW**
* MPPT gewinnt optimistisch: **+15 %** → **+45 mW**

Verluste:

* MPPT-Regler Eigenverbrauch: **20–40 mW**
* Schaltverluste: **10–30 mW**

Netto:

* **0 bis negativ**
* plus: mehr Bauteile, mehr Fehlerquellen

---

#### D) Startproblem bei Low Voltage / Low Power

Viele MPPT-ICs haben:

* Mindest-Eingangsspannung (CN3791 hat 4,4 V)
* Mindestleistung zum Starten

Ergebnis bei diffusem Licht:

* Regler startet
* zieht Strom
* Spannung bricht ein
* Regler schaltet ab
* **Oszillation („Hunting“)**

---

### Warum lineare Lader oft **effizienter** sind

Jetzt kommt der kontraintuitive Teil:

#### Linearer Lader (z. B. CN3065)

* Kein Schalten
* Kein Eigenverbrauch in der Regelung
* Nimmt **nur den Strom, den das Panel liefern kann**
* Spannung darf einfach einbrechen

**Das Panel arbeitet automatisch nahe am MPP**, weil:

* der Strom begrenzt ist
* die Spannung sich natürlich einpendelt

Das ist eine **passive MPPT** durch Quellenbegrenzung.

---

### Wann MPPT bei kleinen Panels trotzdem Sinn macht

MPPT lohnt sich bei kleinen Panels **nur**, wenn:

✅ Panelspannung **deutlich höher** ist als Akkuspannung
(z. B. 9–18 V Panel → 3,7 V Akku)

✅ Dauerhaft **>1–2 W reale Leistung**

✅ Sehr guter MPPT-IC mit extrem niedrigem Quiescent Current
(Energy-Harvesting-Klasse)

---

### Faustregeln (praxisbewährt)

| Setup                    | Empfehlung         |
| ------------------------ | ------------------ |
| 5 V Panel                | ❌ MPPT, ✅ Linear |
| ≤3 W Panel              | ❌ MPPT, ✅ Linear |
| ≥10 W Panel             | ✅ MPPT, ❌ Linear |
| Panel ≥2× Akkuspannung | ✅ MPPT, ❌ Linear |
| Diffuses Licht / Indoor  | ❌ MPPT, ✅ Linear |

---

### Testrechnung mit einem 3W 5V Panel und TP4056/CN3063/CN3791

#### Solarpanel

* **Nennleistung:** 3 W
* **Nennspannung:** 5 V
* **Vmp:** ~4,8 V
* **Imp:** ~0,62 A
* **Voc:** ~6,2 V

⚠️ In der Praxis (Winkel, Temperatur, Wolken):

* **typische Leistung:** 30–70 % → **1–2 W**
* wir rechnen **1,5 W real**

---

#### Akku

* 1S Li-Ion
* **Ladespannung:** 4,2 V

---

#### Linearer Lader: **CN3065 / TP4056**

##### Annahmen

* Ladestrom begrenzt auf **300 mA** (solar-tauglich)
* Akkuspannung im Mittel während des Ladens: **3,8 V**
* Panel arbeitet nahe Vmp (~4,6–4,8 V)

---

##### Leistung

###### Eingangsleistung

[
P_{in} = 4{,}8V \times 0{,}3A = 1{,}44W
]

###### Ausgangsleistung

[
P_{out} = 3{,}8V \times 0{,}3A = 1{,}14W
]

###### Verlustleistung (Wärme)

[
P_{loss} = 1{,}44W - 1{,}14W = 0{,}30W
]

**Wirkungsgrad**
[
\eta = \frac{1{,}14}{1{,}44} \approx \mathbf{79%}
]

---

##### Wichtiger Punkt

* **Kein Schaltverlust**
* **Kein Eigenverbrauch**
* Panelspannung bricht einfach ein → **kein Problem**
* Läuft auch bei **100–150 mA** stabil weiter

**Die 1,14 W gehen zuverlässig in den Akku**

---

#### MPPT-Schaltregler: **CN3791**

Jetzt die „Hightech“-Variante.

---

##### Annahmen (realistisch, nicht ideal)

* MPPT hält Panel bei **Vmp = 4,8 V**
* Panel liefert real **1,5 W**
* Schaltwirkungsgrad bei *kleiner Leistung*: **~80 %**
* Eigenverbrauch IC + Gate + Feedback: **30 mW**

---

##### Leistung

###### Eingangsleistung

[
P_{in} = 1{,}5W
]

###### Nach Schaltverlust

[
P_{switch} = 1{,}5W \times 0{,}8 = 1{,}2W
]

###### Abzüglich Eigenverbrauch

[
P_{out} = 1{,}2W - 0{,}03W = \mathbf{1{,}17W}
]

---

##### Realität-Check

Das ist der **Best Case**.

Jetzt die Probleme:

###### Mindestleistung

CN3791 braucht:

* stabile Eingangsspannung
* Mindeststrom für Regelung

Bei leicht schlechterem Licht:

* Panel fällt auf **1,2 W**
* MPPT-Verluste bleiben fast gleich

Neue Rechnung:

[
1{,}2W \times 0{,}8 - 0{,}03 = \mathbf{0{,}93W}
]

**unter dem linearen Lader**

---

#### Direkter Vergleich

| Szenario                           | Leistung in Akku          |
| ---------------------------------- | ------------------------- |
| **CN3065 / TP4056 (300 mA)** | **1,14 W**          |
| CN3791 (sehr gutes Licht)          | ~1,17 W                   |
| CN3791 (leicht schlechteres Licht) | **0,93 W**          |
| CN3791 (diffus)                    | ❌ schwingt / lädt nicht |

---

#### Warum der Linear-Lader gewinnt

###### CN3065 / TP4056

* Verluste **proportional**
* Kein Fix-Overhead
* Funktioniert von **mW bis W**

###### CN3791

* Fixe Verluste
* Schaltverluste dominant bei kleiner Leistung
* Kleiner Spannungs-Hub (5 V → 4,2 V) → MPPT kann kaum „arbeiten“

---

#### Der entscheidende Satz

> **MPPT gewinnt Prozent – aber verliert Milliwatt.**
> Bei einem 3 W / 5 V Panel brauchst du Milliwatt.

---

#### Empfehlung

Für **3 W / 5 V → 1S Li-Ion**:

* ✔ **CN3065** (Solar-optimiert)
* ✔ **TP4056** *nur* mit niedrig eingestelltem Strom
* ❌ **CN3791** (Overkill, schlechter bei wenig Licht in verbindung bei einem Solarpanel mit gerichter V)
