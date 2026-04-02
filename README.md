# RaspberryPiLounge

Test and control Raspberry Pi GPIO pins, plus initialize SPI and IIC/I2C
interfaces, via auto-generated Python code.

## Repository layout

| Folder | Purpose |
|--------|---------|
| `implementation_plan/` | GPIO controller, GPIO test CLI, requirements, and unit tests |
| `spi_iic_communication_interfaces/` | SPI and IIC/I2C initialization example |

## GPIO implementation folder

Install the GPIO dependency:

```bash
pip install -r implementation_plan/requirements.txt
```

Run the GPIO test CLI:

```bash
python -m implementation_plan.gpio_test --test all
```

Run the GPIO unit tests:

```bash
python -m pytest implementation_plan/tests -v
```

## SPI and IIC/I2C interface folder

Enable SPI and I2C in `raspi-config`, then install the Raspberry Pi OS packages:

```bash
sudo apt install python3-spidev
sudo apt install python3-smbus
```

Run the interface initialization example:

```bash
python spi_iic_communication_interfaces/spi_i2c_init.py
```
