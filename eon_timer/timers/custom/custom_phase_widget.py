import functools
from typing import Final

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QSpinBox, QLabel, QWidget, QGroupBox, QPushButton, QHBoxLayout, QSizePolicy, \
    QDoubleSpinBox

from eon_timer.timers import Calibrator
from eon_timer.util import pyside
from eon_timer.util.const import INT_MAX, INT_MIN
from eon_timer.util.properties import bindings
from eon_timer.util.properties.property import IntProperty
from eon_timer.util.properties.property_change import PropertyChangeEvent
from eon_timer.util.pyside import EnumComboBox
from eon_timer.util.pyside.form import FormWidget
from .custom_phase import CustomPhase


class CustomPhaseWidget(QWidget):
    changed: Final[Signal] = Signal()
    removed: Final[Signal] = Signal()

    class Field(FormWidget.Field):
        UNIT = 'Unit'
        TARGET = 'Target'
        CALIBRATION = 'Calibration'
        HIT = 'Hit'

    def __init__(self,
                 index: int,
                 model: CustomPhase,
                 calibrator: Calibrator):
        super().__init__()
        self.model: Final[CustomPhase] = model
        self.calibrator: Final[Calibrator] = calibrator
        self.__index: Final[IntProperty] = IntProperty(index)

        self.__unit_field: Final[EnumComboBox] = EnumComboBox(CustomPhase.Unit)
        self.__target_field: Final[QSpinBox] = QSpinBox()
        self.__calibration_field: Final[QDoubleSpinBox] = QDoubleSpinBox()
        self.__hit_field: Final[QSpinBox] = QSpinBox()
        self.__init_components()

    def __init_components(self):
        # ----- layout -----
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        # ----- index -----
        label = QLabel()
        layout.addWidget(label, stretch=0)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        update_index = functools.partial(self.__update_index, label)
        self.__index.on_change(update_index)
        update_index()
        # ----- group -----
        group = QGroupBox()
        layout.addWidget(group, stretch=1)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pyside.set_class(group, ['themeable-panel', 'themeable-border'])
        group_layout = QHBoxLayout(group)
        # ----- form -----
        form = FormWidget()
        group_layout.addWidget(form, stretch=1)
        form.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout = form.layout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(10)
        # ----- unit -----
        bindings.bind_enum_combobox(self.__unit_field, self.model.unit)
        self.__unit_field.value.on_change(self.__on_unit_changed)
        form.add_field(self.Field.UNIT, self.__unit_field)
        self.__on_unit_changed()
        # ----- target -----
        self.__target_field.setRange(0, INT_MAX)
        bindings.bind_spinbox(self.__target_field, self.model.target)
        self.__target_field.valueChanged.connect(self.__on_value_changed)
        form.add_field(self.Field.TARGET, self.__target_field)
        # ----- calibration -----
        self.__calibration_field.setRange(INT_MIN, INT_MAX)
        bindings.bind_float_spinbox(self.__calibration_field, self.model.calibration)
        self.__calibration_field.valueChanged.connect(self.__on_value_changed)
        form.add_field(self.Field.CALIBRATION, self.__calibration_field)
        # ----- hit_field -----
        self.__hit_field.setRange(0, INT_MAX)
        bindings.bind_spinbox(self.__hit_field, self.model.hit)
        form.add_field(self.Field.HIT, self.__hit_field)
        # ----- remove_btn -----
        button = QPushButton('x')
        button.setToolTip('Remove')
        group_layout.addWidget(button, stretch=0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        button.clicked.connect(self.__on_remove_button_clicked)
        pyside.set_class(button, ['danger'])

    def calibrate(self):
        if self.hit > 0:
            if self.unit != CustomPhase.Unit.MILLISECONDS:
                calibration = self.calibrator.to_milliseconds(self.target - self.hit)
            else:
                calibration = self.target - self.hit
            self.model.calibration.add(calibration)
            self.model.hit.set(0)

    def __update_index(self,
                       label: QLabel,
                       event: PropertyChangeEvent[int] | None = None):
        index = self.index
        if event is not None:
            index = event.new_value
        label.setText(f'{index + 1}.')

    def __on_value_changed(self):
        self.changed.emit()

    def __on_unit_changed(self, event: PropertyChangeEvent[CustomPhase.Unit] | None = None):
        unit = self.unit
        if event is not None:
            unit = event.new_value

        prefix = '0x' if unit == CustomPhase.Unit.HEX else ''
        integer_base = 16 if unit == CustomPhase.Unit.HEX else 10
        # ----- target_field -----
        self.__target_field.setPrefix(prefix)
        self.__target_field.setDisplayIntegerBase(integer_base)
        # ----- hit_field -----
        self.__hit_field.setPrefix(prefix)
        self.__hit_field.setDisplayIntegerBase(integer_base)

        self.changed.emit()

    def __on_remove_button_clicked(self):
        self.removed.emit()

    def deleteLater(self):
        self.model.dispose()
        self.__index.dispose()
        super().deleteLater()

    @property
    def index(self) -> int:
        return self.__index.get()

    @index.setter
    def index(self, index: int):
        self.__index.set(index)

    @property
    def unit(self) -> CustomPhase.Unit:
        return self.model.unit.get()

    @property
    def target(self) -> int:
        return self.model.target.get()

    @property
    def calibration(self) -> float:
        return self.model.calibration.get()

    @property
    def hit(self) -> int:
        return self.model.hit.get()
