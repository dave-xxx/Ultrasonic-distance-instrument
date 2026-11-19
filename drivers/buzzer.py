"""
Non-blocking parking buzzer for the passive piezo module HW-508.

The beep rate follows the measured distance (same behaviour as the
original ``set_buzzer_frequency.py``, but without ``sleep()``):

- distance is ``None`` or farther than ``far_cm``  -> silent
- distance closer than ``near_cm``                 -> continuous tone
- in between -> short beeps; the pause between them is
  ``pause_ms_per_cm * distance`` (100 cm -> 500 ms, 10 cm -> 50 ms)

Call :meth:`set_distance` whenever a new measurement is available and
:meth:`update` as often as possible from the main loop. Neither method
blocks, so the buzzer never stops the measurement or the display.

Example
-------
.. code-block:: python

    from buzzer import ParkingBuzzer
    import time

    buzzer = ParkingBuzzer(pin=22)
    buzzer.set_distance(40)          # object 40 cm away
    while True:
        buzzer.update()
        time.sleep_ms(5)

Hardware
--------
HW-508: S -> GP22 (PWM), "-" -> GND, middle pin not connected.
The piezo is passive, so it needs a PWM square wave to make a sound.
"""

from machine import Pin, PWM
import time


class ParkingBuzzer:
    """Passive piezo buzzer that beeps faster as an object gets closer."""

    OFF = 0
    BEEP = 1
    TONE = 2

    def __init__(self, pin=22, freq=2500, duty=8192, near_cm=10, far_cm=100,
                 beep_ms=50, pause_ms_per_cm=5):
        """
        :param pin: GPIO connected to the S pin of HW-508.
        :param freq: Tone frequency in Hz.
        :param duty: PWM duty (0-65535) while sounding; 32768 (50 %) is
                     the loudest, 8192 is quieter.
        :param near_cm: Closer than this -> continuous tone.
        :param far_cm: Farther than this -> silent.
        :param beep_ms: Length of one beep in ms.
        :param pause_ms_per_cm: Pause between beeps per cm of distance.
        """
        self._pwm = PWM(Pin(pin))
        self._pwm.freq(freq)
        self._duty = duty
        self.near_cm = near_cm
        self.far_cm = far_cm
        self.beep_ms = beep_ms
        self.pause_ms_per_cm = pause_ms_per_cm

        self._mode = self.OFF
        self._pause_ms = far_cm * pause_ms_per_cm
        self._sounding = False
        self._next_ms = time.ticks_ms()
        self._pwm.duty_u16(0)

    def set_frequency(self, distance_cm):
        """
        Choose the beep pattern for a new distance.

        :param distance_cm: Distance in cm, or ``None`` when there is no
                            valid measurement (the buzzer stays silent).
        """
        if distance_cm is None or distance_cm > self.far_cm:
            self._mode = self.OFF
        elif distance_cm < self.near_cm:
            self._mode = self.TONE
        else:
            self._pause_ms = int(distance_cm * self.pause_ms_per_cm)
            if self._mode != self.BEEP:
                # Start the first beep right away
                self._mode = self.BEEP
                self._next_ms = time.ticks_ms()

    def update(self, now=None):
        """
        Switch the tone on/off when it is time. Call it every few ms.

        :param now: Current ``time.ticks_ms()``; read here when omitted.
        """
        if self._mode == self.OFF:
            self._set_sound(False)
            return
        if self._mode == self.TONE:
            self._set_sound(True)
            return

        if now is None:
            now = time.ticks_ms()
        if time.ticks_diff(now, self._next_ms) >= 0:
            if self._sounding:
                self._set_sound(False)
                self._next_ms = time.ticks_add(now, self._pause_ms)
            else:
                self._set_sound(True)
                self._next_ms = time.ticks_add(now, self.beep_ms)

    def off(self):
        """Silence the buzzer until the next :meth:`set_distance`."""
        self._mode = self.OFF
        self._set_sound(False)

    def deinit(self):
        """Silence the buzzer and release the PWM pin."""
        self.off()
        self._pwm.deinit()

    def _set_sound(self, on):
        if on != self._sounding:
            self._sounding = on
            self._pwm.duty_u16(self._duty if on else 0)


def demo():
    """
    Simulated approach: the distance falls from 120 cm to 5 cm in 10 s,
    so you hear silence, beeps getting faster and finally a continuous tone.
    """
    buzzer = ParkingBuzzer(pin=22)
    start = time.ticks_ms()
    print("Simulated approach 120 -> 5 cm; press Ctrl+C to stop")

    try:
        while True:
            elapsed = time.ticks_diff(time.ticks_ms(), start)
            if elapsed > 10_000:
                break
            distance = 120 - 115 * elapsed / 10_000
            buzzer.set_frequency(distance)
            buzzer.update()
            time.sleep_ms(5)

    except KeyboardInterrupt:
        print("\nProgram stopped.")
    finally:
        buzzer.deinit()


if __name__ == "__main__":
    demo()

