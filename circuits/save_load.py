from gi.repository import Gtk


WINDOW = None


def register_window(window):
    global WINDOW
    WINDOW = window


def show_save_dialog(title, filter_name, filter_pattern):
    dialog = Gtk.FileChooserDialog(
        title, WINDOW,
        Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
    dialog.set_do_overwrite_confirmation(True)
    return _show_dialog(dialog, filter_name, filter_pattern)


def show_load_dialog(title, filter_name, filter_pattern):
    dialog = Gtk.FileChooserDialog(
        title, WINDOW,
        Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    return _show_dialog(dialog, filter_name, filter_pattern)


def _show_dialog(dialog, filter_name, filter_pattern):
    filter = Gtk.FileFilter()
    filter.set_name(filter_name)
    filter.add_pattern(filter_pattern)
    dialog.add_filter(filter)

    response = dialog.run()
    result = None
    if response == Gtk.ResponseType.OK:
        result = dialog.get_filename()
    dialog.destroy()
    return result
