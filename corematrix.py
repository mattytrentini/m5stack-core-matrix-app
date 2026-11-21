# SPDX-License-Identifier: MIT
"""Board peripherals for the M5Stack CoreMatrix. Importing does not touch hardware."""

from machine import I2C, Pin
from time import sleep_ms

from bmi270 import BMI270
from m5ioe1 import M5IOE1, REG_GPIO_DRV_L, REG_GPIO_MODE_L, REG_GPIO_OUT_L
from m5pm1 import M5PM1, REG_GPIO_IN
from tm1680 import TM1680


_LED_EN = 4  # M5IOE1 G4, not ESP32 GPIO4
_LED_EN_MASK = 1 << (_LED_EN - 1)


class CoreMatrix:
    """Initialize the board, optionally using a caller-supplied 100 kHz I2C bus.

    The i2c, pm1, ioe1, imu and display attributes expose the bus and drivers.
    Use one instance at a time; the display and PM1 button pins are shared hardware.
    If PM1's I2C idle sleep is enabled, call pm1.wake() after idle before
    reading buttons or power status.
    """

    BUTTON_A = 1 << 0
    BUTTON_B = 1 << 1
    BUTTON_C = 1 << 2

    def __init__(self, i2c=None, *, brightness=2):
        if i2c is None:
            i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100_000)
        self.i2c = i2c
        self.ioe1 = M5IOE1(i2c, addr=0x4F)
        self.imu = BMI270(i2c, address=0x68)
        self.pm1 = M5PM1(i2c, addr=0x6E)
        for gpio in range(3):
            # KEY1..3 (A/B/C) are active-low on PM1 G0..2.
            self.pm1.Pin(gpio, Pin.IN, Pin.PULL_UP)

        self.display = None
        self._owns_led_power = False
        try:
            # M5GFX's C61 BSP drives PYB_LEDS_EN high in push-pull mode and
            # waits 20 ms before talking to TM1680. Leave other IOE pins alone.
            mode = self.ioe1.read_reg(REG_GPIO_MODE_L)
            drive = self.ioe1.read_reg(REG_GPIO_DRV_L)
            latch = self.ioe1.read_reg(REG_GPIO_OUT_L)
            if not (mode & ~drive & latch & _LED_EN_MASK):
                self._owns_led_power = True
                self.ioe1.Pin(_LED_EN, Pin.OUT, value=1)
                sleep_ms(20)
            self.display = TM1680(i2c, address=0x72, brightness=brightness)
        except BaseException:
            self.deinit()
            raise

    def buttons(self):
        """Return the raw mask of pressed buttons (BUTTON_A/B/C)."""
        return ~self.pm1.read_reg(REG_GPIO_IN) & 0x07

    def power_source(self):
        """Return PM1's raw POWER_SOURCE_* bit mask; do not change power state."""
        return self.pm1.get_power_source()

    def deinit(self):
        """Clear and disable our display; turn off the LED rail if we enabled it."""
        try:
            if self.display is not None:
                try:
                    self.display.fill(0)
                    self.display.show()
                finally:
                    self.display.deinit()
                    self.display = None
        finally:
            if self._owns_led_power:
                self.ioe1.set_pin_value(_LED_EN, 0)
                self._owns_led_power = False
