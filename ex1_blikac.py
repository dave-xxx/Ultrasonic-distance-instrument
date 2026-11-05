from machine import Pin
import time


def main():
    """Main application entry point."""
    print("Press Ctrl+C to stop")

    # TODO 1: Initialize the on-board LED as an output pin
    # Hint: Use Pin("LED", Pin.OUT)
    led = Pin("LED", Pin.OUT)

    try:
        while True:
            # TODO 2: Toggle the LED state (or set it to high then low)
            led.toggle()

            # TODO 3: Add a delay so the blinking is visible (e.g., 500 ms)
            time.sleep_ms(50)

    except KeyboardInterrupt:
        # This part runs when Ctrl+C is pressed
        print("\nProgram stopped. Exiting...")
        
        # Optional cleanup code
        # TODO 4: Ensure the LED is turned OFF before exiting
        led.off()


# Run this only when executed directly, not when imported
if __name__ == "__main__":
    main()