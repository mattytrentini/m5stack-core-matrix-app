# SPDX-License-Identifier: MIT
"""Show a Grove-port Step16 detent on the CoreMatrix and the encoder's RGB LED."""

from machine import Pin
from time import sleep_ms

from corematrix import CoreMatrix
from m5ioe1 import REG_GPIO_DRV_L, REG_GPIO_MODE_L, REG_GPIO_OUT_L
from step16 import Step16


_GROVE_EN = 5  # M5IOE1 G5, not ESP32 GPIO5.
_GROVE_MASK = 1 << (_GROVE_EN - 1)
_COLORS = (
    (255, 0, 0),
    (255, 96, 0),
    (255, 191, 0),
    (223, 255, 0),
    (128, 255, 0),
    (32, 255, 0),
    (0, 255, 64),
    (0, 255, 159),
    (0, 255, 255),
    (0, 159, 255),
    (0, 64, 255),
    (32, 0, 255),
    (128, 0, 255),
    (223, 0, 255),
    (255, 0, 191),
    (255, 0, 96),
)


def run(*, address=0x48, samples=None):
    """Show detents until Ctrl-C, or stop after the requested number of samples."""
    board = CoreMatrix()
    ioe = board.ioe1
    saved = None
    saved_led = None
    try:
        mode = ioe.read_reg(REG_GPIO_MODE_L) & _GROVE_MASK
        level = ioe.read_reg(REG_GPIO_OUT_L) & _GROVE_MASK
        drive = ioe.read_reg(REG_GPIO_DRV_L) & _GROVE_MASK
        if not (mode and level and not drive):
            saved = (mode, level, drive)
            ioe.Pin(_GROVE_EN, Pin.OUT, value=1)
            # Allow the unit to boot before the first I2C read.
            sleep_ms(1000)
        encoder = Step16(board.i2c, address)
        led = encoder.led
        display = board.display
        previous = None
        while samples is None or samples > 0:
            position = encoder.position()
            if position != previous:
                if saved_led is None:
                    saved_led = (led.on, led.brightness, led.rgb)
                    led.brightness = 25
                led.rgb = _COLORS[position]
                if previous is None and not saved_led[0]:
                    led.on = True
                digit = "0123456789ABCDEF"[position]
                display.fill(0)
                display.text(digit, 4, 2, 1)
                if position:
                    display.hline(0, 13, position, 1)
                display.show()
                print("Step16:", digit)
                previous = position
            if samples is not None:
                samples -= 1
                if samples == 0:
                    break
            sleep_ms(100)
        return previous
    finally:
        try:
            if saved_led is not None:
                enabled, brightness, rgb = saved_led
                if not enabled:
                    led.on = False
                led.rgb = rgb
                led.brightness = brightness
        finally:
            try:
                if saved is not None:
                    mode, level, drive = saved
                    ioe.update_bits(REG_GPIO_OUT_L, _GROVE_MASK, 0)
                    ioe.update_bits(REG_GPIO_MODE_L, _GROVE_MASK, mode)
                    ioe.update_bits(REG_GPIO_DRV_L, _GROVE_MASK, drive)
                    ioe.update_bits(REG_GPIO_OUT_L, _GROVE_MASK, level)
            finally:
                board.deinit()
