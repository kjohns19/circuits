from gi.repository import Gtk, Gdk

import clickers
import component_registry

import threading


class Application:
    def __init__(self, circuit):
        self._window = Gtk.Window(title='Circuits')
        self._window.connect('destroy', Gtk.main_quit)

        self._draw_area = Gtk.DrawingArea()
        self._draw_area.set_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK)
        self._draw_area.connect('draw', self._on_draw)
        self._draw_area.connect('button_press_event', self._on_click)
        self._draw_area.connect('button_release_event', self._on_click)
        self._draw_area.connect('motion_notify_event', self._on_move)

        self._mouse_pos = (0, 0)

        self._clicker = None

        component_selector = _make_component_selector(
            component_registry.registry, self)

        clicker_selector = _make_clicker_selector(component_selector, self)

        clicker_selector.set_active(0)
        component_selector.set_active(0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.pack_start(self._draw_area, True, True, 0)
        vbox.pack_start(clicker_selector, False, False, 0)
        vbox.pack_start(component_selector, False, False, 0)

        self._window.add(vbox)
        self._window.resize(800, 800)
        self._circuit = circuit
        self._update_time = 0.5

    @property
    def circuit(self):
        return self._circuit

    @property
    def clicker(self):
        return self._clicker

    @clicker.setter
    def clicker(self, value):
        self._clicker = value

    @property
    def update_time(self):
        return self._update_time

    @update_time.setter
    def update_time(self, value):
        self._update_time = value

    def loop(self):
        exit_event = threading.Event()

        def update_thread():
            while not exit_event.wait(self._update_time):
                self._circuit.update()
                self.repaint()

        update_thread = threading.Thread(target=update_thread)
        update_thread.start()

        self._window.show_all()
        Gtk.main()

        exit_event.set()
        update_thread.join()

    def repaint(self):
        self._draw_area.queue_draw()

    def _on_draw(self, window, cr):
        for component in self._circuit.components:
            component.display.draw(self, cr)
        for component in self._circuit.components:
            component.display.draw_input_wires(self, cr)
        if self._clicker:
            self._clicker.draw(self, cr, self._mouse_pos)

    def _on_click(self, window, event):
        position = (event.x, event.y)
        component = self._circuit.component_at_position(position)

        button = event.button
        if event.type == Gdk.EventType.BUTTON_RELEASE:
            button = -event.button

        self._clicker.on_click(self, event, button, position, component)
        return True

    def _on_move(self, window, event):
        self._mouse_pos = (event.x, event.y)
        self._clicker.on_move(self, event, self._mouse_pos)


def _make_component_selector(registry, app):
    by_category_name = {
        '/'.join((cd.category, cd.name)): cd
        for cd in registry.get_component_data()
    }

    store = Gtk.ListStore(str)
    for category_name in sorted(by_category_name.keys()):
        store.append([category_name])

    combo_box = Gtk.ComboBox.new_with_model(store)

    def set_creator(combo_box):
        category_name = _get_combo_box_item(combo_box)
        component_data = by_category_name[category_name]
        app.clicker.creator = component_data.creator

    combo_box.connect('changed', set_creator)

    text = Gtk.CellRendererText()
    combo_box.pack_start(text, True)
    combo_box.add_attribute(text, 'text', 0)

    return combo_box


def _make_clicker_selector(component_selector, app):
    clickers_by_name = {
        'create': clickers.CreateClicker(),
        'edit': clickers.EditClicker(),
        'run': clickers.RunClicker(),
        'wire': clickers.WireClicker()
    }

    store = Gtk.ListStore(str)
    for clicker_name in sorted(clickers_by_name.keys()):
        store.append([clicker_name])

    combo_box = Gtk.ComboBox.new_with_model(store)

    def set_clicker(combo_box):
        clicker_name = _get_combo_box_item(combo_box)
        clicker = clickers_by_name[clicker_name]
        app.clicker = clicker
        component_selector.set_sensitive(clicker_name == 'create')

    combo_box.connect('changed', set_clicker)

    text = Gtk.CellRendererText()
    combo_box.pack_start(text, True)
    combo_box.add_attribute(text, 'text', 0)

    return combo_box


def _get_combo_box_item(combo_box):
    iter = combo_box.get_active_iter()
    if iter is None:
        return
    model = combo_box.get_model()
    return model[iter][0]
