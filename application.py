from gi.repository import Gtk, Gdk

import clickers
import component_registry

import threading


class Application:
    def __init__(self, circuit):
        self._window = Gtk.Window(title='Circuits')
        self._window.connect('destroy', Gtk.main_quit)

        self._draw_area = Gtk.DrawingArea()
        self._draw_area.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self._draw_area.connect('draw', self._on_draw)
        self._draw_area.connect('button-press-event', self._on_click)

        self._clicker = clickers.CreateClicker()

        self._combo_box = _make_component_selector(
            component_registry.registry, self._clicker)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.pack_start(self._draw_area, True, True, 0)
        vbox.pack_start(self._combo_box, False, False, 0)

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
            component.display.draw(window, cr)
        for component in self._circuit.components:
            component.display.draw_input_wires(window, cr)

    def _on_click(self, window, event):
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return

        button = event.button
        position = (event.x, event.y)
        component = self._circuit.component_at_position(position)

        self._clicker.on_click(self, button, position, component)


def _make_component_selector(registry, clicker):
    by_category_name = {
        '/'.join((cd.category, cd.name)): cd
        for cd in registry.get_component_data()
    }

    store = Gtk.ListStore(str)
    for category_name in sorted(by_category_name.keys()):
        store.append([category_name])

    combo_box = Gtk.ComboBox.new_with_model(store)

    def set_creator(combo_box):
        iter = combo_box.get_active_iter()
        if iter is None:
            return
        model = combo_box.get_model()
        category_name = model[iter][0]
        component_data = by_category_name[category_name]
        clicker.creator = component_data.creator

    combo_box.connect('changed', set_creator)

    text = Gtk.CellRendererText()
    combo_box.pack_start(text, True)
    combo_box.add_attribute(text, 'text', 0)

    return combo_box
