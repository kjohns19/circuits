from . import setup_gi  # noqa: F401 - must be first to initialize GTK requirements

from . import application
from . import circuit
from . import components  # noqa: F401 - import all components


def main() -> None:
    app = application.Application(circuit.Circuit())
    app.loop()


if __name__ == '__main__':
    main()
