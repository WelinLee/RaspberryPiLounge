"""
tests/test_gpio_controller.py
------------------------------
Unit tests for gpio_controller.py using a mock RPi.GPIO module so that
tests can run on any machine (not just a Raspberry Pi).

The RPi.GPIO stub is installed by conftest.py before this file is imported.
"""

import sys
import unittest
from unittest.mock import MagicMock, call, patch

import RPi.GPIO as _gpio_stub  # resolves to our stub from conftest

from implementation_plan.gpio_controller import (
    ALL_GPIO_PINS,
    GPIOController,
    PWM_CAPABLE_PINS,
)

GPIO = _gpio_stub  # convenient alias
_pwm_instance: MagicMock = GPIO.PWM.return_value


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_controller() -> GPIOController:
    """Return a fresh GPIOController with all GPIO mocks reset."""
    GPIO.setmode.reset_mock()
    GPIO.setwarnings.reset_mock()
    GPIO.setup.reset_mock()
    GPIO.output.reset_mock()
    GPIO.input.reset_mock(return_value=True)
    GPIO.cleanup.reset_mock()
    GPIO.PWM.reset_mock()
    _pwm_instance.reset_mock()
    GPIO.PWM.return_value = _pwm_instance
    return GPIOController()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGPIOControllerInit(unittest.TestCase):
    def test_sets_bcm_mode(self):
        c = make_controller()
        GPIO.setmode.assert_called_once_with(GPIO.BCM)

    def test_disables_warnings(self):
        c = make_controller()
        GPIO.setwarnings.assert_called_once_with(False)


class TestSetOutput(unittest.TestCase):
    def test_calls_gpio_setup_as_output(self):
        c = make_controller()
        c.set_output(17)
        GPIO.setup.assert_called_once_with(17, GPIO.OUT, initial=GPIO.LOW)


class TestSetInput(unittest.TestCase):
    def test_pull_up(self):
        c = make_controller()
        c.set_input(17, pull="up")
        GPIO.setup.assert_called_once_with(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def test_pull_down(self):
        c = make_controller()
        c.set_input(17, pull="down")
        GPIO.setup.assert_called_once_with(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def test_pull_none(self):
        c = make_controller()
        c.set_input(17, pull="none")
        GPIO.setup.assert_called_once_with(17, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

    def test_invalid_pull_raises(self):
        c = make_controller()
        with self.assertRaises(ValueError):
            c.set_input(17, pull="invalid")


class TestWrite(unittest.TestCase):
    def test_write_high(self):
        c = make_controller()
        c.write(17, True)
        GPIO.output.assert_called_once_with(17, GPIO.HIGH)

    def test_write_low(self):
        c = make_controller()
        c.write(17, False)
        GPIO.output.assert_called_once_with(17, GPIO.LOW)


class TestRead(unittest.TestCase):
    def test_returns_true_when_high(self):
        c = make_controller()
        GPIO.input.return_value = 1
        self.assertTrue(c.read(17))

    def test_returns_false_when_low(self):
        c = make_controller()
        GPIO.input.return_value = 0
        self.assertFalse(c.read(17))


class TestBlink(unittest.TestCase):
    @patch("time.sleep")
    def test_blink_toggles_correct_number_of_times(self, mock_sleep):
        c = make_controller()
        c.blink(17, hz=2.0, count=3)
        # Each cycle: HIGH, sleep, LOW, sleep → 2 output calls per cycle
        self.assertEqual(GPIO.output.call_count, 6)
        # HIGH appears first in each cycle
        calls = GPIO.output.call_args_list
        self.assertEqual(calls[0], call(17, GPIO.HIGH))
        self.assertEqual(calls[1], call(17, GPIO.LOW))


class TestPWM(unittest.TestCase):
    def test_set_pwm_on_capable_pin(self):
        c = make_controller()
        c.set_pwm(18, frequency_hz=500.0, duty_cycle=75.0)
        GPIO.PWM.assert_called_once_with(18, 500.0)
        _pwm_instance.start.assert_called_once_with(75.0)

    def test_set_pwm_on_non_capable_pin_raises(self):
        c = make_controller()
        with self.assertRaises(ValueError):
            c.set_pwm(17)  # pin 17 is not PWM-capable

    def test_set_pwm_invalid_duty_cycle_raises(self):
        c = make_controller()
        with self.assertRaises(ValueError):
            c.set_pwm(18, duty_cycle=110.0)

    def test_stop_pwm(self):
        c = make_controller()
        c.set_pwm(18)
        c.stop_pwm(18)
        _pwm_instance.stop.assert_called()
        self.assertNotIn(18, c._pwm_channels)

    def test_change_duty_cycle(self):
        c = make_controller()
        c.set_pwm(18)
        c.change_duty_cycle(18, 25.0)
        _pwm_instance.ChangeDutyCycle.assert_called_once_with(25.0)

    def test_change_duty_cycle_no_active_pwm_raises(self):
        c = make_controller()
        with self.assertRaises(RuntimeError):
            c.change_duty_cycle(18, 25.0)

    def test_change_duty_cycle_invalid_raises(self):
        c = make_controller()
        c.set_pwm(18)
        with self.assertRaises(ValueError):
            c.change_duty_cycle(18, -5.0)


class TestCleanup(unittest.TestCase):
    def test_cleanup_stops_pwm_and_calls_gpio_cleanup(self):
        c = make_controller()
        c.set_pwm(18)
        c.cleanup()
        _pwm_instance.stop.assert_called()
        GPIO.cleanup.assert_called_once()

    def test_context_manager_calls_cleanup(self):
        GPIO.cleanup.reset_mock()
        with GPIOController() as gpio:
            pass
        GPIO.cleanup.assert_called_once()


class TestConstants(unittest.TestCase):
    def test_all_gpio_pins_not_empty(self):
        self.assertGreater(len(ALL_GPIO_PINS), 0)

    def test_pwm_capable_pins_are_subset_of_all(self):
        self.assertTrue(PWM_CAPABLE_PINS.issubset(set(ALL_GPIO_PINS)))


if __name__ == "__main__":
    unittest.main()
