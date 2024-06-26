from typing import Final

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QSpinBox, QDoubleSpinBox

from eon_timer.util.const import INT_MAX
from eon_timer.util.injector import component
from eon_timer.util.properties import bindings
from eon_timer.util.properties.property import Property, FloatProperty
from eon_timer.util.properties.property_change import PropertyChangeEvent
from eon_timer.util.pyside import EnumComboBox
from eon_timer.util.pyside.form import FormWidget
from .model import TimerSettingsModel, Console


@component()
class TimerSettingsWidget(FormWidget):
    class Field(FormWidget.Field):
        CONSOLE = 'Console'
        CUSTOM_FRAMERATE = 'Custom Framerate'
        REFRESH_INTERVAL = 'Refresh Interval'
        PRECISION_CALIBRATION = 'Precision Calibration'

    def __init__(self, model: TimerSettingsModel) -> None:
        super().__init__()
        self.console: Final = Property(model.console.get())
        self.custom_framerate: Final = FloatProperty(model.custom_framerate.get())
        self.precision_calibration: Final = Property(model.precision_calibration.get())
        self.refresh_interval: Final = Property(model.refresh_interval.get())
        self.model: Final[TimerSettingsModel] = model
        self.__init_components()

    def __init_components(self) -> None:
        self.setObjectName('timerSettingsWidget')
        # ----- layout -----
        self._layout.set_alignment(Qt.AlignmentFlag.AlignTop)
        self._layout.set_content_margins(10, 10, 10, 10)
        # ----- console -----
        field = EnumComboBox(Console)
        bindings.bind_enum_combobox(field, self.console)
        self.add_field(self.Field.CONSOLE, field,
                       name='timerSettingsConsole')
        # ----- custom framerate -----
        field = QDoubleSpinBox()
        field.setRange(0, INT_MAX)
        bindings.bind_float_spinbox(field, self.custom_framerate)
        self.add_field(self.Field.CUSTOM_FRAMERATE, field,
                       visible=self.console.get() == Console.CUSTOM,
                       name='timerSettingsCustomFramerate')
        self.console.on_change(self.__on_console_changed)
        # ----- refresh interval -----
        field = QSpinBox()
        field.setRange(1, INT_MAX)
        bindings.bind_spinbox(field, self.refresh_interval)
        self.add_field(self.Field.REFRESH_INTERVAL, field,
                       name='timerSettingsRefreshInterval')
        # ----- precision calibration -----
        field = QCheckBox()
        field.setTristate(False)
        bindings.bind_checkbox(field, self.precision_calibration)
        self.add_field(self.Field.PRECISION_CALIBRATION, field,
                       name='timerSettingsPrecisionCalibration')

    def __on_console_changed(self, event: PropertyChangeEvent[Console]):
        self.set_visible(self.Field.CUSTOM_FRAMERATE, event.new_value == Console.CUSTOM)

    def on_accepted(self):
        self.model.console.update(self.console)
        self.model.custom_framerate.update(self.custom_framerate)
        self.model.refresh_interval.update(self.refresh_interval)
        self.model.precision_calibration.update(self.precision_calibration)

    def on_rejected(self):
        self.__reset_properties()

    def on_reset(self):
        self.model.reset()
        self.__reset_properties()

    def __reset_properties(self):
        self.console.update(self.model.console)
        self.custom_framerate.update(self.model.custom_framerate)
        self.refresh_interval.update(self.model.refresh_interval)
        self.precision_calibration.update(self.model.precision_calibration)
