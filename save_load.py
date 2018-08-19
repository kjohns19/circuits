from gi.repository import Gtk


def show_save_dialog(window, circuit):
    dialog = Gtk.FileChooserDialog(
        'Save Circuit', window,
        Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
    dialog.set_do_overwrite_confirmation(True)
    return _show_dialog(dialog)


def show_load_dialog(window):
    dialog = Gtk.FileChooserDialog(
        'Load Circuit', window,
        Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    return _show_dialog(dialog)


def _show_dialog(dialog):
    filter = Gtk.FileFilter()
    filter.set_name('Circuit files')
    filter.add_pattern('*.circuit')
    dialog.add_filter(filter)

    response = dialog.run()
    result = None
    if response == Gtk.ResponseType.OK:
        result = dialog.get_filename()
    dialog.destroy()
    return result
