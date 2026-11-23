# SPDX-License-Identifier: MIT
"""Read all three sensors on a DoF10 connected to CoreMatrix Grove Port A."""

from machine import I2C, Pin
from time import sleep_ms

from bmi270 import BMI270
from bmm350 import BMM350, BMM350_OK
from m5ioe1 import M5IOE1, REG_GPIO_DRV_L, REG_GPIO_MODE_L, REG_GPIO_OUT_L
from spa06_003 import SPA06_003


_GROVE_EN = 5  # M5IOE1 G5, not ESP32 GPIO5.
_GROVE_MASK = 1 << (_GROVE_EN - 1)


def run(*, samples=None):
    """Print readings until Ctrl-C, or stop after the requested sample count."""
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100_000)
    ioe = M5IOE1(i2c, addr=0x4F)
    mode = ioe.read_reg(REG_GPIO_MODE_L) & _GROVE_MASK
    level = ioe.read_reg(REG_GPIO_OUT_L) & _GROVE_MASK
    drive = ioe.read_reg(REG_GPIO_DRV_L) & _GROVE_MASK
    enable_grove = not (mode and level and not drive)
    try:
        if enable_grove:
            ioe.Pin(_GROVE_EN, Pin.OUT, value=1)
            sleep_ms(1000)
        # Unit switch at 1: the CoreMatrix's onboard BMI270 already uses 0x68.
        imu = BMI270(i2c, address=0x69)
        mag = BMM350(i2c)
        baro = SPA06_003(i2c)
        while samples is None or samples > 0:
            accel = imu.accel()
            gyro = imu.gyro()
            if mag.get_sensor_data() != BMM350_OK:
                raise OSError("BMM350 read failed: " + mag.status_string())
            field = mag.data
            temperature, pressure = baro.read()
            print(
                "Accel ({:.2f}, {:.2f}, {:.2f}) g | Gyro ({:.2f}, {:.2f}, {:.2f}) deg/s | "
                "Mag ({:.1f}, {:.1f}, {:.1f}) uT | {:.2f} C / {:.2f} hPa".format(
                    *accel, *gyro, field.mag_x, field.mag_y, field.mag_z, temperature, pressure
                )
            )
            if samples is not None:
                samples -= 1
                if samples == 0:
                    break
            sleep_ms(500)
    finally:
        if enable_grove:
            ioe.update_bits(REG_GPIO_OUT_L, _GROVE_MASK, 0)
            ioe.update_bits(REG_GPIO_MODE_L, _GROVE_MASK, mode)
            ioe.update_bits(REG_GPIO_DRV_L, _GROVE_MASK, drive)
            ioe.update_bits(REG_GPIO_OUT_L, _GROVE_MASK, level)
