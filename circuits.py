#!/usr/bin/env python3.6

import gi
gi.require_version('Gtk', '3.0')

from application import Application
from circuit import Circuit
import components  # noqa: F401

import os


UI_CONFIG_FILE = os.path.join(
    os.path.dirname(__file__),
    'data',
    'ui.glade')


def main():
    circuit = Circuit()
    app = Application(circuit, UI_CONFIG_FILE)
    app.loop()


if __name__ == '__main__':
    main()
