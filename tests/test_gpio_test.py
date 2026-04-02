"""
tests/test_gpio_test.py
-----------------------
Unit tests for gpio_test.py (argument parsing, test routines, summary).
Uses mock GPIO so tests run on any platform.

The RPi.GPIO stub is installed by conftest.py before this file is imported.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

import RPi.GPIO as _gpio_stub  # resolves to our stub from conftest

from gpio_controller import GPIOController
from gpio_test import (
    parse_args,
    run_output_test,
    run_input_test,
    run_pwm_test,
    main,
)

GPIO = _gpio_stub
_pwm_instance: MagicMock = GPIO.PWM.return_value


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_gpio() -> GPIOController:
    GPIO.setmode.reset_mock()
    GPIO.setwarnings.reset_mock()
    GPIO.setup.reset_mock()
    GPIO.output.reset_mock()
    GPIO.input.reset_mock(return_value=1)
    GPIO.cleanup.reset_mock()
    GPIO.PWM.reset_mock()
    _pwm_instance.reset_mock()
    GPIO.PWM.return_value = _pwm_instance
    return GPIOController()


# ---------------------------------------------------------------------------
# parse_args tests
# ---------------------------------------------------------------------------

class TestParseArgs(unittest.TestCase):
    def test_defaults(self):
        ns = parse_args([])
        self.assertEqual(ns.test, "all")
        self.assertIsNone(ns.pins)

    def test_test_flag(self):
        for t in ("output", "input", "pwm", "all"):
            ns = parse_args(["--test", t])
            self.assertEqual(ns.test, t)

    def test_pins_flag(self):
        ns = parse_args(["--pins", "17", "27"])
        self.assertEqual(ns.pins, [17, 27])

    def test_invalid_test_flag_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["--test", "invalid"])


# ---------------------------------------------------------------------------
# test_output tests
# ---------------------------------------------------------------------------

class TestOutputRoutine(unittest.TestCase):
    @patch("time.sleep")
    def test_all_pass_on_valid_pins(self, _):
        gpio = fresh_gpio()
        results = run_output_test(gpio, [17, 27])
        self.assertEqual(results[17], "PASS")
        self.assertEqual(results[27], "PASS")

    @patch("time.sleep")
    def test_fail_recorded_on_exception(self, _):
        gpio = fresh_gpio()
        _gpio_stub.setup.side_effect = RuntimeError("hardware error")
        results = run_output_test(gpio, [17])
        _gpio_stub.setup.side_effect = None
        self.assertEqual(results[17], "FAIL")


# ---------------------------------------------------------------------------
# test_input tests
# ---------------------------------------------------------------------------

class TestInputRoutine(unittest.TestCase):
    def test_high_level_recorded(self):
        gpio = fresh_gpio()
        _gpio_stub.input.return_value = 1
        results = run_input_test(gpio, [17])
        self.assertEqual(results[17], "HIGH")

    def test_low_level_recorded(self):
        gpio = fresh_gpio()
        _gpio_stub.input.return_value = 0
        results = run_input_test(gpio, [17])
        self.assertEqual(results[17], "LOW")


# ---------------------------------------------------------------------------
# test_pwm tests
# ---------------------------------------------------------------------------

class TestPWMRoutine(unittest.TestCase):
    @patch("time.sleep")
    def test_pwm_capable_pin_passes(self, _):
        gpio = fresh_gpio()
        results = run_pwm_test(gpio, [18])
        self.assertEqual(results[18], "PASS")

    @patch("time.sleep")
    def test_non_pwm_pin_skipped(self, _):
        gpio = fresh_gpio()
        results = run_pwm_test(gpio, [17])
        self.assertEqual(results[17], "SKIP")


# ---------------------------------------------------------------------------
# main() integration tests
# ---------------------------------------------------------------------------

class TestMain(unittest.TestCase):
    @patch("time.sleep")
    def test_returns_0_on_success(self, _):
        _gpio_stub.setup.side_effect = None
        _gpio_stub.input.return_value = 1
        rc = main(["--pins", "17", "--test", "output"])
        self.assertEqual(rc, 0)

    def test_returns_1_on_unknown_pin(self):
        rc = main(["--pins", "99"])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
