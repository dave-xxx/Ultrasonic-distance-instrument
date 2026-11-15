from hcsr04 import HCSR04Measure
import time


def main():
    """Main application entry point."""
    print("Press Ctrl+C to stop")
    
    sensor = HCSR04Measure()
    sensor.sensor_init(trig=20, echo=21)

    try:
        while True:
            raw = sensor.get_distance()
            acc = sensor.get_acc_distance(30.0, 1013.0, 77.0)
            
            if raw is None or acc is None:
                print("No echo / out of range")
            else:
                print("raw: {:.1f} cm | compensated: {:.1f} cm".format(raw, acc))
                
            time.sleep(0.5)

    except KeyboardInterrupt:
        # This part runs when Ctrl+C is pressed
        print("\nProgram stopped. Exiting...")


# Run this only when executed directly, not when imported
if __name__ == "__main__":
    main()
