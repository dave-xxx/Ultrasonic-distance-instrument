"""
Buzzer test without the ultrasonic sensor.

A potentiometer on GP26 (Analog header) simulates a distance of 0-120 cm.
Turn it and listen: silent above 100 cm, faster beeps below,
continuous tone under 10 cm.
"""

from machine import Pin, ADC
from buzzer import ParkingBuzzer
import time


def main():
    """Main application entry point."""
    print("Turn the potentiometer; press Ctrl+C to stop")

    buzzer = ParkingBuzzer(pin=22)
    pot = ADC(Pin(26))
    last_print = time.ticks_ms()

    try:
        while True:
            distance = pot.read_u16() / 65535 * 120
            buzzer.set_distance(distance)
            buzzer.update()

            # Print twice a second so the REPL is not flooded
            if time.ticks_diff(time.ticks_ms(), last_print) >= 500:
                last_print = time.ticks_ms()
                print("Distance: {:.1f} cm".format(distance))

            time.sleep_ms(5)

    except KeyboardInterrupt:
        # This part runs when Ctrl+C is pressed
        print("\nProgram stopped. Exiting...")

    finally:
        buzzer.deinit()


# Run this only when executed directly, not when imported
if __name__ == "__main__":
    main()
