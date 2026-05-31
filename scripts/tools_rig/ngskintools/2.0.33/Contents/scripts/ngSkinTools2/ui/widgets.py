from ngSkinTools2.api import PaintMode
from ngSkinTools2.python_compatibility import Object
from PySide2 import QtWidgets, QtCore
from ngSkinTools2.signal import Signal
from ngSkinTools2.ui import qt
from ngSkinTools2.ui.layout import scale_multiplier


def curve_mapping(x, s, t):
    """
    provides a linear-to smooth curve mapping

    based on a paper https://arxiv.org/abs/2010.09714
    """
    epsilon = 0.000001

    if x < 0:
        return 0
    if x > 1:
        return 1
    if x < t:
        return (t * x) / (x + s * (t - x) + epsilon)

    return ((1 - t) * (x - 1)) / (1 - x - s * (t - x) + epsilon) + 1


class NumberSliderGroup(Object):
    """
    float spinner is the "main control" while the slider acts as complementary way to change value
    """

    def __init__(self, value_type=float, minimum=0, maximum=1, tooltip="", expo=None):
        float_mode = value_type == float

        self.__layout = layout = QtWidgets.QHBoxLayout()
        self.valueChanged = Signal("sliderGroupValueChanged")

        self.spinner = spinner = QtWidgets.QDoubleSpinBox() if float_mode else QtWidgets.QSpinBox()
        spinner.setKeyboardTracking(False)

        self.expo = expo
        self.expo_coefficient = 1.0

        spinner.setMinimumWidth(80 * scale_multiplier)
        if float_mode:
            spinner.setDecimals(3)

        value_range = maximum - minimum
        single_step = value_range / 100.0
        if not float_mode and single_step < 1:
            single_step = 1
        spinner.setSingleStep(single_step)

        spinner.setToolTip(tooltip)

        slider_resolution = 1000.0
        self.slider = slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(slider_resolution)
        slider.setToolTip(tooltip)

        layout.addWidget(spinner)
        layout.addWidget(slider)

        # formulas: https://www.desmos.com/calculator/gjwk5t3wmn

        def to_slider_value(v):
            x = float(v - minimum) / value_range

            y = x
            if self.expo == 'start':
                y = curve_mapping(x, self.expo_coefficient, 0)
            if self.expo == 'end':
                y = curve_mapping(x, self.expo_coefficient, 1)

            return y * slider_resolution

        def from_slider_value(v):
            x = v / slider_resolution
            if self.expo == 'start':
                x = curve_mapping(x, self.expo_coefficient, 1)
            if self.expo == 'end':
                x = curve_mapping(x, self.expo_coefficient, 0)

            return minimum + value_range * x

        @qt.on(spinner.valueChanged)
        def update_slider():
            with qt.signals_blocked(slider):
                slider.setValue(to_slider_value(spinner.value()))
            self.valueChanged.emit()

        @qt.on(slider.valueChanged)
        def slider_updated():
            spinner.setValue(from_slider_value(slider.value()))

        self.update_slider = update_slider

    def layout(self):
        return self.__layout

    def value(self):
        return self.spinner.value()

    def set_value(self, value):
        if self.value != value:
            self.spinner.setValue(value)

    def set_enabled(self, enabled):
        self.spinner.setEnabled(enabled)
        self.slider.setEnabled(enabled)

    def blockSignals(self, block):
        result = self.spinner.blockSignals(block)
        self.slider.blockSignals(block)
        return result

    def set_expo(self, expo, coefficient=3):
        self.expo = expo
        self.expo_coefficient = coefficient
        self.update_slider()


def set_paint_expo(number_group, paint_mode):
    """
    Sets number slider group expo according to paint mode.

    :type paint_mode: int
    :type number_group: NumberSliderGroup
    """
    intensity_expo = {
        PaintMode.add: ("start", 3),
        PaintMode.scale: ("end", 8),
        PaintMode.smooth: ("start", 3),
        PaintMode.sharpen: ("start", 3),
    }
    expo, c = intensity_expo.get(paint_mode, (None, 1))
    if number_group.expo == expo and number_group.expo_coefficient == c:
        return

    number_group.set_expo(expo=expo, coefficient=c)


def button_row(button_defs, side_menu=None):
    result = QtWidgets.QHBoxLayout()

    stretch_marker = "Marker"

    for i in (side_menu or []) + [stretch_marker] + button_defs:
        if i == stretch_marker:
            result.addStretch()
            continue
        label, handler = i
        btn = QtWidgets.QPushButton(label, minimumWidth=100)
        qt.on(btn.clicked)(handler)
        result.addWidget(btn)

    return result
