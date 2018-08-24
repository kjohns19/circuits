from component_registry import registry
from component import Component

import cairo
import enum
from gi.repository import Gtk
import inspect


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


def draw_text(cr, text, position, bold=False):
    weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
    cr.set_source_rgb(0, 0, 0)
    cr.select_font_face(
        'FreeSans',
        cairo.FONT_SLANT_NORMAL,
        weight)
    cr.set_font_size(12)

    x, y, w, h, dx, dy = cr.text_extents(text)

    cr.move_to(*(position - (w/2, -h/2)))
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

    @registry.register(name, category)
    def creator(circuit):
        def on_update(component):
            operands = (input.value for input in component.inputs)
            try:
                result = function(*operands)
            except Exception:
                result = default_value
            component.outputs[0].value = result
        component = Component(
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
