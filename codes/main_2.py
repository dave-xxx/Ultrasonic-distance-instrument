from buzzer import ParkingBuzzer
from hcsr04 import HCSR04Measure
from bme280 import BME280
from update_display import ParkingDisplay
import time
from machine import I2C, Pin

def main():
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
    address = 0x76

    if address not in i2c.scan():
        raise OSError(f"BME280 at {address:#04x} was not detected")

    bme280 = BME280(i2c)
    buzzer = ParkingBuzzer(pin=22)
    hcsr04 = HCSR04Measure()
    hcsr04.sensor_init(trig=20, echo=21)
    display = ParkingDisplay()
    display.display_init(i2c_id=0, sda=4, scl=5, freq=100_000)

    # Tlačítko podle schématu: GP19, internal pull-down (stisknuto = 1)
    button = Pin(19, Pin.IN, Pin.PULL_DOWN)
    last_btn_state = 0

    temperature, humidity, pressure, _ = bme280.read_values()
    unit_idx = 0
    acc = 100
    now = time.ticks_ms()
    last_bme280 = now
    last_hcsr04 = now
    last_draw = now
    last_btn_time = now
    force_draw = False

    print("Reading BME280; press Ctrl+C to stop.")

    try:
        while True:
            now = time.ticks_ms()

            # Tlačítko s debouncerem (neblokující)
            btn_state = button.value()
            if btn_state == 1 and last_btn_state == 0:
                if time.ticks_diff(now, last_btn_time) >= 200:
                    unit_idx = 1 - unit_idx
                    last_btn_time = now
                    force_draw = True
                    print(f"Unit switched to: {'INCH' if unit_idx == 1 else 'CM'}")
            last_btn_state = btn_state

            if time.ticks_diff(now, last_bme280) >= 5000:
                last_bme280 = now
                temperature, humidity, pressure, _ = bme280.read_values()
                print(
                    f"Temperature: {temperature:.1f} C  "
                    f"Humidity: {humidity:.1f} %  "
                    f"Pressure: {pressure:.1f} hPa "
                )

            if time.ticks_diff(now, last_hcsr04) >= 60:
                last_hcsr04 = now
                acc = hcsr04.get_acc_distance(temperature, pressure, humidity)
                if acc is not None:
                    print(f"Distance: {acc:.1f} cm")

            if time.ticks_diff(now, last_draw) >= 100 or force_draw:
                last_draw = now
                force_draw = False
                display.update_display(distance=acc, unit_idx=unit_idx)

            if acc is not None:
                buzzer.set_frequency(distance_cm=acc)
            buzzer.update()

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")
        display.clear()
        buzzer.deinit()


if __name__ == "__main__":
    main()
