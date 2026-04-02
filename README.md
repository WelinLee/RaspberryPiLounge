# RaspberryPiLounge

Test and control Raspberry Pi GPIO pins, plus initialize SPI and IIC/I2C
interfaces, via auto-generated Python code.

## Current contents

| File | Purpose |
|------|---------|
| `gpio_controller.py` | Reusable `GPIOController` class for GPIO setup, read/write, blink, and PWM |
| `gpio_test.py` | CLI script that exercises Raspberry Pi GPIO pins |
| `spi_i2c_init.py` | Minimal SPI and IIC/I2C initialization example |
| `requirements.txt` | Python dependency for GPIO support |
| `tests/` | Unit tests for the GPIO implementation |
