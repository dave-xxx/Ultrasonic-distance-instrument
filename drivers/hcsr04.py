"""
Author: David Latzka
Description: MicroPython driver module providing the HCSR04Measure class for
             reading raw and temperature/humidity-compensated distances in
             centimeters from an HC-SR04 ultrasonic sensor.
"""

from machine import Pin, time_pulse_us
from utime import sleep_us


class HCSR04Measure:
    def __init__(self):
        """Initializes sensor attributes."""
        self.trig_pin = None
        self.echo_pin = None
        self.echo_timeout_us = None
        self.is_initialized = False


    def sensor_init(self, trig: int, echo: int, echo_timeout_us=500*2*30):
        """
        Initializes the sensor with specific GPIO pins for Trigger and Echo.
        
        Args:
            trig (int): GPIO pin connected to the sensor's Trigger.
            echo (int): GPIO pin connected to the sensor's Echo.
        """
        self.trig_pin = trig
        self.echo_pin = echo
        self.echo_timeout_us = echo_timeout_us
        
        self.trigger = Pin(self.trig_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)

        self.echo = Pin(self.echo_pin, mode=Pin.IN, pull=None)
        
        self.is_initialized = True
        print(f"Sensor initialized with Trig: {trig}, Echo: {echo}")


    def _measure_time_pulse_us(self):
        """
        Send the pulse to trigger and listen on echo pin.
        """
        self.trigger.value(0)
        sleep_us(5)
        self.trigger.value(1)
        sleep_us(10)
        self.trigger.value(0)
                               
        pulse_time = time_pulse_us(self.echo, 1, self.echo_timeout_us)
        
        if pulse_time < 0: 
            pulse_time = None
            
        return pulse_time


    def get_distance(self) -> float | None:
        """
        Measures and returns the distance in centimeters using a standard 
        speed of sound constant (approx. 343 m/s or 0.0343 cm/µs).
        
        Returns:
            float: Distance in centimeters.
            None: None if no echo was received.
        """
        if not self.is_initialized:
            raise RuntimeError("Sensor has not been initialized. Call sensor_init() first.")

        duration_us = self._measure_time_pulse_us()
        
        if duration_us is None:
            return None
        
        distance = (duration_us / 2) / 29.1
        
        return distance


    def get_acc_distance(self, temperature: float, pressure: float, humidity: float) -> float | None:
        """
        Measures and returns an acoustically compensated distance based on 
        current environmental conditions (temperature, pressure, and humidity).
        
        Args:
            temperature (float): Ambient temperature in degrees Celsius (°C).
            pressure (float): Atmospheric pressure in hPa or mmHg (reserved for future use).
            humidity (float): Relative humidity percentage (0% - 100%).
            
        Returns:
            float: Compensated distance in centimeters.
            None: None if no echo was received.
        """
        if not self.is_initialized:
            raise RuntimeError("Sensor has not been initialized. Call sensor_init() first.")

        # 1. Calculate more precise speed of sound based on temperature, humidity, pressure (reserved).
        # A standard approximation formula for the speed of sound (c in m/s):
        # c ≈ 331.3 * sqrt(1 + T / 273.15) adjusted for humidity and pressure.
        # Below is a common simplified empirical formula factoring in temperature (°C) and humidity (%):
        
        # Speed of sound in m/s
        # (For better precision, water vapor pressure derived from humidity and pressure can be included)
        speed_m_s = 331.3 + (0.606 * temperature) + (0.0124 * humidity)
        
        # Convert speed to cm/µs: (m/s * 100 cm/m) / 1,000,000 µs/s = m/s / 10,000
        speed_cm_us = speed_m_s / 10000.0

        # 2. Measure duration
        duration_us = self._measure_time_pulse_us()
        
        if duration_us is None:
            return None

        # 3. Calculate compensated distance
        distance = (duration_us * speed_cm_us) / 2.0
        
        return distance

