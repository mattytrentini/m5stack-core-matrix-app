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

With the board connected over USB, use `mpremote` 1.29 or newer:

```sh
mpremote mip install github:mattytrentini/m5stack-core-matrix-app
mpremote exec 'import corematrix_demo; corematrix_demo.run()'
```

If multiple boards are attached, put `connect PORT` before `mip` or `exec`.
From a local checkout, `mpremote mip install ./package.json` also works.
When using Windows `mpremote.exe` from WSL, pass
`"$(wslpath -m "$PWD/package.json")"` instead of `./package.json`.
On a board connected to Wi-Fi, use
`mip.install("github:mattytrentini/m5stack-core-matrix-app")`.

## Demo

Tilt the board to move the dot. **A** toggles the guide marks, **B** cycles
brightness, and **C** exits. At the REPL, Ctrl-C also stops the demo.
Run `corematrix_demo.run(frames=30)` for a short run that returns to the REPL.

For your own program, `from corematrix import CoreMatrix` exposes `i2c`, `pm1`,
`ioe1`, `imu` and `display` on a `CoreMatrix()` instance. `buttons()` returns
an active-high pressed mask (`BUTTON_A`, `BUTTON_B`, `BUTTON_C`) and
`power_source()` returns the PM1 supply mask. `deinit()` blanks the display
and turns off its rail if the instance enabled it. The tilt demo does not
change charging, SD, buzzer, Grove power or PM1 sleep/wake configuration.

## Step16 encoder demo

Connect the [M5Stack Unit Step16](https://docs.m5stack.com/en/unit/Unit_Step16)
to Grove Port A. Follow the [installation instructions](#install) to install
the app and its Step16 dependency, then run:

```sh
mpremote exec 'import step16_demo; step16_demo.run()'
```

Turn the knob to show its absolute detent (`0`–`F`) and a matching bar on the
CoreMatrix. The Step16 RGB LED cycles through 16 colors, one per detent.
Ctrl-C exits. For a bounded run, pass `samples=30`. The demo restores the
Step16's previous RGB settings and the Grove Port A power configuration on
exit. It does not write to the Step16's flash.

The installed driver also exposes `encoder.led` for RGB power, brightness,
and color in your own programs. See [micropython-step16](https://github.com/mattytrentini/micropython-step16)
for the RGB API and standalone installation.

## DoF10 sensor demo

Connect the [M5Stack Unit DoF10](https://docs.m5stack.com/en/unit/Unit_DoF10)
to Grove Port A. Set its BMI270 address switch to **1** (`0x69`), since the
CoreMatrix's onboard BMI270 already uses `0x68`. The app install pulls in
all three drivers through [m5stack-unit-dof10](https://github.com/mattytrentini/m5stack-unit-dof10).

```sh
mpremote exec 'import dof10_demo; dof10_demo.run()'
```

Move the unit and watch the acceleration, angular velocity, magnetic field,
temperature, and pressure in the terminal. Ctrl-C exits, or pass `samples=5`
for a bounded run. The demo restores the prior Grove power configuration
on exit.

## Drivers

| Device | Source | License |
| --- | --- | --- |
| Stamp Timer Power2 (M5PM1) | [M5Stack UiFlow2](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/m5stack/libs/driver/m5pm1.py), used unchanged | MIT |
| M5IOE1 I/O expander | [M5Stack UiFlow2](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/m5stack/libs/driver/m5ioe1.py), used unchanged | MIT |
| BMI270 accelerometer and gyroscope | [micropython-lib](https://github.com/micropython/micropython-lib/tree/master/micropython/drivers/imu/bmi270), used unchanged | MIT |
| TM1680 white LED matrix | [micropython-tm1680](https://github.com/mattytrentini/micropython-tm1680), installed as a dependency | MIT |
| Step16 rotary encoder | [micropython-step16](https://github.com/mattytrentini/micropython-step16), installed as a dependency | MIT |
| DoF10 magnetometer and barometer | [BMM350](https://github.com/SolderedElectronics/Soldered-BMM350-MicroPython-Library) and [SPA06-003](https://github.com/mattytrentini/micropython-spa06-003), installed by the DoF10 bundle | GPL-3.0 and MIT, respectively |

The application powers the display and instantiates the TM1680 driver.
See the driver repository for standalone installation and framebuffer usage.

## Hardware check

The complete manifest installed over USB with `mpremote mip`. On the board,
M5PM1 reported 5.134 V USB input and no buttons pressed; BMI270 returned
approximately 1 g at rest. The expander switched the display rail, the
TM1680 acknowledged framebuffer and brightness writes, and the demo completed
30 frames and powered down its display rail. The lit pixels and physical
button presses were not observed.
