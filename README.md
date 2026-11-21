# MicroPython on M5Stack CoreMatrix

This application runs on the [M5Stack CoreMatrix](https://docs.m5stack.com/en/core/CoreMatrix)
with the `M5STACK_COREMATRIX` MicroPython firmware. The firmware contains no
application or peripheral drivers. Installing this package does not create
`main.py` or start the demo at boot.

## Firmware

Build from the separate MicroPython firmware worktree:

```sh
mpbuild build --build-container espressif/idf:v5.5.5 M5STACK_COREMATRIX
esptool --chip esp32c61 --port PORT erase-flash
esptool --chip esp32c61 --port PORT write-flash 0 \
    ports/esp32/build-M5STACK_COREMATRIX/firmware.bin
```

Erase only for a clean install: this deletes everything on the device.
Replace `PORT` with the USB serial port.

## Install

With the board connected over USB and `mpremote` 1.29 or newer, run from this checkout:

```sh
mpremote mip install ./package.json
mpremote exec 'import corematrix_demo; corematrix_demo.run()'
```

If multiple boards are attached, put `connect PORT` before `mip` or `exec`.
After hosting this repository, pass its `package.json` URL instead. On a board
already connected to Wi-Fi, the same URL works with `mip.install(url)`.
The manifest uses paths relative to itself for files in this repository.

## Demo

Tilt the board to move the dot. **A** toggles the guide marks, **B** cycles
brightness, and **C** exits. At the REPL, Ctrl-C also stops the demo.
Run `corematrix_demo.run(frames=30)` for a short run that returns to the REPL.

For your own program, `from corematrix import CoreMatrix` exposes `i2c`, `pm1`,
`ioe1`, `imu` and `display` on a `CoreMatrix()` instance. `buttons()` returns
an active-high pressed mask (`BUTTON_A`, `BUTTON_B`, `BUTTON_C`) and
`power_source()` returns the PM1 supply mask. `deinit()` blanks the display
and turns off its rail if the instance enabled it. Charging, SD, buzzer,
Grove power and PM1 sleep/wake configuration are not changed by the demo.

## Drivers

| Device | Source | License |
| --- | --- | --- |
| Stamp Timer Power2 (M5PM1) | [M5Stack UiFlow2](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/m5stack/libs/driver/m5pm1.py), used unchanged | MIT |
| M5IOE1 I/O expander | [M5Stack UiFlow2](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/m5stack/libs/driver/m5ioe1.py), used unchanged | MIT |
| BMI270 accelerometer and gyroscope | [micropython-lib](https://github.com/micropython/micropython-lib/tree/master/micropython/drivers/imu/bmi270), used unchanged | MIT |
| TM1680 white LED matrix | `tm1680.py` in this repository; [datasheet](https://datasheet.lcsc.com/datasheet/pdf/11c225efe9ad4391ba4fc8ffaab5702e.pdf?productCode=C84836) and [M5GFX panel](https://github.com/m5stack/M5GFX/blob/master/src/lgfx/v1/panel/Panel_TM1680.inl) as protocol and wiring references | MIT |

`tm1680.json` installs only the TM1680 driver. `TM1680(i2c, address=0x72)`
expects an already powered display with CoreMatrix-compatible 16×16 wiring.
It is a native one-bit `framebuf.FrameBuffer`: call `pixel()`, `text()`, or
other drawing methods, then `show()`. `brightness(0)` blanks the display
without losing the drawing; levels 1–16 set global PWM duty.

[PixelFramebuffer](https://github.com/mattytrentini/micropython-pixel-framebuf)
(MIT) adapts RGB565 to addressable RGB LEDs and converts pixels one at a time.
The TM1680 instead takes packed monochrome data. Its driver uses a 32-byte
framebuffer and a reusable 33-byte transmit buffer, and writes the whole
image in one I2C transaction.

## Hardware check

The complete manifest installed over USB with `mpremote mip`. On the board,
M5PM1 reported 5.134 V USB input and no buttons pressed; BMI270 returned
approximately 1 g at rest. The expander switched the display rail, the
TM1680 acknowledged framebuffer and brightness writes, and the demo completed
30 frames and powered down its display rail. The lit pixels and physical
button presses were not observed.
