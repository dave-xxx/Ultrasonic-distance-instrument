"""
Author: Vojtěch Smerekovský (modified test code by David Latzka)
Description: Example script for testing the SH1106 parking display module.
             Initializes the OLED display on I2C0 (SDA=GP4, SCL=GP5),
             continuously cycles through simulated distances and units
             (CM / INCH) to verify all proximity segments and out-of-range
             handling until interrupted with Ctrl+C. 
"""

from update_display import ParkingDisplay
import time


def main():
    """Main application entry point."""
    print("Press Ctrl+C to stop")

    display = ParkingDisplay()
    display.display_init(i2c_id=0, sda=4, scl=5, freq=100_000)

    # Test values covering all segments (>70, <=70, <=40, <=10) and out of range (None)
    test_distances = [95.0, 60.0, 25.5, 8.2, None]
    unit_idx = 0  # 0 = CM, 1 = INCH

    try:
        while True:
            for dist in test_distances:
                unit_name = "CM" if unit_idx == 0 else "INCH"
                display.update_display(distance=dist, unit_idx=unit_idx)

                if dist is None:
                    print("Display: --- | unit: {} (out of range)".format(unit_name))
                else:
                    print("Display: {:.1f} cm | unit: {}".format(dist, unit_name))

                time.sleep(1.5)

            # Switch between CM and INCH after each full cycle
            unit_idx = 1 - unit_idx

    except KeyboardInterrupt:
        # This part runs when Ctrl+C is pressed
        display.clear()
        print("\nProgram stopped. Exiting...")


# Run this only when executed directly, not when imported
if __name__ == "__main__":
    main()
