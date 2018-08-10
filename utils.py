import cairo
from gi.repository import Gtk


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


def show_popup(title, options, event, callback):
    menu = Gtk.Menu()

    title_menu = Gtk.MenuItem(title)
    title_menu.set_sensitive(False)
    menu.append(title_menu)

    for option in options:
        def activate(widget, option=option):
            callback(option)

        item = Gtk.MenuItem(option)
        item.connect('activate', activate)
        menu.append(item)

    menu.show_all()
    menu.popup(None, None, None, None, event.button, event.time)
