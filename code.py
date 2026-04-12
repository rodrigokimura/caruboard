import time

import board
import digitalio
import keypad
import neopixel
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


KEYS: list[dict[Action, list[int]]] = [
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
COLORS: list[str] = [
    "#e3342f",
    "#f6993f",
    "#ffed4a",
    "#38c172",
    "#4dc0b5",
    "#3490dc",
    "#6574cd",
    "#9561e2",
    "#f66d9b",
]
KB = Keyboard(usb_hid.devices)
LED = digitalio.DigitalInOut(getattr(board, "LED"))
LED.direction = digitalio.Direction.OUTPUT
LED.value = False
PIXELS = neopixel.NeoPixel(
    getattr(board, "GP23"),
    1,
    brightness=0.1,
)


def cb(key: int, action: Action) -> None:
    print(f"{action} on key {key}")
    LED.value = True
    KB.send(*KEYS[key].get(action, []))
    LED.value = False
    PIXELS.fill(parse_color(COLORS[key]))


def parse_color(
    color: str | list[int | str] | tuple[int | str, int | str, int | str],
) -> tuple[int, int, int]:
    if isinstance(color, str):
        if color[0] == "#":
            color = color[1:]
        if len(color) != 6:
            raise ValueError("Invalid color")
        r = color[:2]
        g = color[2:4]
        b = color[4:]
        return int(r, 16), int(g, 16), int(b, 16)

    if isinstance(color, (list, tuple)):
        return int(color[0]), int(color[1]), int(color[2])

    raise NotImplementedError


def setup() -> ButtonHandler:
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
    actions: dict[Action, int | str] = {
        "D": ButtonInput.DOUBLE_PRESS,
        "S": ButtonInput.SHORT_PRESS,
        "H": ButtonInput.HOLD,
    }
    for n in range(keys.key_count):
        key = KEYS[n]
        for code, action in actions.items():
            if code in key:
                callbacks.add(ButtonInput(action, n, get_cb(cb, n, code)))

    return ButtonHandler(keys.events, callbacks, keys.key_count)


def main() -> None:
    handler = setup()

    while True:
        handler.update()
        time.sleep(0.0025)


if __name__ == "__main__":
    main()
