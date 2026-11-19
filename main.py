"""
Ultrasonic distance instrument - main program.

    Initialization -> while True -> Read BME280 -> Measure distance
    -> flag = True? (switch unit) -> Draw display -> Change the beep rate

Timing plan (one loop, no long sleep() anywhere):

=====================  ===========  ==============================================
Activity               Interval     How it runs
=====================  ===========  ==============================================
Read BME280            2 s          temperature changes slowly; one read blocks
                                    about 16 ms, so it is not read every cycle
Measure HC-SR04        100 ms       HC-SR04 needs at least 60 ms between pings
Switch unit            on press     button IRQ only sets a flag (200 ms debounce),
                                    the loop handles it in the next cycle
Draw display           100 ms       right after each measurement
Buzzer on/off          every ~5 ms  buzzer.update() is non-blocking
=====================  ===========  ==============================================

Invalid data:
- no echo or more than 400 cm -> distance = None -> display shows "---",
  buzzer is silent
- BME280 missing or I2C error -> default 20 degC, 1013 hPa, 50 %
- OLED missing -> program keeps measuring and beeping, prints to the REPL

Files needed on the Pico (root or /lib):
    main.py, hcsr04.py, bme280.py, sh1106.py, buzzer.py,
    update_display.py (optional, see below)

Display interface (Vojta): ``update_display.py`` must contain::

    def update_display(oled, distance_cm, unit_idx):
        # distance_cm: float in cm, or None when there is no valid echo
        # unit_idx:    0 = cm, 1 = in
        ...
        oled.show()

Until that function exists, a simple text screen (draw_simple) is used.
"""

from machine import Pin, I2C
import time

from hcsr04 import HCSR04Measure
from bme280 import BME280
from sh1106 import SH1106_I2C
from buzzer import ParkingBuzzer

try:
    from update_display import update_display
except ImportError:
    update_display = None


# ---- Pins (see README, Zapojení pinů) ----
PIN_SDA = 4         # I2C0 SDA - OLED + BME280
PIN_SCL = 5         # I2C0 SCL
PIN_TRIG = 20       # HC-SR04 Trig
PIN_ECHO = 21       # HC-SR04 Echo (through 1k/2k divider)
PIN_BUZZER = 22     # HW-508 S (PWM)
PIN_BUTTON = 19     # button to 3V3, internal pull-down

# ---- Timing ----
MEASURE_PERIOD_MS = 100
ENV_PERIOD_MS = 2000
LOOP_SLEEP_MS = 5
DEBOUNCE_MS = 200

# ---- Measurement ----
MAX_RANGE_CM = 400                    # HC-SR04 range is 2-400 cm
DEFAULT_ENV = (20.0, 1013.25, 50.0)   # temperature degC, pressure hPa, humidity %

# ---- Units: index = unit_idx ----
UNITS = ("cm", "in")
CM_PER_UNIT = (1.0, 2.54)

DEBUG = True                          # print every measurement to the REPL

# Set by the button interrupt, cleared by the main loop
button_flag = False
_last_press_ms = 0


def on_button(pin):
    """Button IRQ: only set the flag (with debounce), the loop does the rest."""
    global button_flag, _last_press_ms
    now = time.ticks_ms()
    if time.ticks_diff(now, _last_press_ms) > DEBOUNCE_MS:
        _last_press_ms = now
        button_flag = True


def read_environment(bme):
    """
    Read the BME280.

    :return: (temperature degC, pressure hPa, humidity %); defaults when the
             sensor is missing or does not answer.
    """
    if bme is None:
        return DEFAULT_ENV
    try:
        temperature = bme.temperature()   # first: starts a new measurement
        humidity = bme.humidity()
        pressure = bme.pressure()
        return (temperature, pressure, humidity)
    except OSError:
        return DEFAULT_ENV


def measure_distance(sensor, env):
    """
    Measure the distance compensated for temperature and humidity.

    :return: Distance in cm, or None (no echo / out of range).
    """
    temperature, pressure, humidity = env
    distance = sensor.get_acc_distance(temperature, pressure, humidity)
    if distance is None or distance > MAX_RANGE_CM:
        return None
    return distance


def format_distance(distance_cm, unit_idx):
    """Return the distance as text in the selected unit, e.g. '25.9 cm'."""
    if distance_cm is None:
        return "---"
    value = distance_cm / CM_PER_UNIT[unit_idx]
    return "{:.1f} {}".format(value, UNITS[unit_idx])


def draw_simple(oled, distance_cm, unit_idx):
    """Temporary screen used until update_display() is ready."""
    oled.fill(0)
    oled.text("Distance:", 0, 16)
    oled.text(format_distance(distance_cm, unit_idx), 0, 32)
    oled.show()


def init_oled(i2c):
    try:
        return SH1106_I2C(i2c)
    except OSError:
        print("OLED not found - continuing without display")
        return None


def init_bme(i2c):
    try:
        return BME280(i2c=i2c)
    except OSError:
        print("BME280 not found - using default 20 degC")
        return None


def main():
    global button_flag

    # ---- Initialization: I2C, sensors, unit_idx = 0 ----
    i2c = I2C(0, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400_000)
    oled = init_oled(i2c)
    bme = init_bme(i2c)

    sensor = HCSR04Measure()
    sensor.sensor_init(trig=PIN_TRIG, echo=PIN_ECHO)

    buzzer = ParkingBuzzer(pin=PIN_BUZZER)

    button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_DOWN)
    button.irq(trigger=Pin.IRQ_RISING, handler=on_button)

    draw = update_display if update_display is not None else draw_simple
    unit_idx = 0
    env = read_environment(bme)
    next_measure = time.ticks_ms()
    next_env = time.ticks_add(next_measure, ENV_PERIOD_MS)

    print("Running; press Ctrl+C to stop")

    try:
        # ---- while True ----
        while True:
            now = time.ticks_ms()

            if time.ticks_diff(now, next_measure) >= 0:
                next_measure = time.ticks_add(now, MEASURE_PERIOD_MS)

                # ---- Read BME280 (every ENV_PERIOD_MS) ----
                if time.ticks_diff(now, next_env) >= 0:
                    next_env = time.ticks_add(now, ENV_PERIOD_MS)
                    env = read_environment(bme)

                # ---- Measure distance HC-SR04 ----
                distance = measure_distance(sensor, env)

                # ---- flag = True? -> Switch unit ----
                if button_flag:
                    button_flag = False
                    unit_idx = (unit_idx + 1) % len(UNITS)

                # ---- Draw display ----
                if oled is not None:
                    draw(oled, distance, unit_idx)

                # ---- Change the beep rate ----
                buzzer.set_distance(distance)

                if DEBUG:
                    print("{} | {:.1f} degC".format(
                        format_distance(distance, unit_idx), env[0]))

            # Runs every ~5 ms, so beeps keep their length
            buzzer.update(time.ticks_ms())
            time.sleep_ms(LOOP_SLEEP_MS)

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")

    finally:
        buzzer.deinit()
        if oled is not None:
            oled.fill(0)
            oled.show()


# Run this only when executed directly, not when imported
if __name__ == "__main__":
    main()
