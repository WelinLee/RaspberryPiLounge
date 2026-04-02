# RaspberryPiLounge

Test and control all 40 GPIO pins on a Raspberry Pi via auto-generated Python code.

## Files

| File | Purpose |
|------|---------|
| `gpio_controller.py` | Reusable `GPIOController` class – configure, read, write, blink, and PWM any pin |
| `gpio_test.py` | CLI script that exercises every GPIO pin with output, input, and PWM tests |
| `requirements.txt` | Python dependencies (`RPi.GPIO`) |
| `tests/` | Unit tests (run on any platform via mocks) |

## Requirements

* Raspberry Pi (any model with a 40-pin header)
* Python 3.9+
* `RPi.GPIO` library

```bash
pip install -r requirements.txt
```

## Running the GPIO tests

```bash
# Test all pins (output blink + input read + PWM)
python gpio_test.py

# Test only output pins
python gpio_test.py --test output

# Test only input pins
python gpio_test.py --test input

# Test only PWM pins
python gpio_test.py --test pwm

# Test specific BCM pin numbers
python gpio_test.py --pins 17 27 22
```

## Using GPIOController in your own code

```python
from gpio_controller import GPIOController

with GPIOController() as gpio:
    # Digital output
    gpio.set_output(17)
    gpio.write(17, True)   # HIGH
    gpio.blink(17, hz=2, count=5)

    # Digital input (with pull-up)
    gpio.set_input(22, pull="up")
    level = gpio.read(22)  # True = HIGH, False = LOW

    # Hardware PWM (pins 12, 13, 18, 19)
    gpio.set_pwm(18, frequency_hz=1000, duty_cycle=50)
    gpio.change_duty_cycle(18, 75)
    gpio.stop_pwm(18)
# gpio.cleanup() is called automatically
```

## Raspberry Pi 40-pin header BCM map

| Physical | BCM | Physical | BCM |
|----------|-----|----------|-----|
| 1  | 3V3  | 2  | 5V  |
| 3  | 2    | 4  | 5V  |
| 5  | 3    | 6  | GND |
| 7  | 4    | 8  | 14 (TXD) |
| 9  | GND  | 10 | 15 (RXD) |
| 11 | 17   | 12 | 18 (PWM0) |
| 13 | 27   | 14 | GND |
| 15 | 22   | 16 | 23 |
| 17 | 3V3  | 18 | 24 |
| 19 | 10 (MOSI) | 20 | GND |
| 21 | 9 (MISO)  | 22 | 25 |
| 23 | 11 (SCLK) | 24 | 8 (CE0) |
| 25 | GND  | 26 | 7 (CE1) |
| 27 | 0    | 28 | 1 |
| 29 | 5    | 30 | GND |
| 31 | 6    | 32 | 12 (PWM0) |
| 33 | 13 (PWM1) | 34 | GND |
| 35 | 19 (MISO) | 36 | 16 |
| 37 | 26   | 38 | 20 (MOSI) |
| 39 | GND  | 40 | 21 (SCLK) |

PWM-capable pins: **12, 13, 18, 19**

## Running the unit tests

Tests use a stub for `RPi.GPIO` so they run on any machine (not just a Pi).

```bash
python -m pytest tests/ -v
```
