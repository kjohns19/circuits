from gi.repository import Gtk, Gdk

import threading


class Application:
    def __init__(self, circuit):
        self._window = Gtk.Window(title='Circuits')
        self._window.connect('destroy', Gtk.main_quit)

        self._draw_area = Gtk.DrawingArea()
        self._draw_area.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self._draw_area.connect('draw', self._on_draw)

        self._window.add(self._draw_area)
        self._window.resize(800, 800)
        self._circuit = circuit
        self._update_time = 0.5

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
                self._draw_area.queue_draw()

        update_thread = threading.Thread(target=update_thread)
        update_thread.start()

        self._window.show_all()
        Gtk.main()

        exit_event.set()
        update_thread.join()

    def _on_draw(self, window, cr):
        for component in self._circuit.components:
            component.display.draw(window, cr)
        for component in self._circuit.components:
            component.display.draw_input_wires(window, cr)
