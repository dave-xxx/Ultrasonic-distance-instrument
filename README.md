# Ultrasonic-distance-instrument
Measure distance at a steady interval and show the result and a visual near/far indication.

Add a threshold alarm, 
peak/minimum tracking, 
or a simple parking-distance display. 
Check the sensor's echo voltage and use a divider or level shifter if required.

## Team members:
- David Latzka: flowchart
- Dominik Pitrun: block diagram, pinouts
- Vojtěch Smerekovský: Github editor

## Electronic components:
- Raspberry Pi Pico
- OLED display
- Ultrasonic-distance senzor
- buzzer/speaker
- tlačítko na přepínání jednotek

## Features:
- distance measure
- parking display
- v určitých metrech se zobrazí na displeji čára (jako obrubník) (threshold alarm)
- v určitých metrech to začne pípat
- přepínání jednotek vzdálenosti

### Secondary features:
- korekce měření pomocí teploměru BME 280
- progress bar car on the side

## PINS
### Ultrasonic distance sensor HC-SR04:
- VCC
- Trig
- Echo
- GND

### Buzzer HW-508 V0.2:
- S (Signal)
- VCC
- GND

### Display 128x64 SH1106 I2C OLED:
- SDA
- SCK
- VCC
- GND

## Funkce
### Sensor
- v pravidelných intervalech snímá vzdálennost
- vzdálenost zapíše do proměnné

### Display
- má rozsvícený display s čárami parking displeje
- bere proměnnou o vzdálenosti a nechá ji vypsat na displej
- upravuje vyplneni car podle vzdálenosti
- místo pro zobrazení jednotek

### Bzucak
- bere proměnnou o vzdálenosti a podle toho pípá 
- upravuje rychlost pípání podle vzdálenosti

### Button
- zmáčknutí tlačítka se přepnou jednotky (metry/palce), toto se nahraje i na displej


## Work plan
### Week 1
- block diagram with pinouts (Dominik)
- parking display (Vojtech)
- drivers (Vojtech)
- flowchart (David)
- discord skupina (Vojtech)

### Week 2
- code for display (Vojta)
- code for measure distance (David)
- buzzer ()

## Hardware design

### Blokové schéma

![Blokové schéma](block_diagram.png)

Pico W v pravidelném intervalu vyšle na HC-SR04 spouštěcí puls (Trig) a změří délku odezvy (Echo). Z délky pulzu a teploty z BME280 spočítá vzdálenost. Výsledek zobrazí na OLED displeji jako číslo a parkovací čáry a podle vzdálenosti mění rychlost pípání piezo bzučáku. Tlačítko přepíná jednotky metry / palce.

Výpočet: rychlost zvuku `c = 331,3 + 0,606 · T` (m/s, T ve °C), vzdálenost `d = t · c / 2` (t = délka pulzu Echo).

### Schéma zapojení

![Schéma zapojení](wiring_diagram.png)

### Zapojení pinů

| Modul | Pin modulu | Pico W | Fyz. pin | Směr | Rozšiřující deska |
|---|---|---|---|---|---|
| OLED SH1106 | SDA | GP4 (I2C0 SDA) | 6 | obousměrně | lišta I2C0, D/4 |
| OLED SH1106 | SCK | GP5 (I2C0 SCL) | 7 | Pico → OLED | lišta I2C0, C/5 |
| OLED SH1106 | VCC | 3V3 OUT | 36 | napájení | lišta I2C0, 3V3 |
| OLED SH1106 | GND | GND | 38 | zem | lišta I2C0, GND |
| BME280 | SDA | GP4 (I2C0 SDA) | 6 | obousměrně | lišta I2C0, D/4 |
| BME280 | SCL | GP5 (I2C0 SCL) | 7 | Pico → BME280 | lišta I2C0, C/5 |
| BME280 | VIN | 3V3 OUT | 36 | napájení | lišta I2C0, 3V3 |
| BME280 | GND | GND | 38 | zem | lišta I2C0, GND |
| HC-SR04 | Trig | GP20 | 26 | Pico → senzor | Digital, řádek GP20 |
| HC-SR04 | Echo | GP21 (přes dělič) | 27 | senzor → Pico | Digital, řádek GP21 |
| HC-SR04 | Vcc | VBUS (5 V) | 40 | napájení | lišta vedle Pica, VBUS |
| HC-SR04 | Gnd | GND | 28 | zem | Digital, GND |
| Piezo HW-508 | S | GP22 (PWM) | 29 | Pico → piezo | Digital, řádek GP22 |
| Piezo HW-508 | – | GND | 28 | zem | Digital, řádek GP22 |
| Piezo HW-508 | prostřední | nezapojen (NC) | – | – | – |
| Tlačítko | vývod 1 | GP19 (pull-down) | 25 | tlačítko → Pico | Digital, řádek GP19 |
| Tlačítko | vývod 2 | 3V3 OUT | 36 | napájení | Digital, řádek GP19 |





## Flowchart
![flowchart](./main-program-flowchart-v1.0.svg)

## Block diagram
![Blokové schéma s piny](https://github.com/dave-xxx/Ultrasonic-distance-instrument/blob/1acf169554ab39e37ba99871cb8f2bfcaa18266c/block_diagram_temporary.png)

## Oled display
![reverse camera filled](./reverse_camera_filled.png)
