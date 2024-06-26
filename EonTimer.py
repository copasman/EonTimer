#!/usr/bin/env python3
import os
import signal
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from eon_timer import resources
from eon_timer.app_window import AppWindow
from eon_timer.util.injector.app_context import AppContext
from eon_timer.util.injector.provider import InstanceProvider


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName('EonTimer')
    app.setOrganizationName('DasAmpharos')
    app.setOrganizationDomain('io.github.dasampharos')
    icon_filepath = resources.get_filepath('icon-512.png')
    app.setWindowIcon(QIcon(icon_filepath))

    context = AppContext(['eon_timer'], provided={QApplication: InstanceProvider(app)})
    app_window = context.get_component(AppWindow)
    app_window.show()
    return app.exec()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
    sys.exit(main())
