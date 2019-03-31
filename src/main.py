# Must be first
import gi
gi.require_version('Gtk', '3.0')

from application import Application
from circuit import Circuit
import components  # noqa: F401 - import all components


def main():
    circuit = Circuit()
    app = Application(circuit)
    app.loop()


if __name__ == '__main__':
    main()
