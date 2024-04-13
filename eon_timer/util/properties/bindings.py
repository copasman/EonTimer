from typing import TypeVar

from PySide6.QtWidgets import QSpinBox, QCheckBox

from eon_timer.util.enum import EnhancedEnum
from eon_timer.util.pyside import EnumComboBox
from .property import Property, PropertyChangeEvent

EnhancedEnumT = TypeVar('EnhancedEnumT', bound=EnhancedEnum)


def bind_combobox(combobox: EnumComboBox[EnhancedEnumT],
                  p_property: Property[EnhancedEnumT]) -> None:
    def on_value_changed(event: PropertyChangeEvent[EnhancedEnumT]) -> None:
        p_property.set(event.new_value)

    def on_property_changed(event: PropertyChangeEvent[EnhancedEnumT]) -> None:
        combobox.set_value(event.new_value)

    combobox.value.update(p_property)
    combobox.value.on_change(on_value_changed)
    p_property.on_change(on_property_changed)


def bind_checkbox(checkbox: QCheckBox,
                  p_property: Property[bool]) -> None:
    def on_property_changed(event: PropertyChangeEvent[bool]) -> None:
        if event.new_value != checkbox.isChecked():
            checkbox.setChecked(event.new_value)

    checkbox.setChecked(p_property.get())
    checkbox.stateChanged.connect(p_property.set)
    p_property.on_change(on_property_changed)


def bind_spinbox(spinbox: QSpinBox,
                 p_property: Property[int]) -> None:
    def on_property_changed(event: PropertyChangeEvent[int]) -> None:
        if event.new_value != spinbox.value():
            spinbox.setValue(event.new_value)

    spinbox.setValue(p_property.get())
    spinbox.valueChanged.connect(p_property.set)
    p_property.on_change(on_property_changed)
