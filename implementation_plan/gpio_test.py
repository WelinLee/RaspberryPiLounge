"""
gpio_test.py
------------
Exercise every GPIO-capable pin on the Raspberry Pi 40-pin header.

Tests performed
---------------
1. Output blink test   – drives each output pin HIGH then LOW (verifiable
                         with a multimeter or oscilloscope).
2. Input read test     – reads the current logic level of each pin
                         configured as an input with pull-up / pull-down.
3. PWM test            – runs a 1 kHz / 50 % duty-cycle signal on each
                         PWM-capable pin for a short burst.

Usage
-----
    python -m implementation_plan.gpio_test                # run all tests
    python -m implementation_plan.gpio_test --test output  # run only the output blink test
    python -m implementation_plan.gpio_test --test input   # run only the input read test
    python -m implementation_plan.gpio_test --test pwm     # run only the PWM test
    python -m implementation_plan.gpio_test --pins 17 27   # test only pins 17 and 27

Requires RPi.GPIO (installed automatically on Raspberry Pi OS).
Must be run as root or as a user in the 'gpio' group.
"""

import argparse
import sys
import time

from implementation_plan.gpio_controller import (
    ALL_GPIO_PINS,
    GPIOController,
    PWM_CAPABLE_PINS,
)


# ---------------------------------------------------------------------------
# Individual test routines
# ---------------------------------------------------------------------------

def run_output_test(gpio: GPIOController, pins: list[int]) -> dict[int, str]:
    """
    Blink each pin once at 2 Hz (0.5 s HIGH, 0.5 s LOW).

    Returns a dict mapping pin → "PASS" | "SKIP" | "FAIL".
    """
    results: dict[int, str] = {}
    print("\n[Output blink test]")
    for pin in pins:
        try:
            gpio.set_output(pin)
            gpio.write(pin, True)
            time.sleep(0.25)
            gpio.write(pin, False)
            time.sleep(0.25)
            print(f"  Pin {pin:>2} (BCM) … PASS")
            results[pin] = "PASS"
        except Exception as exc:  # noqa: BLE001
            print(f"  Pin {pin:>2} (BCM) … FAIL  ({exc})")
            results[pin] = "FAIL"
    return results


def run_input_test(gpio: GPIOController, pins: list[int]) -> dict[int, str]:
    """
    Configure each pin as an input with pull-up and read its level.

    Returns a dict mapping pin → "HIGH" | "LOW" | "FAIL".
    """
    results: dict[int, str] = {}
    print("\n[Input read test (pull-up enabled)]")
    for pin in pins:
        try:
            gpio.set_input(pin, pull="up")
            level = gpio.read(pin)
            label = "HIGH" if level else "LOW"
            print(f"  Pin {pin:>2} (BCM) … {label}")
            results[pin] = label
        except Exception as exc:  # noqa: BLE001
            print(f"  Pin {pin:>2} (BCM) … FAIL  ({exc})")
            results[pin] = "FAIL"
    return results


def run_pwm_test(gpio: GPIOController, pins: list[int],
                 duration: float = 1.0) -> dict[int, str]:
    """
    Run 1 kHz / 50 % PWM on each PWM-capable pin for *duration* seconds.

    Returns a dict mapping pin → "PASS" | "SKIP" | "FAIL".
    """
    results: dict[int, str] = {}
    print("\n[PWM test (1 kHz, 50 % duty cycle)]")
    for pin in pins:
        if pin not in PWM_CAPABLE_PINS:
            print(f"  Pin {pin:>2} (BCM) … SKIP  (not PWM-capable)")
            results[pin] = "SKIP"
            continue
        try:
            gpio.set_pwm(pin, frequency_hz=1000.0, duty_cycle=50.0)
            time.sleep(duration)
            gpio.stop_pwm(pin)
            print(f"  Pin {pin:>2} (BCM) … PASS")
            results[pin] = "PASS"
        except Exception as exc:  # noqa: BLE001
            print(f"  Pin {pin:>2} (BCM) … FAIL  ({exc})")
            results[pin] = "FAIL"
    return results


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------

def print_summary(label: str, results: dict[int, str]) -> None:
    totals: dict[str, int] = {}
    for v in results.values():
        totals[v] = totals.get(v, 0) + 1
    parts = ", ".join(f"{k}: {v}" for k, v in sorted(totals.items()))
    print(f"\n  {label} summary — {parts}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test all GPIO pins on the Raspberry Pi 40-pin header.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--test",
        choices=["output", "input", "pwm", "all"],
        default="all",
        help="Which test suite to run (default: all)",
    )
    parser.add_argument(
        "--pins",
        nargs="+",
        type=int,
        metavar="BCM_PIN",
        default=None,
        help="Restrict testing to specific BCM pin numbers (default: all GPIO pins)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    pins = args.pins if args.pins is not None else ALL_GPIO_PINS
    unknown = [p for p in pins if p not in ALL_GPIO_PINS]
    if unknown:
        print(f"ERROR: unknown BCM pin(s): {unknown}", file=sys.stderr)
        print(f"Valid pins: {ALL_GPIO_PINS}", file=sys.stderr)
        return 1

    print("=" * 60)
    print(" Raspberry Pi 40-pin GPIO Test")
    print(f" Pins under test : {pins}")
    print(f" Test suite      : {args.test}")
    print("=" * 60)

    all_results: dict[str, dict[int, str]] = {}
    failures = 0

    with GPIOController() as gpio:
        if args.test in ("output", "all"):
            r = run_output_test(gpio, pins)
            all_results["output"] = r
            failures += sum(1 for v in r.values() if v == "FAIL")

        if args.test in ("input", "all"):
            r = run_input_test(gpio, pins)
            all_results["input"] = r
            failures += sum(1 for v in r.values() if v == "FAIL")

        if args.test in ("pwm", "all"):
            r = run_pwm_test(gpio, pins)
            all_results["pwm"] = r
            failures += sum(1 for v in r.values() if v == "FAIL")

    print("\n" + "=" * 60)
    print(" Results Summary")
    print("=" * 60)
    for label, results in all_results.items():
        print_summary(label, results)

    if failures:
        print(f"\n  {failures} failure(s) detected.")
        return 1

    print("\n  All tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
