from machine import I2C, Pin
from sh1106 import SH1106_I2C
import time


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
    
    
    # oled.rect(0, 28, 100, 20, 1)
    # oled.text(str(distance), 4, 34)
    #oled.line(0, 0, 127, 63, 1)
    oled.show()

    try:
        while True:
            time.sleep(2)

    except KeyboardInterrupt:
        oled.fill(0)
        oled.show()
        
        

if __name__ == "__main__":
    main()
