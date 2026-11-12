from time import sleep
from machine import Pin, PWM, ADC


bzucak = PWM(Pin(22))

potenciometr = ADC(Pin(26))

def ovladej_bzucak(distance):
    if distance > 100:
        bzucak.duty_u16(0)
        sleep(0.1)
    elif distance < 10:
        bzucak.freq(600)
        bzucak.duty_u16(8192)
        sleep(0.1)
    else:
        bzucak.freq(900)
        bzucak.duty_u16(8192)
        sleep(0.05)
        bzucak.duty_u16(0)
        pauza = distance / 200.0
        sleep(pauza)
        
    print(f"Vzdálenost: {distance:.1f}")

try:
    while True:
        hodnota_adc = potenciometr.read_u16()
    
        distance = (hodnota_adc / 65535) * 120
        
        ovladej_bzucak(distance)

except KeyboardInterrupt:
    bzucak.duty_u16(0)
    bzucak.deinit()
    print("Program ukončen.")
