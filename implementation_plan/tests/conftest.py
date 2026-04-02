"""
tests/conftest.py
-----------------
Set up a stub RPi.GPIO module before any test file is imported,
so gpio_controller.py and gpio_test.py can be imported on non-Pi hardware.
"""

import sys
import types
from unittest.mock import MagicMock

# Build stub modules
_rpi_stub = types.ModuleType("RPi")
_gpio_stub = types.ModuleType("RPi.GPIO")

_gpio_stub.BCM = "BCM"
_gpio_stub.OUT = "OUT"
_gpio_stub.IN = "IN"
_gpio_stub.HIGH = 1
_gpio_stub.LOW = 0
_gpio_stub.PUD_UP = "PUD_UP"
_gpio_stub.PUD_DOWN = "PUD_DOWN"
_gpio_stub.PUD_OFF = "PUD_OFF"
_gpio_stub.setmode = MagicMock()
_gpio_stub.setwarnings = MagicMock()
_gpio_stub.setup = MagicMock()
_gpio_stub.output = MagicMock()
_gpio_stub.input = MagicMock(return_value=1)
_gpio_stub.cleanup = MagicMock()

_pwm_instance = MagicMock()
_gpio_stub.PWM = MagicMock(return_value=_pwm_instance)

_rpi_stub.GPIO = _gpio_stub
sys.modules.setdefault("RPi", _rpi_stub)
sys.modules.setdefault("RPi.GPIO", _gpio_stub)
