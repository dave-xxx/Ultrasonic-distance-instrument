from upadte_display import ParkingDisplay
import time 

def main():
    """Main application entry point."""
    print("Press Ctrl+C to stop")
    
    display = ParkingDisplay()
    display.display_init(i2c_id=0, sda=4, scl=5, freq=100_000):


    try:
        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        # This part runs when Ctrl+C is pressed
        print("\nProgram stopped. Exiting...")


# Run this only when executed directly, not when imported
if __name__ == "__main__":
    main()
