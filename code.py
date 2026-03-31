import time

import board
import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode as KC
from button_handler import ButtonHandler, ButtonInput

try:
    from typing import Callable, Literal

    Action = Literal["S", "D", "H"]
except ImportError:
    pass


def get_cb(func: Callable[[int, Action], None], key_number: int, action: Action):
    def cb():
        return func(key_number, action)

    return cb


KEYS: list[dict[str, list[int]]] = [
    {
        "S": [],
        "D": [],
        "H": [KC.WINDOWS, KC.ONE],
    },
    {
        "S": [KC.WINDOWS, KC.UP_ARROW],
        "D": [],
        "H": [KC.WINDOWS, KC.TWO],
    },
    {
        "S": [],
        "D": [],
        "H": [KC.WINDOWS, KC.THREE],
    },
    {
        "S": [KC.WINDOWS, KC.LEFT_ARROW],
        "D": [KC.WINDOWS, KC.CONTROL, KC.LEFT_ARROW],
        "H": [KC.WINDOWS, KC.SHIFT, KC.LEFT_ARROW],
    },
    {
        "S": [KC.WINDOWS, KC.TAB],
        "D": [],
        "H": [KC.WINDOWS, KC.D],
    },
    {
        "S": [KC.WINDOWS, KC.RIGHT_ARROW],
        "D": [KC.WINDOWS, KC.CONTROL, KC.RIGHT_ARROW],
        "H": [KC.WINDOWS, KC.SHIFT, KC.RIGHT_ARROW],
    },
    {
        "S": [KC.ALT, KC.LEFT_ARROW],
        "D": [],
        "H": [],
    },
    {
        "S": [KC.WINDOWS, KC.DOWN_ARROW],
        "D": [],
        "H": [],
    },
    {
        "S": [KC.ALT, KC.RIGHT_ARROW],
        "D": [],
        "H": [],
    },
]
KB = Keyboard(usb_hid.devices)


def cb(key: int, action: Literal["S", "D", "H"]) -> None:
    print(f"{action} on key {key}")
    KB.send(*KEYS[key].get(action, []))


def main() -> None:
    keys = keypad.Keys(
        (
            getattr(board, "GP29"),
            getattr(board, "GP28"),
            getattr(board, "GP27"),
            getattr(board, "GP22"),
            getattr(board, "GP21"),
            getattr(board, "GP26"),
            getattr(board, "GP17"),
            getattr(board, "GP16"),
            getattr(board, "GP19"),
        ),
        value_when_pressed=False,
        pull=True,
    )

    callbacks: set[ButtonInput] = set()
    for n in range(keys.key_count):
        callbacks.add(ButtonInput(ButtonInput.DOUBLE_PRESS, n, get_cb(cb, n, "D")))
        callbacks.add(ButtonInput(ButtonInput.SHORT_PRESS, n, get_cb(cb, n, "S")))
        callbacks.add(ButtonInput(ButtonInput.HOLD, n, get_cb(cb, n, "H")))

    handler = ButtonHandler(keys.events, callbacks, keys.key_count)

    while True:
        handler.update()
        time.sleep(0.0025)


if __name__ == "__main__":
    main()
