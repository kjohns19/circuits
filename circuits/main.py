import setup_gi  # noqa: F401 - must be first to initialize GTK requirements

from application import Application
from circuit import Circuit
import components  # noqa: F401 - import all components


def main():
    circuit = Circuit()
    app = Application(circuit)
    app.loop()


if __name__ == '__main__':
    main()
