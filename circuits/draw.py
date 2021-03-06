import collections.abc as abc
import contextlib
import enum
import itertools
import math
import typing as t

import cairo

from . import shapes


class Color:
    def __init__(self, rgb: tuple[float, float, float]) -> None:
        self._rgb = rgb

    @property
    def rgb(self) -> tuple[float, float, float]:
        return self._rgb

    @property
    def red(self) -> float:
        return self._rgb[0]

    @property
    def green(self) -> float:
        return self._rgb[1]

    @property
    def blue(self) -> float:
        return self._rgb[2]


COLOR_BLACK = Color((0.0, 0.0, 0.0))
COLOR_GRAY = Color((0.8, 0.8, 0.8))
COLOR_WHITE = Color((1.0, 1.0, 1.0))
COLOR_RED = Color((1.0, 0.0, 0.0))
COLOR_YELLOW = Color((1.0, 1.0, 0.0))
COLOR_GREEN = Color((0.0, 1.0, 0.0))
COLOR_CYAN = Color((0.0, 1.0, 1.0))
COLOR_BLUE = Color((0.0, 0.0, 1.0))
COLOR_MAGENTA = Color((1.0, 0.0, 1.0))


class TextHAlign(enum.Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class TextVAlign(enum.Enum):
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2


@contextlib.contextmanager
def save_state(cr: cairo.Context) -> abc.Generator[None, None, None]:
    cr.save()
    try:
        yield
    finally:
        cr.restore()


def text(cr: cairo.Context, text: str, position: shapes.Vector2, size: int = 12,
         bold: bool = False, h_align: TextHAlign = TextHAlign.CENTER,
         v_align: TextVAlign = TextVAlign.MIDDLE,
         background_color: t.Optional[Color] = None) -> None:
    weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
    cr.select_font_face(
        'FreeMono',
        cairo.FONT_SLANT_NORMAL,
        weight)
    cr.set_font_size(size)

    # Can't display null bytes
    text = text.replace('\x00', '')

    x, y, w, h, dx, dy = cr.text_extents(text)

    offset = [0.0, 0.0]
    if h_align == TextHAlign.CENTER:
        offset[0] = -w/2
    elif h_align == TextHAlign.RIGHT:
        offset[0] = -w

    if v_align == TextVAlign.MIDDLE:
        offset[1] = h/2
    elif v_align == TextVAlign.TOP:
        offset[1] = h

    corner = position + offset

    if background_color is not None:
        cr.set_source_rgb(*background_color.rgb)
        rect_corner = corner - (2, h/2 + 6)
        cr.rectangle(rect_corner.x, rect_corner.y, w+4, h+4)
        cr.fill()

    cr.move_to(*corner)
    cr.set_source_rgb(0, 0, 0)
    cr.show_text(text)


def line(cr: cairo.Context, pos1: shapes.Vector2, pos2: shapes.Vector2,
         color: Color, thickness: float = 2.0) -> None:
    cr.set_source_rgb(*color.rgb)
    cr.move_to(*pos1)
    cr.line_to(*pos2)
    cr.set_line_width(thickness)
    cr.stroke()


def lines(cr: cairo.Context, positions: abc.Iterable[shapes.Vector2],
          color: Color, thickness: float = 2.0) -> None:
    it1, it2 = itertools.tee(positions)
    next(it2, None)
    for pos1, pos2 in zip(it1, it2):
        line(cr, pos1, pos2, color, thickness)


def circle(cr: cairo.Context, position: shapes.Vector2, radius: float,
           fill_color: Color, outline_color: Color) -> None:
    cr.new_path()
    cr.arc(position.x, position.y, radius, 0, math.pi*2)

    cr.set_source_rgb(*fill_color.rgb)
    cr.fill_preserve()

    cr.set_source_rgb(*outline_color.rgb)
    cr.set_line_width(2)
    cr.stroke()


def rectangle(cr: cairo.Context, rect: shapes.Rectangle,
              fill_color: t.Optional[Color],
              outline_color: t.Optional[Color] = None) -> None:
    cr.rectangle(*rect.top_left, *rect.size)

    if fill_color:
        cr.set_source_rgb(*fill_color.rgb)
        if outline_color:
            cr.fill_preserve()
        else:
            cr.fill()

    if outline_color:
        cr.set_source_rgb(*outline_color.rgb)
        cr.set_line_width(2)
        cr.stroke()
