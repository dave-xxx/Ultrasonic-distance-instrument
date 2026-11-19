from buzzer import ParkingBuzzer
from hcsr04 import HCSR04Measure
from bme280 import BME280
import time
from machine import I2C, Pin

def main():
    temperature, humidity, pressure = 20, 50, 1000
    
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
    address = 0x76

    if address not in i2c.scan():
        raise OSError(f"BME280 at {address:#04x} was not detected")

    bme280 = BME280(i2c)
    buzzer = ParkingBuzzer(pin=22)
    hcsr04 = HCSR04Measure()
    hcsr04.sensor_init(trig=20, echo=21)
    
    print("Reading BME280; press Ctrl+C to stop.")

    try:
        while True:
            if time.ticks_diff(time.ticks_ms(), last_print) >= 150:
                last_print = time.ticks_ms()
                temperature, humidity, pressure, _ = bme280.read_values()
                print(
                    f"Temperature: {temperature:.1f} C  "
                    f"Humidity: {humidity:.1f} %  "
                    f"Pressure: {pressure:.1f} hPa "
                )
                
            if time.ticks_diff(time.ticks_ms(), last_print) >= 200:
                acc = hcsr04.get_acc_distance(temperature, pressure, humidity)
                print(
                    f"Distance: {acc:.1f} units"
                )
            
            buzzer.set_frequency(distance_cm=acc)
            buzzer.update()

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")
        buzzer.deinit()


if __name__ == "__main__":
    main()
