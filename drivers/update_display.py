from machine import I2C, Pin
from sh1106 import SH1106_I2C
from array import array
import time


class ParkingDisplay:
    def __init__(self):
        """Initializes display attributes and static graphic assets."""
        self.i2c = None
        self.oled = None
        self.is_initialized = False

        # Souřadnice lichoběžníků (LD, PD, PH, LH)
        self._bot_third = array('h', [4, 61, 123, 61, 115, 44, 12, 44])
        self._mid_third = array('h', [15, 39, 112, 39, 105, 24, 22, 24])
        self._top_third = array('h', [25, 19, 102, 19, 95, 4, 32, 4])

        # Pixel-art ikony pro jednotky
        self._icon_cm = [
            [0,1,1,1,0,0,1,0,0,0,1],
            [1,0,0,0,1,0,1,1,0,1,1],
            [1,0,0,0,0,0,1,0,1,0,1],
            [1,0,0,0,1,0,1,0,0,0,1],
            [0,1,1,1,0,0,1,0,0,0,1]
        ]
        self._icon_inch = [
            [1,1,1,0,1,0,0,0,1,0,0,1,1,1,0,0,1,0,0,0,1],
            [0,1,0,0,1,1,0,0,1,0,1,0,0,0,1,0,1,0,0,0,1],
            [0,1,0,0,1,0,1,0,1,0,1,0,0,0,0,0,1,1,1,1,1],
            [0,1,0,0,1,0,0,1,1,0,1,0,0,0,1,0,1,0,0,0,1],
            [1,1,1,0,1,0,0,0,1,0,0,1,1,1,0,0,1,0,0,0,1]
        ]


    def display_init(self, i2c_id: int = 0, sda: int = 4, scl: int = 5, freq: int = 100_000):
        """
        Initializes the SH1106 OLED display over I2C.

        Args:
            i2c_id (int): Hardware I2C bus ID (0 or 1).
            sda (int): GPIO pin connected to SDA.
            scl (int): GPIO pin connected to SCL.
            freq (int): I2C clock frequency in Hz.
        """
        self.i2c = I2C(i2c_id, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.oled = SH1106_I2C(self.i2c)
        self.oled.fill(0)
        self.oled.show()

        self.is_initialized = True
        print(f"Display initialized on I2C{i2c_id} (SDA: {sda}, SCL: {scl})")


    def _draw_frame(self):
        """Draws the static parking guide lines and segment gaps."""
        # Šikmé čáry
        self.oled.line(2, 61, 31, 2, 1)
        self.oled.line(125, 61, 96, 2, 1)

        # Mezery mezi stupněma
        self.oled.fill_rect(0, 20, 128, 2, 0)
        self.oled.fill_rect(0, 40, 128, 2, 0)

        # Vodorovné čárky
        self.oled.hline(32, 2, 10, 1)   # nahoře
        self.oled.hline(86, 2, 10, 1)
        self.oled.hline(22, 22, 10, 1)  # uprostřed
        self.oled.hline(96, 22, 10, 1)
        self.oled.hline(12, 42, 10, 1)  # dole
        self.oled.hline(106, 42, 10, 1)


    def _draw_unit(self, unit_idx: int):
        """Draws the CM or INCH icon in the top-left corner."""
        icon = self._icon_cm if unit_idx == 0 else self._icon_inch
        pos_x, pos_y = 2, 2
        for y, row in enumerate(icon):
            for x, value in enumerate(row):
                self.oled.pixel(pos_x + x, pos_y + y, value)


    def update_display(self, distance: float | None, unit_idx: int = 0):
        """
        Updates the OLED screen with the current distance, active segments, and unit.

        Args:
            distance (float | None): Distance in centimeters, or None if out of range.
            unit_idx (int): 0 for CM, 1 for INCH.
        """
        if not self.is_initialized:
            raise RuntimeError("Display has not been initialized. Call display_init() first.")

        self.oled.fill(0)
        self._draw_frame()

        if distance is None:
            # Pokud senzor nedostal odezvu
            self.oled.text("---", 52, 28, 1)
        else:
            # Vybarvení třetin podle vzdálenosti v cm
            if distance <= 70:
                self.oled.poly(0, 0, self._bot_third, 1, True)
            if distance <= 40:
                self.oled.poly(0, 0, self._mid_third, 1, True)
            if distance <= 10:
                self.oled.poly(0, 0, self._top_third, 1, True)

            # Výpočet hodnoty a barvy textu (invertovaná při vybarveném středu)
            value = distance if unit_idx == 0 else distance / 2.54
            text_color = 0 if distance <= 40 else 1
            self.oled.text(f"{value:.1f}", 48, 28, text_color)

        self._draw_unit(unit_idx)
        self.oled.show()


    def clear(self):
        """Clears the OLED display."""
        if not self.is_initialized:
            raise RuntimeError("Display has not been initialized. Call display_init() first.")

        self.oled.fill(0)
        self.oled.show()


# Příklad použití při samostatném spuštění souboru
if __name__ == "__main__":
    display = ParkingDisplay()
    display.display_init(i2c_id=0, sda=4, scl=5)

    try:
        display.update_display(distance=60, unit_idx=1)
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        display.clear()
