"""
gpio_controller.py
------------------
Reusable helper module for driving the Raspberry Pi 40-pin GPIO header.

Supported operations
--------------------
* set_output(pin)      – configure a BCM pin as a digital output
* set_input(pin, ...)  – configure a BCM pin as a digital input (optional pull)
* write(pin, value)    – set a digital output HIGH / LOW
* read(pin)            – read the logic level of an input pin
* blink(pin, ...)      – toggle an output at a configurable frequency / count
* set_pwm(pin, ...)    – start hardware PWM on a PWM-capable pin
* stop_pwm(pin)        – stop PWM on a pin
* cleanup()            – release all GPIO resources

All pin numbers use the **BCM** (Broadcom SOC) numbering scheme.

Raspberry Pi 40-pin header BCM map
-----------------------------------
Physical | BCM  || Physical | BCM
---------|------||---------|------
   1     |  3V3 ||    2    |  5V
   3     |  2   ||    4    |  5V
   5     |  3   ||    6    |  GND
   7     |  4   ||    8    |  14 (TXD)
   9     |  GND ||   10    |  15 (RXD)
  11     |  17  ||   12    |  18 (PWM0)
  13     |  27  ||   14    |  GND
  15     |  22  ||   16    |  23
  17     |  3V3 ||   18    |  24
  19     |  10 (MOSI) || 20 |  GND
  21     |  9  (MISO) || 22 |  25
  23     |  11 (SCLK) || 24 |  8  (CE0)
  25     |  GND ||   26    |  7  (CE1)
  27     |  0   ||   28    |  1
  29     |  5   ||   30    |  GND
  31     |  6   ||   32    |  12 (PWM0)
  33     |  13 (PWM1)|| 34 |  GND
  35     |  19 (MISO) || 36 |  16
  37     |  26  ||   38    |  20 (MOSI)
  39     |  GND ||   40    |  21 (SCLK)
"""

import time
import RPi.GPIO as GPIO


# BCM pin numbers available on the 40-pin header (power / GND excluded)
ALL_GPIO_PINS = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
]

# Pins that support hardware PWM
PWM_CAPABLE_PINS = {12, 13, 18, 19}


class GPIOController:
    """
    Thin wrapper around RPi.GPIO that tracks pin state and ensures
    resources are released cleanly.
    """

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self._pwm_channels: dict[int, GPIO.PWM] = {}

    # ------------------------------------------------------------------
    # Pin configuration
    # ------------------------------------------------------------------

    def set_output(self, pin: int) -> None:
        """Configure *pin* as a digital output, driven LOW initially."""
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    def set_input(self, pin: int, pull: str = "none") -> None:
        """
        Configure *pin* as a digital input.

        Parameters
        ----------
        pin  : BCM pin number
        pull : "up"   – enable internal pull-up
               "down" – enable internal pull-down
               "none" – floating (default)
        """
        pull_map = {
            "up": GPIO.PUD_UP,
            "down": GPIO.PUD_DOWN,
            "none": GPIO.PUD_OFF,
        }
        if pull not in pull_map:
            raise ValueError(f"pull must be one of {list(pull_map)}, got '{pull}'")
        GPIO.setup(pin, GPIO.IN, pull_up_down=pull_map[pull])

    # ------------------------------------------------------------------
    # Digital I/O
    # ------------------------------------------------------------------

    def write(self, pin: int, value: bool) -> None:
        """Drive *pin* HIGH (True / 1) or LOW (False / 0)."""
        GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)

    def read(self, pin: int) -> bool:
        """Return the current logic level of *pin*."""
        return bool(GPIO.input(pin))

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def blink(self, pin: int, hz: float = 1.0, count: int = 5) -> None:
        """
        Toggle *pin* at *hz* for *count* complete on/off cycles.

        Parameters
        ----------
        pin   : BCM output pin (must already be configured as output)
        hz    : blink frequency in Hertz (default 1 Hz)
        count : number of full on/off cycles (default 5)
        """
        period = 1.0 / hz
        for _ in range(count):
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(period / 2)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(period / 2)

    # ------------------------------------------------------------------
    # PWM
    # ------------------------------------------------------------------

    def set_pwm(self, pin: int, frequency_hz: float = 1000.0,
                duty_cycle: float = 50.0) -> None:
        """
        Start hardware PWM on *pin*.

        Parameters
        ----------
        pin           : BCM pin (must be in PWM_CAPABLE_PINS)
        frequency_hz  : PWM frequency in Hz (default 1000 Hz)
        duty_cycle    : duty cycle in percent 0–100 (default 50 %)
        """
        if pin not in PWM_CAPABLE_PINS:
            raise ValueError(
                f"Pin {pin} does not support hardware PWM. "
                f"PWM-capable pins: {sorted(PWM_CAPABLE_PINS)}"
            )
        if not (0.0 <= duty_cycle <= 100.0):
            raise ValueError(f"duty_cycle must be 0–100, got {duty_cycle}")

        self.set_output(pin)
        if pin in self._pwm_channels:
            self._pwm_channels[pin].stop()

        pwm = GPIO.PWM(pin, frequency_hz)
        pwm.start(duty_cycle)
        self._pwm_channels[pin] = pwm

    def change_duty_cycle(self, pin: int, duty_cycle: float) -> None:
        """Change the duty cycle of an already-running PWM channel."""
        if pin not in self._pwm_channels:
            raise RuntimeError(f"No active PWM on pin {pin}. Call set_pwm() first.")
        if not (0.0 <= duty_cycle <= 100.0):
            raise ValueError(f"duty_cycle must be 0–100, got {duty_cycle}")
        self._pwm_channels[pin].ChangeDutyCycle(duty_cycle)

    def stop_pwm(self, pin: int) -> None:
        """Stop PWM on *pin* and release the channel."""
        if pin in self._pwm_channels:
            self._pwm_channels[pin].stop()
            del self._pwm_channels[pin]

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """Stop all PWM channels and release all GPIO resources."""
        for pwm in self._pwm_channels.values():
            pwm.stop()
        self._pwm_channels.clear()
        GPIO.cleanup()

    # Context-manager support so `with GPIOController() as gpio:` works
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cleanup()
