from __future__ import annotations

import argparse

try:
    import spidev
except ImportError as exc:
    raise SystemExit(
        "spidev is required. Install it on Raspberry Pi with "
        "'sudo apt install python3-spidev'."
    ) from exc

try:
    from smbus2 import SMBus
except ImportError:
    try:
        from smbus import SMBus  # type: ignore[no-redef]
    except ImportError as exc:
        raise SystemExit(
            "smbus2 or smbus is required. Install one on Raspberry Pi with "
            "'sudo apt install python3-smbus'."
        ) from exc

def initialize_spi(
    bus: int = 0,
    device: int = 0,
    max_speed_hz: int = 500000,
    mode: int = 0,
) -> spidev.SpiDev:
    """Open and configure SPI, closing it if setup fails."""
    spi = spidev.SpiDev()
    try:
        spi.open(bus, device)
        spi.max_speed_hz = max_speed_hz
        spi.mode = mode
        return spi
    except Exception:
        spi.close()
        raise


def initialize_i2c(bus: int = 1) -> SMBus:
    """Open an IIC/I2C bus; the caller is responsible for closing it."""
    return SMBus(bus)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize Raspberry Pi SPI and IIC/I2C communication."
    )
    parser.add_argument("--spi-bus", type=int, default=0)
    parser.add_argument("--spi-device", type=int, default=0)
    parser.add_argument("--spi-speed", type=int, default=500000)
    parser.add_argument("--spi-mode", type=int, default=0)
    parser.add_argument("--i2c-bus", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spi: spidev.SpiDev | None = None
    i2c: SMBus | None = None

    try:
        spi = initialize_spi(
            bus=args.spi_bus,
            device=args.spi_device,
            max_speed_hz=args.spi_speed,
            mode=args.spi_mode,
        )
        i2c = initialize_i2c(bus=args.i2c_bus)
        print(
            "SPI initialized on "
            f"bus={args.spi_bus}, device={args.spi_device}, "
            f"speed={args.spi_speed}Hz, mode={args.spi_mode}"
        )
        print(f"IIC/I2C initialized on bus={args.i2c_bus}")
    finally:
        if spi is not None:
            spi.close()
        if i2c is not None:
            i2c.close()


if __name__ == "__main__":
    main()
