from machine import Pin
from hcsr04 import HCSR04
import time


def main():
    print("Press Ctrl+C to stop.")
    
    sensor = HCSR04(trigger_pin=20, echo_pin=21)

    try:
        while True:
            distance = sensor.distance_cm()
            print('Distance:', distance, 'cm')
            time.sleep(0.2);

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")

if __name__ == "__main__":
    main()
