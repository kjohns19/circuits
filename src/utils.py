import component as component_module
import component_registry
import shapes

import cairo
import enum
from gi.repository import Gtk
import inspect
import os


class MouseButton(enum.IntEnum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    RELEASE_LEFT = -1
    RELEASE_MIDDLE = -2
    RELEASE_RIGHT = -3

    @classmethod
    def is_press(cls, button):
        return button > 0

    @classmethod
    def is_release(cls, button):
        return button < 0


class TextHAlign(enum.Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class TextVAlign(enum.Enum):
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2


def data_file(name):
    data_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'data'))
    return os.path.join(data_dir, name)


def draw_text(cr, text, position, size=12, bold=False,
              h_align=TextHAlign.CENTER, v_align=TextVAlign.MIDDLE):
    weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
    cr.set_source_rgb(0, 0, 0)
    cr.select_font_face(
        'FreeSans',
        cairo.FONT_SLANT_NORMAL,
        weight)
    cr.set_font_size(size)

    x, y, w, h, dx, dy = cr.text_extents(text)

    offset = [0, 0]
    if h_align == TextHAlign.CENTER:
        offset[0] = -w/2
    elif h_align == TextHAlign.RIGHT:
        offset[0] = -w

    if v_align == TextVAlign.MIDDLE:
        offset[1] = h/2
    elif v_align == TextVAlign.BOTTOM:
        offset[1] = h

    cr.move_to(*(shapes.Vector2(position) + offset))
    cr.show_text(text)


def draw_line(cr, pos1, pos2, color):
    cr.set_source_rgb(*color)
    cr.move_to(*pos1)
    cr.line_to(*pos2)
    cr.set_line_width(2)
    cr.stroke()


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


def create_nary_component(name, category, function, default_value=None):
    signature = inspect.signature(function)
    num_inputs = len(signature.parameters)

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
            circuit, num_inputs=num_inputs, num_outputs=1, on_update=on_update)
        on_update(component)
        return component


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