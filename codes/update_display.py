from machine import I2C, Pin
from sh1106 import SH1106_I2C
import time
from array import array

def main():
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
    oled = SH1106_I2C(i2c)
    distance = 40
    unit_idx = 1
    
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

    # vybarveni tretin
    if distance <= 70:
        # ctyri body lichobezniku (LD,    PD,     PH,      LH)
        bot_third = array('h', [4, 61, 123, 61, 115, 44, 12, 44])
        oled.poly (0, 0, bot_third, 1, True) # vykresleni a vyplneni (0, 0 - posun na disp, True - tvar se vyplni)
    if distance <= 40:
        mid_third = array('h', [15, 39, 112, 39, 105, 24, 22, 24])
        oled.poly (0, 0, mid_third, 1, True)
    if distance <= 10:
        top_third = array('h', [25, 19, 102, 19, 95, 4, 32, 4])
        oled.poly (0, 0, top_third, 1, True)

    # hodnota
    oled.fill_rect(46, 24, 34, 16, 0) # prazdne pozadi (x = 63 - width/2)
    if unit_idx == 0:
        oled.text(f"{distance:.1f}",48 ,28, 1)
    else:
        oled.text(f"{distance / 2.54:.1f}",48 ,28, 1)

    
    # jednotka
    if unit_idx == 0:
        icon = [
            [0,1,1,1,0,0,1,0,0,0,1],
            [1,0,0,0,1,0,1,1,0,1,1],
            [1,0,0,0,0,0,1,0,1,0,1],
            [1,0,0,0,1,0,1,0,0,0,1],
            [0,1,1,1,0,0,1,0,0,0,1]
        ]
    else:
        icon = [
            [1,1,1,0,1,0,0,0,1,0,0,1,1,1,0,0,1,0,0,0,1],
            [0,1,0,0,1,1,0,0,1,0,1,0,0,0,1,0,1,0,0,0,1],
            [0,1,0,0,1,0,1,0,1,0,1,0,0,0,0,0,1,1,1,1,1],
            [0,1,0,0,1,0,0,1,1,0,1,0,0,0,1,0,1,0,0,0,1],
            [1,1,1,0,1,0,0,0,1,0,0,1,1,1,0,0,1,0,0,0,1]
        ]
    pos_x, pos_y = 2, 2
    for y, row in enumerate(icon):
        for x, value in enumerate(row):
            oled.pixel(pos_x + x, pos_y + y, value)
    
    oled.show()

    try:
        while True:
            time.sleep(2)

    except KeyboardInterrupt:
        oled.fill(0)
        oled.show()
        
if __name__ == "__main__":
    main()

