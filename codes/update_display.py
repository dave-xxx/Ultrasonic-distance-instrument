from machine import I2C, Pin
from sh1106 import SH1106_I2C
import time
from array import array

def thirds(distance):
    if distance < 70:
        # ctyri body lichobezniku (LD,    PD,     PH,      LH)
        bot_third = array('h', [4, 61, 123, 61, 106, 44, 12, 44])
        oled.poly (0, 0, bot_third, 1, True) # vykresleni a vyplneni (0, 0 - posun na disp, True - tvar se vyplni)
    if distance < 40:
        mid_third = array('h', [15, 39, 103, 39, 96, 44, 22, 44])
        oled.poly (0, 0, mid_third, 1, True)
    if distance < 10:
        top_third = array('h', [25, 19, 93, 19, 86, 4, 32, 4])

def units ():
    if unit_idx == 0:
        distance = distance
        unit = 'CM'
    else:
        distance = distance/2.54
        unit = 'INCH'

    # units = ["CM", "INCH"]
    # unit = units[unit_idx]

def main():
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
    oled = SH1106_I2C(i2c)
    distance = 25.9

    oled.fill(0)
    # sikme cary
    oled.line(2, 61, 31, 2, 1)
    oled.line(125, 61, 96, 2, 1)
       
    # mezery mezi stupnema
    oled.fill_rect(0, 20, 128, 2, 0)
    oled.fill_rect(0, 40, 128, 2, 0)

    # vodorovne carky
    oled.hline(32, 2, 10, 1) # nahore
    oled.hline(86, 2, 10, 1)
    oled.hline(22, 22, 10, 1) # uprostred
    oled.hline(96, 22, 10, 1)
    oled.hline(12, 42, 10, 1) # dole
    oled.hline(106, 42, 10, 1)

    # hodnota
    oled.fill_rect(46, 24, 34, 16, 1) # prazdne pozadi (x = 63 - width/2)
    oled.text(str(distance),48 ,28, 0)
    
    # jednotka
    oled.text(unit, 2, 2, 1)
    
    oled.show()

    try:
        while True:
            time.sleep(2)

    except KeyboardInterrupt:
        oled.fill(0)
        oled.show()
        
        

if __name__ == "__main__":
    main()
