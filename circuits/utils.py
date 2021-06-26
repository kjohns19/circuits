import cairo
import collections.abc as abc
import enum
from gi.repository import Gtk  # type: ignore
import inspect
import itertools
import math
import pathlib
import typing as t

from . import component as component_module
from . import component_registry
from . import properties
from . import shapes


class MouseButton(enum.IntEnum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    RELEASE_LEFT = -1
    RELEASE_MIDDLE = -2
    RELEASE_RIGHT = -3

    @classmethod
    def is_press(cls, button: 'MouseButton') -> bool:
        return button > 0

    @classmethod
    def is_release(cls, button: 'MouseButton') -> bool:
        return button < 0


class TextHAlign(enum.Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class TextVAlign(enum.Enum):
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2


Color = tuple[int, int, int]


def data_file(name: str) -> str:
    data_dir = pathlib.Path(__file__).resolve().parent.parent / 'data'
    return str(data_dir / name)


def draw_text(cr: cairo.Context, text: str, position: shapes.Vector2, size: int = 12,
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
        cr.set_source_rgb(*background_color)
        rect_corner = corner - (2, h/2 + 6)
        cr.rectangle(rect_corner.x, rect_corner.y, w+4, h+4)
        cr.fill()

    cr.move_to(*corner)
    cr.set_source_rgb(0, 0, 0)
    cr.show_text(text)


def draw_line(cr: cairo.Context, pos1: shapes.Vector2, pos2: shapes.Vector2,
              color: Color) -> None:
    cr.set_source_rgb(*color)
    cr.move_to(*pos1)
    cr.line_to(*pos2)
    cr.set_line_width(2)
    cr.stroke()


def draw_lines(cr: cairo.Context, positions: abc.Iterable[shapes.Vector2],
               color: Color) -> None:
    it1, it2 = itertools.tee(positions)
    next(it2, None)
    for pos1, pos2 in zip(it1, it2):
        draw_line(cr, pos1, pos2, color)


def draw_circle(cr: cairo.Context, position: shapes.Vector2, radius: float,
                fill_color: Color, outline_color: Color) -> None:
    cr.new_path()
    cr.arc(position.x, position.y, radius, 0, math.pi*2)

    cr.set_source_rgb(*fill_color)
    cr.fill_preserve()

    cr.set_source_rgb(*outline_color)
    cr.set_line_width(2)
    cr.stroke()


def draw_rectangle(cr: cairo.Context, rect: shapes.Rectangle,
                   fill_color: Color, outline_color: t.Optional[Color] = None) -> None:
    cr.rectangle(*rect.top_left, *rect.size)

    if fill_color:
        cr.set_source_rgb(*fill_color)
        if outline_color:
            cr.fill_preserve()
        else:
            cr.fill()

    if outline_color:
        cr.set_source_rgb(*outline_color)
        cr.set_line_width(2)
        cr.stroke()


def get_connected_components(components):
    def build(component, components):
        if component in components:
            return
        components.add(component)
        for input in component.inputs:
            if input.is_connected():
                output = input.connected_output.component
                build(output, components)
        for output in component.outputs:
            for connected_input in output.connected_inputs:
                build(connected_input.component, components)
    all_components = set()
    for component in components:
        build(component, all_components)
    return all_components


def show_popup(title, options, event, callback):
    menu = Gtk.Menu()

    title_menu = Gtk.MenuItem(title)
    title_menu.set_sensitive(False)
    menu.append(title_menu)

    for i, option in enumerate(options):
        def activate(widget, option=option, i=i):
            callback(i, option)

        item = Gtk.MenuItem(option)
        item.connect('activate', activate)
        menu.append(item)

    menu.show_all()
    menu.popup(None, None, None, None, event.button, event.time)


def create_nary_component(name, category, function,
                          min_inputs=None, max_inputs=None,
                          input_labels=None, output_labels=None,
                          default_value=None):
    if min_inputs is None:
        signature = inspect.signature(function)
        min_inputs = len(signature.parameters)
    max_inputs = max_inputs or min_inputs

    @component_registry.registry.register(name, category)
    def creator(circuit):
        def on_update(component):
            operands = (input.value for input in component.inputs)
            try:
                result = function(*operands)
            except Exception:
                result = default_value
            component.outputs[0].value = result
        component = component_module.Component(
            circuit, num_inputs=min_inputs, num_outputs=1, on_update=on_update,
            input_labels=input_labels, output_labels=output_labels)
        on_update(component)
        return component

    if min_inputs != max_inputs:
        creator.add_property(properties.NumInputsProperty(
            min_value=min_inputs, max_value=max_inputs))


def data_getter(name):
    return lambda component: component.data[name]


def data_setter(name):
    def setter(component, value):
        component.data[name] = value
    return setter


def attr_getter(name):
    return lambda component: getattr(component, name)


def attr_setter(name):
    return lambda component, value: setattr(component, name, value)
