# RaspberryPiLounge

To test RaspberryPi 40 pins via Github copilot auto-generation code.

## SPI and IIC/I2C initialization

This repository now includes a minimal Python example for initializing both SPI
and IIC/I2C communication on a Raspberry Pi.

### File

- `spi_i2c_init.py`

### Raspberry Pi setup

1. Enable SPI and I2C in `raspi-config` or your OS configuration tool.
2. Install the Python modules commonly available on Raspberry Pi OS:
   - `sudo apt install python3-spidev`
   - `sudo apt install python3-smbus`

### Run

```bash
python3 spi_i2c_init.py
```

Optional arguments:

```bash
python3 spi_i2c_init.py --spi-bus 0 --spi-device 0 --spi-speed 500000 --spi-mode 0 --i2c-bus 1
```
