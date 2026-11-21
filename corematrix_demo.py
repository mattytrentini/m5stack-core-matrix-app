# SPDX-License-Identifier: MIT
"""Interactive tilt demo; call run() explicitly to start."""

from time import sleep_ms

from corematrix import CoreMatrix


def run(*, frames=None, delay_ms=40):
    """Show tilt. A toggles the guide, B changes brightness, and C exits.

    With frames=None, run until C or Ctrl-C. Set frames to a nonnegative
    integer to cap the number of displayed frames. Return the number shown.
    """
    if frames is not None:
        if not isinstance(frames, int) or frames < 0:
            raise ValueError("frames must be a nonnegative integer or None")
        if frames == 0:
            return 0

    board = CoreMatrix()
    try:
        display = board.display
        stable = previous = board.buttons()
        guide = True
        brightness = 2
        shown = 0
        while frames is None or shown < frames:
            raw = board.buttons()
            # Accept each transition only after two consecutive samples.
            changed = (raw ^ stable) & ~(raw ^ previous)
            stable ^= changed
            previous = raw
            pressed = changed & raw
            if pressed & board.BUTTON_C:
                break
            if pressed & board.BUTTON_A:
                guide = not guide
            if pressed & board.BUTTON_B:
                brightness = 1 if brightness == 8 else brightness * 2
                display.brightness(brightness)

            ax, ay, _ = board.imu.accel()
            # M5Unified maps board X/Y to raw +Y/-X. With the SD edge down,
            # board X points down, board Y right; gravity opposes acceleration.
            x = min(14, max(0, round(7 + ax * 7)))
            y = min(14, max(0, round(7 - ay * 7)))
            display.fill(0)
            if guide:
                display.pixel(7, 0, 1)
                display.pixel(7, 15, 1)
                display.pixel(0, 7, 1)
                display.pixel(15, 7, 1)
            display.fill_rect(x, y, 2, 2, 1)
            display.show()
            shown += 1
            sleep_ms(delay_ms)
        return shown
    finally:
        board.deinit()
